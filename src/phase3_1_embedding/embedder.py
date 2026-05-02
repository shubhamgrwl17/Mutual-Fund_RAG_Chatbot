import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class ChunkEmbedder:
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        """
        Initializes the embedding model.
        Note: bge-small-en-v1.5 does not require an instruction prefix for document embedding.
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info("Model loaded successfully.")

    def embed_chunks(self, chunks: List[Dict[str, Any]], batch_size: int = 32) -> List[Dict[str, Any]]:
        """
        Generates embeddings for a list of chunks.
        Expects chunks to have a 'content' field.
        Adds 'embedding' field to each chunk.
        """
        if not chunks:
            return []

        # Extract content to embed
        texts = [chunk["content"] for chunk in chunks]
        
        logger.info(f"Generating embeddings for {len(texts)} chunks...")
        # encode returns numpy array by default, we convert to list of floats for JSON serialization
        embeddings = self.model.encode(texts, batch_size=batch_size, show_progress_bar=True)
        
        logger.info("Embeddings generated.")
        
        # Add embedding back to the chunks
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i].tolist()
            
        return chunks
