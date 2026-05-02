import sys
import logging
from src.phase6_generation.generator import AnswerGenerator

# Fix for Windows terminal Unicode issues
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

def run_e2e_tests():
    print("\nInitializing End-to-End RAG System...")
    generator = AnswerGenerator()
    print("System Ready.\n")
    
    test_queries = [
        "What is the exit load for HDFC Mid-cap Opportunities Fund?",
        "Who is the fund manager for Nippon India Growth Fund?",
        "Should I invest in SBI Magnum Midcap for high returns?",
        "What are the 3-year returns for ICICI Prudential Midcap and is it better than Motilal Oswal?",
        "How to bake a chocolate cake?"
    ]
    
    print("=== END-TO-END RAG VERIFICATION ===")
    for i, query in enumerate(test_queries):
        print(f"\n[{i+1}] User: {query}")
        result = generator.generate_answer(query)
        print(f"Bot Status: {result['status']}")
        print(f"Bot Answer:\n{result['answer']}")
        print("-" * 50)

if __name__ == "__main__":
    run_e2e_tests()
