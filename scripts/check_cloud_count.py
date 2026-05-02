import chromadb
import os
from dotenv import load_dotenv

def check_count():
    load_dotenv()
    
    host = os.getenv('CHROMA_HOST')
    collection_name = os.getenv('CHROMA_COLLECTION')
    
    print(f"Connecting to: {host}...")
    client = chromadb.HttpClient(host=host, ssl=True)
    
    collection = client.get_collection(collection_name)
    count = collection.count()
    
    print("-" * 30)
    print(f"SUCCESS: Found {count} chunks on Hugging Face.")
    print("-" * 30)

if __name__ == "__main__":
    check_count()
