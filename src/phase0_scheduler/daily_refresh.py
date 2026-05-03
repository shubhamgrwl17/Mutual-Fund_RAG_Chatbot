import os
import sys
import logging
import json
import hashlib
from pathlib import Path

# Add project root to sys.path for absolute imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.phase1_scraping.run_ingestion import run_ingestion
from src.phase2_chunking.run_chunking import run_chunking_pipeline
from src.phase3_1_embedding.pipeline import run_embedding_pipeline
from src.phase3_2_vector_db.run_indexing import main as run_indexing

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("DailyRefresh")

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

def get_corpus_hash():
    """Generate a combined hash of all processed JSON files to detect changes."""
    if not PROCESSED_DIR.exists():
        return ""
    
    files = sorted(list(PROCESSED_DIR.glob("*.json")))
    combined_content = ""
    for f in files:
        # We only hash the functional data, ignoring metadata timestamps
        try:
            with open(f, "r", encoding="utf-8") as file:
                data = json.load(file)
                # Remove metadata to avoid false positives on every scrape
                if "_metadata" in data:
                    del data["_metadata"]
                combined_content += json.dumps(data, sort_keys=True)
        except Exception:
            continue
            
    return hashlib.md5(combined_content.encode()).hexdigest()

def main():
    logger.info("=== Starting Daily Corpus Refresh Pipeline ===")
    
    try:
        # Capture old hash
        old_hash = get_corpus_hash()
        logger.info(f"Existing corpus hash: {old_hash[:8] if old_hash else 'None'}")

        # Phase 1: Scraping & Validation
        logger.info("\n--- Phase 1: Ingestion ---")
        try:
            run_ingestion()
        except SystemExit as e:
            if e.code != 0:
                logger.error("Phase 1 failed. Aborting pipeline.")
                sys.exit(1)

        # Capture new hash
        new_hash = get_corpus_hash()
        logger.info(f"New corpus hash: {new_hash[:8]}")

        if old_hash == new_hash and old_hash != "":
            logger.info("\n>>> [DIFF DETECTION] No functional changes detected in fund data. Skipping re-indexing. <<<")
            logger.info("=== Daily Corpus Refresh Completed (No-op) ===")
            sys.exit(0)
            
        logger.info("\n>>> [DIFF DETECTION] Changes detected. Proceeding with full pipeline. <<<")

        # Phase 2: Chunking
        logger.info("\n--- Phase 2: Chunking ---")
        run_chunking_pipeline()

        # Phase 3.1: Embedding
        logger.info("\n--- Phase 3.1: Embedding ---")
        INPUT_CHUNKS = "data/chunks/corpus.jsonl"
        OUTPUT_CHUNKS = "data/embeddings/corpus_with_embeddings.jsonl"
        run_embedding_pipeline(INPUT_CHUNKS, OUTPUT_CHUNKS)

        # Phase 3.2: Vector DB Update
        logger.info("\n--- Phase 3.2: Indexing ---")
        idx_exit_code = run_indexing()
        if idx_exit_code != 0:
            logger.error("Phase 3.2 failed. Aborting pipeline.")
            sys.exit(1)

        logger.info("\n=== Daily Corpus Refresh Completed Successfully! ===")
        sys.exit(0)

    except Exception as e:
        logger.exception(f"Pipeline failed with unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
