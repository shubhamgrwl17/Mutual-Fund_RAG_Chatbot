# Phase 3.1 — Embedding Generation

## Overview
Generates vector embeddings for the mutual fund chunks using the `BAAI/bge-small-en-v1.5` model.

## Files
- `embedder.py`: Core logic for loading the embedding model (Hugging Face `sentence-transformers`) and computing vector representations for text.
- `pipeline.py`: Orchestrator that reads the `corpus.jsonl` from Phase 2, passes the text to the embedder, and saves the final `corpus_with_embeddings.jsonl`.
- `__init__.py`: Package initialization.

## Execution
```bash
python -m src.phase3_1_embedding.pipeline
```

## Responsibilities
- Generates embeddings using the local model (`bge-small-en-v1.5`).
- Implements differential updates (only re-embeds chunks that changed based on hash comparisons).
- Outputs embeddings for the next phase.
