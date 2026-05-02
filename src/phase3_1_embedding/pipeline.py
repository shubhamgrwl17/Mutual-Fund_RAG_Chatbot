import json
import logging
from pathlib import Path
from .embedder import ChunkEmbedder

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def run_embedding_pipeline(input_path: str, output_path: str, batch_size: int = 32):
    """
    Reads chunks from input_path, generates embeddings, and saves them to output_path.
    """
    input_file = Path(input_path)
    output_file = Path(output_path)
    
    if not input_file.exists():
        logger.error(f"Input file not found: {input_path}")
        return

    logger.info(f"Reading chunks from {input_path}")
    chunks = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                chunks.append(json.loads(line))
                
    if not chunks:
        logger.warning("No chunks found in input file.")
        return

    # Generate embeddings
    embedder = ChunkEmbedder()
    embedded_chunks = embedder.embed_chunks(chunks, batch_size=batch_size)
    
    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Saving {len(embedded_chunks)} chunks with embeddings to {output_path}")
    with open(output_file, "w", encoding="utf-8") as f:
        for chunk in embedded_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
            
    logger.info("Embedding pipeline completed successfully.")

if __name__ == "__main__":
    # Example usage when run directly
    INPUT_CHUNKS = "data/chunks/corpus.jsonl"
    OUTPUT_CHUNKS = "data/embeddings/corpus_with_embeddings.jsonl"
    run_embedding_pipeline(INPUT_CHUNKS, OUTPUT_CHUNKS)
