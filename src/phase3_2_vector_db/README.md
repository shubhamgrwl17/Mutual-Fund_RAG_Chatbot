# Phase 3.2 — Vector Store Indexing

## Overview
Indexes the generated embeddings into the vector database (ChromaDB) to enable fast semantic search.

## Files
- `indexer.py`: Contains the `MutualFundIndexer` class which handles connections to ChromaDB (both local and cloud/HTTP) and manages collection creation and data upserts.
- `run_indexing.py`: Entry point for the indexing process. Loads embedded data and triggers the indexer.
- `Dockerfile`: Deployment configuration for hosting ChromaDB as a standalone server (e.g., on Hugging Face Spaces).
- `IMPLEMENTATION_PLAN.md`: Detailed architectural plan for this phase.
- `__init__.py`: Package initialization.

## Execution
```bash
# To index locally
python -m src.phase3_2_vector_db.run_indexing
```

## Deploy Chroma on Hugging Face Spaces (Remote Mode)

Use this when you want a centralized Chroma server instead of local `data/vector_db`.

### 1) Create the Space
- Create a new Hugging Face Space with **Docker** SDK.
- Make it **Private** if you want token-protected access.

### 2) Use the provided Dockerfile
- Copy `src/phase3_2_vector_db/Dockerfile` into the root of the Space repo.
- Commit and push; the Space should build and expose the server on port `8000`.

### 3) Get Space URL + token
- Space URL format: `https://<username>-<space-name>.hf.space`
- If private, generate a Hugging Face access token and keep it ready.

### 4) Configure your local `.env`
Create `.env` in this project from `.env.example` and set:

```env
CHROMA_MODE=remote
CHROMA_COLLECTION=mutual_fund_faq
CHROMA_HOST=<username>-<space-name>.hf.space
CHROMA_PORT=443
CHROMA_SSL=true
CHROMA_AUTH_TOKEN=<your_hf_token_if_private_else_blank>
EMBEDDED_CHUNKS_PATH=data/embeddings/corpus_with_embeddings.jsonl
CHROMA_BATCH_SIZE=100
```

Notes:
- `CHROMA_HOST` should be hostname only (no `https://`).
- For public spaces, leave `CHROMA_AUTH_TOKEN` empty.

### 5) Run remote indexing
```bash
python -m src.phase3_2_vector_db.run_indexing
```

You should see logs showing chunks upserted into the remote collection.

## Quick env reference
- `CHROMA_MODE`: `local` or `remote`
- `CHROMA_COLLECTION`: target collection name
- `CHROMA_PERSIST_DIR`: local DB path (local mode only)
- `CHROMA_HOST`/`CHROMA_PORT`/`CHROMA_SSL`: remote connection settings
- `CHROMA_AUTH_TOKEN`: optional bearer token for private endpoints
- `EMBEDDED_CHUNKS_PATH`: Phase 3.1 output file
- `CHROMA_BATCH_SIZE`: upsert batch size
