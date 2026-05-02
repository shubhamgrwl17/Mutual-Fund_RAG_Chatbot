import json
import logging
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
        self.collection = self.client.get_or_create_collection(
            name=self.config.collection_name
        )

    def _create_client(self):
        mode = (self.config.mode or "").lower().strip()
        if mode == "remote":
            headers = {}
            if self.config.auth_token:
                headers["Authorization"] = f"Bearer {self.config.auth_token}"
            # Some Chroma versions don't accept headers; handle gracefully.
            try:
                return chromadb.HttpClient(
                    host=self.config.host,
                    port=self.config.port,
                    ssl=self.config.ssl,
                    headers=headers or None,
                )
            except TypeError:
                client = chromadb.HttpClient(
                    host=self.config.host, port=self.config.port, ssl=self.config.ssl
                )
                if headers:
                    logger.warning(
                        "Chroma HttpClient does not support headers in this version; "
                        "auth token will be ignored."
                    )
                return client

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

