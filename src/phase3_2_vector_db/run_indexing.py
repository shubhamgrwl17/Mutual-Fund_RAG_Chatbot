import logging
import os
import sys

from dotenv import load_dotenv

from src.phase3_2_vector_db.indexer import IndexerConfig, MutualFundIndexer


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def _get_env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"Env var {name} must be an int, got: {raw!r}")


def main() -> int:
    load_dotenv()

    embedded_path = os.getenv(
        "EMBEDDED_CHUNKS_PATH", "data/embeddings/corpus_with_embeddings.jsonl"
    )
    mode = os.getenv("CHROMA_MODE", "local")
    collection_name = os.getenv("CHROMA_COLLECTION", "mutual_fund_faq")
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "data/vector_db")
    host = os.getenv("CHROMA_HOST", "localhost")
    port = _get_env_int("CHROMA_PORT", 8000)
    ssl = os.getenv("CHROMA_SSL", "false").lower().strip() in ("1", "true", "yes")
    auth_token = os.getenv("CHROMA_AUTH_TOKEN")
    batch_size = _get_env_int("CHROMA_BATCH_SIZE", 100)

    cfg = IndexerConfig(
        mode=mode,
        collection_name=collection_name,
        persist_dir=persist_dir,
        host=host,
        port=port,
        ssl=ssl,
        auth_token=auth_token,
    )

    logger.info(
        "Phase 3.2 indexing starting (mode=%s, collection=%s, embedded=%s)",
        cfg.mode,
        cfg.collection_name,
        embedded_path,
    )

    try:
        indexer = MutualFundIndexer(cfg)
        total, batches = indexer.upsert_batches(embedded_path, batch_size=batch_size)
        logger.info("Indexing complete: %s chunks upserted in %s batches", total, batches)

        # Smoke query for local confidence
        try:
            result = indexer.collection.query(
                query_texts=["expense ratio"],
                n_results=3,
            )
            got = len(result.get("ids", [[]])[0]) if isinstance(result, dict) else 0
            logger.info("Smoke query returned %s result(s)", got)
        except Exception as e:
            logger.warning("Smoke query failed (non-fatal): %s", e)

        return 0
    except Exception as e:
        logger.exception("Indexing failed: %s", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

