import sys
import uuid
import logging
from src.phase6_generation.generator import AnswerGenerator

# Fix for Windows terminal Unicode issues
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.getLogger("httpx").setLevel(logging.WARNING)

def test_session_memory():
    generator = AnswerGenerator()
    thread_id = f"test-thread-{uuid.uuid4().hex[:6]}"
    
    print(f"\n=== SESSION MEMORY TEST (Thread: {thread_id}) ===")
    
    # Turn 1: Establish Context
    q1 = "Tell me about the Nippon India Growth Fund."
    print(f"\n[Turn 1] User: {q1}")
    res1 = generator.generate_answer(q1, thread_id=thread_id)
    print(f"Bot: {res1['answer'][:100]}...")
    
    # Turn 2: Follow-up with Pronoun
    q2 = "What is its expense ratio?"
    print(f"\n[Turn 2] User: {q2}")
    res2 = generator.generate_answer(q2, thread_id=thread_id)
    
    print(f"Rewritten Query: {res2['metadata'].get('rewritten_query')}")
    print(f"Bot Status: {res2['status']}")
    print(f"Bot Answer: {res2['answer']}")
    
    # Turn 3: Change Subject
    q3 = "What about SBI Midcap?"
    print(f"\n[Turn 3] User: {q3}")
    res3 = generator.generate_answer(q3, thread_id=thread_id)
    print(f"Bot Answer: {res3['answer'][:100]}...")

if __name__ == "__main__":
    test_session_memory()
