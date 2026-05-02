"""
Pipeline script to run the Phase 2 chunking process.
Reads from data/processed/*.json and outputs data/chunks/corpus.jsonl.
"""

import json
import logging
import sys
from pathlib import Path

from src.phase2_chunking.chunker import process_scheme_to_chunks

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks"

def run_chunking_pipeline():
    logger.info("Starting Phase 2: Data Processing & Section-Based Chunking")
    
    # Ensure chunks dir exists
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    
    output_file = CHUNKS_DIR / "corpus.jsonl"
    
    total_files_processed = 0
    total_chunks_generated = 0
    
    # Write chunks sequentially as JSONL
    with open(output_file, 'w', encoding='utf-8') as f_out:
        for json_path in PROCESSED_DIR.glob("*.json"):
            logger.info(f"Processing {json_path.name}...")
            
            try:
                with open(json_path, 'r', encoding='utf-8') as f_in:
                    scheme_data = json.load(f_in)
                    
                chunks = process_scheme_to_chunks(scheme_data)
                
                for chunk in chunks:
                    # json.dumps without newlines ensures it's one line (JSONL format)
                    f_out.write(json.dumps(chunk, ensure_ascii=False) + "\n")
                
                total_files_processed += 1
                total_chunks_generated += len(chunks)
                logger.info(f"  -> Generated {len(chunks)} chunks.")
                
            except Exception as e:
                logger.error(f"Failed to process {json_path.name}: {e}")
                sys.exit(1)

    logger.info("\n=== Chunking Summary ===")
    logger.info(f"Files Processed: {total_files_processed}")
    logger.info(f"Total Chunks Generated: {total_chunks_generated}")
    logger.info(f"Output saved to: {output_file}")
    logger.info("Phase 2 pipeline completed successfully!")

if __name__ == "__main__":
    run_chunking_pipeline()
