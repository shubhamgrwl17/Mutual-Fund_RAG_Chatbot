# Phase 2 — Data Processing & Section-Based Chunking

## Overview
Transforms processed JSON scheme data into highly semantic, section-based text chunks. 

## Responsibilities
- Maps specific JSON fields into readable string templates.
- Segments data into logical sections (e.g., Returns, Exit Load, Holdings) to prevent overlapping context issues during retrieval.
- Handles missing or `null` values gracefully.
- Generates JSONL output for the embedding layer.

## Key Files

| File | Purpose |
|------|---------|
| `aliases.py` | Maps common user queries/acronyms to strict scheme IDs. |
| `formatters.py` | Contains 9 null-safe text formatters (one for each section) to prevent hallucination. |
| `chunker.py` | Core engine that slices the Phase 1 processed JSON into semantic chunk objects. |
| `run_chunking.py` | Orchestration script that processes all JSONs and writes the final `corpus.jsonl`. |
| `IMPLEMENTATION_PLAN.md` | The detailed execution plan used to build this phase. |

## Usage

```bash
# Run the chunking pipeline
python -m src.phase2_processing.run_chunking
```
