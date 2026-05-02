# Implementation Plan - Phase 3.2: Vector DB Indexing (ChromaDB)

This phase moves the embedded chunks from a JSONL file into a searchable vector database (ChromaDB). It is designed to be "Cloud-Ready," allowing for automated updates via GitHub Actions and serving multiple users via a centralized server (e.g., Hugging Face Spaces).

## User Review Required

> [!IMPORTANT]
> **Hugging Face Setup**: This plan assumes you will create a free Hugging Face Space. I will provide the `Dockerfile` and setup instructions in a separate document once this code is ready.
> 
> **Authentication**: For the cloud version, we will use Token-based authentication to prevent unauthorized users from overwriting your mutual fund data.

## Proposed Changes

### [Component: Vector Indexing]

#### [NEW] indexer.py
- Create a `MutualFundIndexer` class.
- Support `HttpClient` (Remote) and `PersistentClient` (Local).
- Implement `upsert_batches`:
    - Reads chunks in batches (e.g., 100 at a time).
    - Uses `collection.upsert()` to handle updates to existing fund data without creating duplicates.
- Map the schema:
    - **ID**: `chunk_id`
    - **Vector**: `embedding`
    - **Metadata**: All fields except content/embedding (e.g., `scheme_name`, `section`, `source_url`).
    - **Document**: The raw string `content`.

#### [NEW] run_indexing.py
- The main entry point for this phase.
- Uses `python-dotenv` to load configurations (Host, Port, Auth Token).
- Reports statistics: Total chunks indexed, batches processed, and any failures.

#### [NEW] Dockerfile
- A simple Dockerfile to be copied into Hugging Face Spaces to run the ChromaDB server.

---

## Verification Plan

### Automated Tests
- Run `python -m src.phase3_2_vector_db.run_indexing` in **Local Mode**.
- Verify that a `data/vector_db` folder is created.
- Run a small search script to ensure `collection.query()` returns relevant fund chunks.

### Manual Verification
1.  Change one value in a fund's raw JSON (e.g., NAV).
2.  Re-run the full pipeline (Phases 1 -> 3.2).
3.  Verify that ChromaDB reflects the *new* value for that specific ID instead of creating a second entry.
