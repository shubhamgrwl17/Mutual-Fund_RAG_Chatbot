import sys
import logging
from src.phase6_generation.generator import AnswerGenerator

# Fix for Windows terminal Unicode issues
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

def debug():
    g = AnswerGenerator()
    query = "What has been the trend of SBI Mid Cap NAV over the years? What is its exit load? How does the exit load look like when we compare it to other Mid Cap mutual funds?"
    
    # 1. Get raw context
    retrieval_result = g.retriever.retrieve(query)
    context_chunks = retrieval_result["context"]
    print("\n--- RAW CONTEXT ---")
    for c in context_chunks:
        print(f"[{c['section']}] {c['content']}")
        
    # 2. Get LLM response
    res = g.generate_answer(query)
    print("\n--- SYSTEM RESPONSE ---")
    print(f"STATUS: {res['status']}")
    print(f"ANSWER: {res['answer']}")
    if 'metadata' in res:
        print(f"ISSUES: {res['metadata']['validation_issues']}")

if __name__ == "__main__":
    debug()
