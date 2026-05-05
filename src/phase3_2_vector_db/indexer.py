import json
import logging
import time
import requests
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import chromadb

logger = logging.getLogger(__name__)


def _jsonl_iter(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _sanitize_metadata_value(value: Any) -> Optional[Any]:
    """
    Chroma metadata values must be primitive types (str/int/float/bool).
    We drop complex types, and coerce lists/dicts to JSON strings.
    """
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, dict)):
        try:
            return json.dumps(value, ensure_ascii=False)
        except Exception:
            return str(value)
    return str(value)


def _build_metadata(chunk: dict) -> Dict[str, Any]:
    """
    Metadata = all top-level fields except 'content'/'embedding',
    plus selected nested _metadata fields (flattened).
    """
    md: Dict[str, Any] = {}

    for k, v in chunk.items():
        if k in ("content", "embedding"):
            continue
        if k == "_metadata" and isinstance(v, dict):
            continue
        md[k] = _sanitize_metadata_value(v)

    nested = chunk.get("_metadata", {}) if isinstance(chunk.get("_metadata"), dict) else {}
    for nk, nv in nested.items():
        md[f"meta_{nk}"] = _sanitize_metadata_value(nv)

    # Remove None values (Chroma can be picky depending on version)
    return {k: v for k, v in md.items() if v is not None}


@dataclass(frozen=True)
class IndexerConfig:
    mode: str  # "local" or "remote"
    collection_name: str = "mutual_fund_faq"
    persist_dir: str = "data/vector_db"
    host: str = "localhost"
    port: int = 8000
    ssl: bool = False
    auth_token: Optional[str] = None


class MutualFundIndexer:
    def __init__(self, config: IndexerConfig):
        self.config = config
        self.client = self._create_client()
        self.collection = self._get_collection()

    def _get_collection(self):
        """Helper to get collection with a small retry since the client might still be stabilizing."""
        for attempt in range(1, 4):
            try:
                return self.client.get_or_create_collection(
                    name=self.config.collection_name
                )
            except Exception as e:
                if attempt == 3:
                    raise
                logger.warning(f"Attempt {attempt} to get collection failed: {e}. Retrying...")
                time.sleep(5)

    def _wake_up_remote(self):
        """Send a heartbeat request to wake up a potentially sleeping remote host (like HF Spaces)."""
        if self.config.mode != "remote":
            return

        scheme = "https" if self.config.ssl else "http"
        url = f"{scheme}://{self.config.host}:{self.config.port}/api/v1/heartbeat"
        
        logger.info(f"Sending wake-up heartbeat to {url}...")
        try:
            # We use a long timeout for the wake-up call itself
            response = requests.get(url, timeout=60)
            if response.status_code == 200:
                logger.info("Host is awake and responding.")
                return True
            else:
                logger.warning(f"Host responded with status {response.status_code}")
        except Exception as e:
            logger.warning(f"Wake-up ping failed: {e}")
        
        return False

    def _create_client(self):
        mode = (self.config.mode or "").lower().strip()
        if mode == "remote":
            # 1. Try to wake up the space first
            self._wake_up_remote()

            headers = {}
            if self.config.auth_token:
                headers["Authorization"] = f"Bearer {self.config.auth_token}"

            # 2. Initialize client with retries
            for attempt in range(1, 4):
                try:
                    logger.info(f"Initializing Chroma HttpClient (Attempt {attempt}/3)...")
                    return chromadb.HttpClient(
                        host=self.config.host,
                        port=self.config.port,
                        ssl=self.config.ssl,
                        headers=headers or None,
                    )
                except Exception as e:
                    if attempt == 3:
                        logger.error(f"Failed to initialize Chroma client after {attempt} attempts.")
                        raise
                    logger.warning(f"Attempt {attempt} failed: {e}. Retrying in 10s...")
                    time.sleep(10)
                    # Try waking up again if it failed
                    self._wake_up_remote()

        if mode == "local":
            persist_path = Path(self.config.persist_dir)
            persist_path.mkdir(parents=True, exist_ok=True)
            return chromadb.PersistentClient(path=str(persist_path))

        raise ValueError("IndexerConfig.mode must be 'local' or 'remote'")

    def upsert_batches(
        self,
        embedded_jsonl_path: str,
        batch_size: int = 100,
    ) -> Tuple[int, int]:
        """
        Upsert vectors into Chroma in batches.
        Returns: (total_upserted, batches_processed)
        """
        path = Path(embedded_jsonl_path)
        if not path.exists():
            raise FileNotFoundError(f"Embedded JSONL not found: {embedded_jsonl_path}")

        batch_ids: List[str] = []
        batch_embeddings: List[List[float]] = []
        batch_docs: List[str] = []
        batch_metas: List[Dict[str, Any]] = []

        total = 0
        batches = 0

        def flush():
            nonlocal total, batches
            if not batch_ids:
                return
            self.collection.upsert(
                ids=batch_ids,
                embeddings=batch_embeddings,
                documents=batch_docs,
                metadatas=batch_metas,
            )
            total += len(batch_ids)
            batches += 1
            batch_ids.clear()
            batch_embeddings.clear()
            batch_docs.clear()
            batch_metas.clear()

        for chunk in _jsonl_iter(path):
            chunk_id = chunk.get("chunk_id")
            embedding = chunk.get("embedding")
            content = chunk.get("content")

            if not chunk_id or not isinstance(chunk_id, str):
                logger.warning("Skipping chunk without valid chunk_id")
                continue
            if not isinstance(content, str) or not content.strip():
                logger.warning("Skipping chunk %s with empty content", chunk_id)
                continue
            if not isinstance(embedding, list) or not embedding:
                logger.warning("Skipping chunk %s with missing embedding", chunk_id)
                continue

            batch_ids.append(chunk_id)
            batch_embeddings.append(embedding)
            batch_docs.append(content)
            batch_metas.append(_build_metadata(chunk))

            if len(batch_ids) >= batch_size:
                flush()

        flush()
        return total, batches

