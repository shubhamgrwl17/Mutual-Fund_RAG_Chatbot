"""
Daily corpus refresh pipeline orchestration.
Triggered by GitHub Actions at 09:00 AM IST.
"""
import os
import sys
import logging
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

def main():
    logger.info("=== Starting Daily Corpus Refresh Pipeline ===")
    
    try:
        # Phase 1: Scraping & Validation
        logger.info("\n--- Phase 1: Ingestion ---")
        # run_ingestion calls sys.exit(1) on failure, but we want to catch it if possible
        # Since it calls sys.exit, we might need a wrapper or just let it exit
        try:
            run_ingestion()
        except SystemExit as e:
            if e.code != 0:
                logger.error("Phase 1 failed. Aborting pipeline.")
                sys.exit(1)

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
