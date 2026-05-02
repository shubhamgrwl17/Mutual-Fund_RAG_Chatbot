# Implementation Plan - Phase 4: Retrieval Pipeline

## Goal
Implement a high-precision hybrid retrieval pipeline combining semantic (dense) search, keyword (sparse) search, and cross-encoder re-ranking. Aligns with `docs/rag_architecture.md`.

## 1. Core Configuration
The following constants will be used to ensure deterministic retrieval:
- `TOP_K_INITIAL = 20` (Initial candidates from dense/sparse)
- `TOP_N_FINAL = 10` (Final context sent to LLM)
- `RRF_K = 60` (Constant for Reciprocal Rank Fusion)
- `DENSE_WEIGHT = 0.6`
- `SPARSE_WEIGHT = 0.4`
- `SIMILARITY_THRESHOLD = -2.0` (Min re-rank score to avoid hallucination)

## 2. Proposed Changes

### [Phase 4: Retrieval Logic]

#### [NEW] src/phase4_retrieval/retriever.py
Create the `HybridRetriever` class with:

- **Initialization**:
    - **Dense**: Connects to ChromaDB (`HttpClient` or `PersistentClient`).
    - **Sparse**: Loads `data/embeddings/corpus_with_embeddings.jsonl` at startup. Fails fast if file is missing. Fits `BM25Okapi` on the `content` field.
    - **Re-Ranker**: Loads `cross-encoder/ms-marco-MiniLM-L-6-v2`.

- **Metadata Filtering**:
    - Support pre-filtering on `scheme_name`, `scheme_id`, and `section`.
    - Filters are applied during the initial dense/sparse retrieval phase.

- **Pre-Retrieval Guardrails (Defensive Engineering)**:
    - **Fund Name Resolver / Aliases**: Use a mapping to resolve typos/aliases (e.g., "Nipon" -> `nippon-india-growth`) before searching to improve accuracy.
    - **Vague Query Handler**: If the query is < 5 words and contains no known fund name (e.g., "What are the returns?"), return a `NEEDS_CLARIFICATION` signal to prompt the user.
    - **Out-of-Corpus Detector**: If the query explicitly asks about a fund not in our `KNOWN_FUND_NAMES` (e.g., "Axis Bluechip"), return an `OUT_OF_CORPUS` signal immediately, skipping database search.

- **Hybrid Search (RRF)**:
    - Formula: $Score_{RRF} = \frac{DENSE\_WEIGHT}{RRF\_K + rank_{dense}} + \frac{SPARSE\_WEIGHT}{RRF\_K + rank_{sparse}}$
    - Returns Top-30 fused candidates for re-ranking.

- **Re-Ranking & Thresholding**:
    - Scores query against candidates using CrossEncoder.
    - **Fallback**: If `max(scores) < SIMILARITY_THRESHOLD`, returns an empty list (triggering a "I don't have this information" fallback in the bot).

- **`retrieve(query, filters=None)`**:
    - Main orchestration method returning a list of dictionaries containing:
        - `chunk_id`, `content`, `section`, `source_url`, `scores` (dense, sparse, rrf, rerank).

#### [NEW] src/phase4_retrieval/run_retrieval.py
- CLI script to test queries and inspect scores for debugging.

## 3. Verification Plan

### Automated Test Queries
Run the retriever against these specific scenarios:
1. **Factual**: "What is the exit load for HDFC Midcap?" (Expect: HDFC exit load chunk).
2. **Typo Stress**: "Nipon midcap fund managers" (Expect: Nippon India managers chunk).
3. **Vague**: "What is the risk category?" (Expect: High-score chunks for various funds).
4. **Out-of-Corpus**: "How many stocks are in Apple Inc?" (Expect: 0 results / Fallback triggered).
5. **Metadata Route**: Query specifically for "NAV" (Expect: chunks where `section == "nav_and_aum"`).

### Success Criteria
- Correct chunk must be in **Top-1** after re-ranking for factual queries.
- System must return empty context for queries unrelated to the mutual fund corpus.
