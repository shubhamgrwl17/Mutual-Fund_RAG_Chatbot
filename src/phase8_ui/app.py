try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

import os
import sys
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.phase6_generation.generator import AnswerGenerator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("API")

app = FastAPI(title="Mutual Fund RAG API")

# Enable CORS for Next.js development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class ChatRequest(BaseModel):
    query: str
    thread_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    id: str
    role: str
    content: str
    status: str
    metadata: dict

# --- Initialize Generator ---
generator = None

def get_generator():
    global generator
    if generator is None:
        try:
            logger.info("Initializing AnswerGenerator...")
            generator = AnswerGenerator()
        except Exception as e:
            logger.error(f"Failed to initialize AnswerGenerator: {e}")
            raise e
    return generator

@app.get("/api/health")
async def health_check():
    gen_status = "uninitialized"
    if generator:
        gen_status = "ready"
    return {
        "status": "healthy", 
        "generator_status": gen_status,
        "service": "mutual-fund-rag-api"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Processing query: {request.query}")
        gen = get_generator()
        # AnswerGenerator.generate_answer is a synchronous method
        result = gen.generate_answer(request.query)
        
        return ChatResponse(
            id=os.urandom(8).hex(),
            role="bot",
            content=result["answer"],
            status=result["status"],
            metadata={
                "intent": result.get("metadata", {}).get("intent", "N/A"),
                "chunks_used": result.get("metadata", {}).get("chunks_used", 0)
            }
        )
    except Exception as e:
        logger.exception("Error in chat endpoint")
        raise HTTPException(status_code=500, detail=str(e))

# --- Static Files (Frontend) ---
STATIC_DIR = Path(__file__).parent / "static"

# Mount static files
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
else:
    logger.warning(f"Static directory not found at {STATIC_DIR}. Frontend will not be served.")

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Fallback for SPA routing: serve index.html for unknown routes."""
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"detail": "Not Found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
