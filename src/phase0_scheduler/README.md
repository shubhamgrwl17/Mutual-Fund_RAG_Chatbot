# Phase 0: Automation & Scheduled Refresh

This module handles the orchestration and automation of the Mutual Fund RAG pipeline. It ensures that the assistant's knowledge base is kept up-to-date with the latest market data from Groww without manual intervention.

## Purpose
The primary goal of this phase is to establish a "Data Heartbeat" for the system. It automates the multi-step process of scraping, chunking, embedding, and indexing new data, while enforcing strict quality gates to prevent corrupted information from reaching production.

## File Roles

### 1. `daily_refresh.py`
The **Main Orchestrator**. This script chains together all phases of the RAG pipeline into a single execution flow:
- Triggers Phase 1 (Scraping) to fetch new data.
- Triggers Phase 2 (Chunking) to process the raw HTML/JSON.
- Triggers Phase 3.1 (Embedding) to generate vectors.
- Triggers Phase 3.2 (Indexing) to update the ChromaDB vector store.
- Handles error propagation and ensures the pipeline stops if any step fails.

### 2. `validate_data.py`
The **Quality Gate**. This script acts as a final circuit breaker before data is committed to the repository:
- Reuses validation logic from Phase 1 to check individual scheme integrity.
- Performs completeness checks (ensuring all 6 mandatory funds are present).
- Detects anomalies such as empty data files or suspicious NAV values.
- Returns a non-zero exit code on failure to block the GitHub Actions deployment.

### 3. `IMPLEMENTATION_PLAN0.md`
The **Technical Roadmap**. Contains the detailed design decisions, orchestration flow, and infrastructure requirements (GitHub Secrets) for the automation layer.

## Automation Trigger
The orchestration logic is triggered daily via:
- **GitHub Actions**: `.github/workflows/daily_corpus_refresh.yml`
- **Schedule**: Every day at **09:00 AM IST** (`30 3 * * *` UTC).
- **Manual**: Can be triggered via the "Run workflow" button in the GitHub Actions tab.

## Local Execution
To run the full refresh pipeline locally from the project root:
```bash
python src/phase0_scheduler/daily_refresh.py
```

To run only the quality gate:
```bash
python src/phase0_scheduler/validate_data.py
```
