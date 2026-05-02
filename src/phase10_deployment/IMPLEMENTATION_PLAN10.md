# Implementation Plan - Phase 10: Deployment & Automation

## Goal
Automate the data refresh cycle using GitHub Actions to ensure the bot always has current NAV and AUM data.

## 1. Automation Workflow
- **Frequency**: Every night at 00:00 UTC.
- **Workflow**:
    - 1. Setup Python environment.
    - 2. Run `src/phase1_ingestion/scraper.py`.
    - 3. Run `src/phase2_chunking/chunker.py`.
    - 4. Run `src/phase3_2_vector_db/cloud_sync.py` to update the cloud store.
    - 5. Commit updated local corpus (JSONL) back to the repo.

## 2. Monitoring & Alerts
- If any step fails, GitHub Actions will send a failure notification.
- Add a "Last Scrape Status" badge to the README.

## 3. Production Environment
- Ensure `CHROMA_MODE=remote` is set in the CI environment.
- Inject `GROQ_API_KEY` and `CHROMA_HOST` as GitHub Secrets.
