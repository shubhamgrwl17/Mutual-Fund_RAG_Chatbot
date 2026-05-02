import sys
import json
import logging
from src.phase4_retrieval.retriever import HybridRetriever

# Fix for Windows terminal Unicode issues (e.g. Rupee symbol)
if sys.platform == "win32":
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')

# Setup basic logging to suppress noisy external libs
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

def print_result(result: dict):
    print(f"\n[{result['status']}] {result['message']}")
    if result.get("context"):
        print("\n--- TOP CONTEXT CHUNKS ---")
        for i, chunk in enumerate(result["context"]):
            print(f"\nRank {i+1} | Score: {chunk['scores']['rerank_score']}")
            print(f"Source: {chunk['source_url']}")
            print(f"Section: {chunk['section']}")
            print(f"Content: {chunk['content'][:150]}...")
            print(f"Intermediate Scores: RRF={chunk['scores']['rrf_score']}, Dense Rank={chunk['scores']['dense_rank']}, Sparse Rank={chunk['scores']['sparse_rank']}")
    print("-" * 50)

def main():
    print("Initializing Hybrid Retriever Pipeline (Loading models...)")
    retriever = HybridRetriever()
    print("Ready.\n")
    
    test_queries = [
        ("Factual", "What is the exit load for HDFC Midcap?"),
        ("Typo Stress", "Who manages the Nipon midcap fund?"),
        ("Vague", "What is the risk category?"),
        ("Out-of-Corpus", "How many stocks are in Apple Inc?"),
        ("Section Targeting", "What are the scheme returns for ICICI Prudential?")
    ]
    
    print("\n=== AUTOMATED TEST SUITE ===")
    for test_type, query in test_queries:
        print(f"\n>> Test: {test_type}")
        print(f">> Query: '{query}'")
        result = retriever.retrieve(query)
        print_result(result)
        
    print("\n=== TESTS COMPLETE ===")

if __name__ == "__main__":
    main()
