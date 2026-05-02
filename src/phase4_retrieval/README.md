# Phase 4: Retrieval Pipeline

This phase implements a high-precision hybrid retrieval system that combines semantic understanding with exact keyword matching.

## File Descriptions

| File | Description |
| :--- | :--- |
| `retriever.py` | **Core Engine**: Implements the `HybridRetriever` class. Orchestrates Dense Search (ChromaDB), Sparse Search (BM25), Reciprocal Rank Fusion (RRF), and Cross-Encoder Re-ranking. |
| `aliases.py` | **Defensive Guardrails**: Contains the fund name resolver (typo correction), out-of-corpus detection, and vague query handling logic. |
| `run_retrieval.py` | **Test CLI**: A script to verify retrieval accuracy across factual, typo-laden, and out-of-corpus queries. |
| `IMPLEMENTATION_PLAN.md` | **Design Doc**: The detailed technical plan and deterministic constants used for this phase. |

## Key Features
- **Hybrid Search**: Combines ChromaDB (Semantic) and BM25 (Keywords).
- **Re-Ranking**: Uses `ms-marco-MiniLM-L-6-v2` to ensure the most relevant context is prioritized.
- **Fail-Safe**: Implements a similarity threshold (0.65) to prevent hallucinations.
