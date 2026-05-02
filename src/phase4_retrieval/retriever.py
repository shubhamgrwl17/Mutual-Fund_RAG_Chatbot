import os
import json
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from chromadb.utils import embedding_functions

from src.phase4_retrieval.aliases import resolve_fund_name, detect_out_of_corpus, needs_clarification

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger(__name__)

class HybridRetriever:
    """
    Hybrid Retriever combining Dense (ChromaDB) and Sparse (BM25) search,
    with Cross-Encoder re-ranking and defensive guardrails.
    """
    
    # Core Configuration
    TOP_K_INITIAL = 20
    TOP_N_FINAL = 10
    RRF_K = 60
    DENSE_WEIGHT = 0.6
    SPARSE_WEIGHT = 0.4
    SIMILARITY_THRESHOLD = -2.0
    
    def __init__(self):
        load_dotenv()
        
        # 1. Initialize Dense Retrieval (ChromaDB)
        mode = os.getenv("CHROMA_MODE", "local")
        collection_name = os.getenv("CHROMA_COLLECTION", "mutual_fund_faq")
        
        logger.info(f"Initializing HybridRetriever in {mode} mode...")
        if mode == "remote":
            host = os.getenv("CHROMA_HOST", "localhost")
            port = os.getenv("CHROMA_PORT", "8000")
            ssl = os.getenv("CHROMA_SSL", "false").lower() == "true"
            self.client = chromadb.HttpClient(host=host, port=port, ssl=ssl)
        else:
            persist_dir = os.getenv("CHROMA_PERSIST_DIR", "data/vector_db")
            self.client = chromadb.PersistentClient(path=persist_dir)
            
        # Initialize embedding function manually
        logger.info("Loading embedding model (BAAI/bge-small-en-v1.5)...")
        from sentence_transformers import SentenceTransformer
        self.embedding_model = SentenceTransformer("BAAI/bge-small-en-v1.5")
        
        self.collection = self.client.get_collection(name=collection_name)
        
        # 2. Initialize Sparse Retrieval (BM25)
        self.corpus_data = self._load_corpus()
        if not self.corpus_data:
            raise FileNotFoundError("Could not load corpus for BM25. Please run Phase 3.1 first.")
            
        # Tokenize corpus for BM25
        tokenized_corpus = [doc['content'].lower().split() for doc in self.corpus_data]
        self.bm25 = BM25Okapi(tokenized_corpus)
        logger.info(f"Loaded {len(self.corpus_data)} chunks into BM25 index.")
        
        # 3. Initialize Re-ranker
        logger.info("Loading CrossEncoder (ms-marco-MiniLM-L-6-v2)...")
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        logger.info("HybridRetriever initialization complete.")

    def _load_corpus(self) -> List[Dict[str, Any]]:
        """Loads the JSONL corpus from disk."""
        corpus_path = os.getenv("EMBEDDED_CHUNKS_PATH", "data/embeddings/corpus_with_embeddings.jsonl")
        corpus = []
        if not os.path.exists(corpus_path):
            return corpus
            
        with open(corpus_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    corpus.append(json.loads(line))
        return corpus

    def dense_search(self, query: str, where_filter: Optional[Dict] = None) -> List[Dict]:
        """Performs semantic search using ChromaDB."""
        # Embed query manually
        query_embedding = self.embedding_model.encode(query).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=self.TOP_K_INITIAL,
            where=where_filter
        )
        
        dense_results = []
        if not results['ids'] or not results['ids'][0]:
            return dense_results
            
        for i in range(len(results['ids'][0])):
            dense_results.append({
                "chunk_id": results['ids'][0][i],
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "dense_distance": results['distances'][0][i]  # Lower is better (cosine distance)
            })
        return dense_results

    def sparse_search(self, query: str, filter_scheme_id: Optional[str] = None) -> List[Dict]:
        """Performs keyword search using BM25."""
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        # Pair scores with chunk_ids and filter if necessary
        scored_chunks = []
        for i, score in enumerate(scores):
            chunk = self.corpus_data[i]
            if filter_scheme_id and chunk['scheme_id'] != filter_scheme_id:
                continue
            
            # Reconstruct metadata dict
            metadata = {
                "scheme_id": chunk['scheme_id'],
                "scheme_name": chunk['scheme_name'],
                "section": chunk['section'],
                **chunk['_metadata']
            }
            
            scored_chunks.append({
                "chunk_id": chunk['chunk_id'],
                "content": chunk['content'],
                "metadata": metadata,
                "sparse_score": score # Higher is better
            })
            
        # Sort and take top K
        scored_chunks.sort(key=lambda x: x['sparse_score'], reverse=True)
        return scored_chunks[:self.TOP_K_INITIAL]

    def _reciprocal_rank_fusion(self, dense_res: List[Dict], sparse_res: List[Dict]) -> List[Dict]:
        """Merges Dense and Sparse results using RRF."""
        chunk_map = {}
        
        # Process Dense
        for rank, item in enumerate(dense_res):
            chunk_id = item['chunk_id']
            if chunk_id not in chunk_map:
                chunk_map[chunk_id] = item.copy()
                chunk_map[chunk_id]['rrf_score'] = 0.0
                
            chunk_map[chunk_id]['dense_rank'] = rank
            chunk_map[chunk_id]['rrf_score'] += self.DENSE_WEIGHT / (self.RRF_K + rank)
            
        # Process Sparse
        for rank, item in enumerate(sparse_res):
            chunk_id = item['chunk_id']
            if chunk_id not in chunk_map:
                chunk_map[chunk_id] = item.copy()
                chunk_map[chunk_id]['rrf_score'] = 0.0
                chunk_map[chunk_id]['dense_rank'] = -1
                
            chunk_map[chunk_id]['sparse_rank'] = rank
            chunk_map[chunk_id]['rrf_score'] += self.SPARSE_WEIGHT / (self.RRF_K + rank)

        # Sort by RRF score
        fused = list(chunk_map.values())
        fused.sort(key=lambda x: x['rrf_score'], reverse=True)
        return fused

    def retrieve(self, query: str) -> Dict[str, Any]:
        """
        Main orchestrator: Pre-flight checks -> Dense + Sparse -> RRF -> Rerank -> Final output.
        """
        # 1. Pre-Retrieval Guardrails
        if detect_out_of_corpus(query):
            logger.warning("Guardrail Triggered: OUT_OF_CORPUS")
            return {
                "status": "OUT_OF_CORPUS",
                "message": "I only have information about specific mid-cap funds (HDFC, Nippon, Motilal, Mirae, ICICI, SBI). Please ask about these.",
                "context": []
            }
            
        if needs_clarification(query):
            logger.warning("Guardrail Triggered: NEEDS_CLARIFICATION")
            return {
                "status": "NEEDS_CLARIFICATION",
                "message": "Could you specify which fund you're asking about?",
                "context": []
            }

        # Resolve scheme alias for metadata filtering
        target_scheme_id = resolve_fund_name(query)
        where_filter = {"scheme_id": target_scheme_id} if target_scheme_id else None

        # 2. Hybrid Retrieval
        logger.info(f"Searching Dense + Sparse (Filter: {where_filter})...")
        dense_results = self.dense_search(query, where_filter)
        sparse_results = self.sparse_search(query, target_scheme_id)

        # 3. Reciprocal Rank Fusion
        fused_candidates = self._reciprocal_rank_fusion(dense_results, sparse_results)
        
        if not fused_candidates:
            return {"status": "SUCCESS", "message": "No relevant chunks found.", "context": []}

        # 4. Re-Ranking
        # Create pairs: (query, document)
        pairs = [[query, doc['content']] for doc in fused_candidates]
        logger.info(f"Re-ranking {len(pairs)} candidates...")
        rerank_scores = self.reranker.predict(pairs)
        
        for i, score in enumerate(rerank_scores):
            fused_candidates[i]['rerank_score'] = float(score)
            
        # Sort by rerank score
        fused_candidates.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        # 5. Thresholding
        top_score = fused_candidates[0]['rerank_score']
        if top_score < self.SIMILARITY_THRESHOLD:
            logger.warning(f"Guardrail Triggered: LOW_CONFIDENCE (Max score {top_score:.2f} < {self.SIMILARITY_THRESHOLD})")
            return {
                "status": "LOW_CONFIDENCE",
                "message": "I don't have this information in my sources.",
                "context": []
            }

        # Top N Selection
        final_context = fused_candidates[:self.TOP_N_FINAL]
        
        # Cleanup response
        cleaned_context = []
        for c in final_context:
            cleaned_context.append({
                "chunk_id": c["chunk_id"],
                "content": c["content"],
                "section": c["metadata"].get("section", "unknown"),
                "source_url": c["metadata"].get("source_url", ""),
                "scores": {
                    "dense_rank": c.get("dense_rank", -1),
                    "sparse_rank": c.get("sparse_rank", -1),
                    "rrf_score": round(c.get("rrf_score", 0), 4),
                    "rerank_score": round(c.get("rerank_score", 0), 4)
                }
            })

        return {
            "status": "SUCCESS",
            "message": f"Retrieved {len(cleaned_context)} chunks successfully.",
            "context": cleaned_context
        }
