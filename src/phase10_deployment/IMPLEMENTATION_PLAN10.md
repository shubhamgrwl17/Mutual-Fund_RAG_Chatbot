# Implementation Plan - Phase 10: Deployment & Automation

## Goal
Establish a self-healing, automated data pipeline using GitHub Actions to keep the mutual fund corpus (NAV, AUM, holdings) fresh without manual intervention, while maintaining strict data quality gates.

## 1. Automation Workflow (Daily Scheduler)
- **Frequency**: Every day at **03:30 UTC (09:00 AM IST)**.
- **Workflow Steps**:
    1. **Setup**: Python environment & dependencies.
    2. **Refresh Pipeline**: Run `src/phase0_scheduler/daily_refresh.py`.
        - Scrape Groww URLs using `__NEXT_DATA__` extraction.
        - **Diff Detection**: Compare with previous data; skip re-index if no changes.
        - Re-chunk and re-embed only modified schemes.
        - Sync to Cloud Vector DB (Hugging Face Spaces / Chroma Remote).
    3. **Data Quality Gate**: Run `src/phase0_scheduler/validate_data.py`.
        - Verify schema compliance and sanity checks (NAV > 0).
        - **Critical**: Pipeline must fail and block commit if validation fails.
    4. **Persistence**: Commit updated `data/` artifacts back to the repository.
        - Use `git push --force-with-lease` to prevent silent merge conflicts.

## 2. Monitoring & Resilience
- **Failure Alerts**: GitHub Actions will send failure notifications on any step crash or validation failure.
- **Status Visibility**: Add a "Daily Refresh" status badge to the main `README.md`.
- **Retries**: Configure the workflow with 1 automatic retry on failure to handle transient network issues.

## 3. Production Environment & Secrets
Ensure the following GitHub Secrets are configured:
- `GROQ_API_KEY`: For LLM-based query processing and intent classification.
- `HUGGINGFACE_API_KEY`: For syncing to the Space Hub.
- `CHROMA_HOST` / `CHROMA_AUTH_TOKEN`: For remote vector store access.
- `GITHUB_TOKEN`: For repository commits (automatic).
- `SLACK_WEBHOOK_URL` (Optional): For real-time failure alerts.

## 4. Technical Implementation Details

### 4.1 Scheduler Refinement (Diff Detection)
The `src/phase0_scheduler/daily_refresh.py` will be updated to:
- Load the previous day's processed JSON data.
- Compare key metrics (`nav`, `aum`, `holdings`) for all 6 schemes.
- **Skip Logic**: If changes are within a 0% threshold (identical), the pipeline will log "No changes detected" and skip the expensive embedding and vector DB update steps.

### 4.2 Application Containerization
A root-level `Dockerfile` will be implemented using a multi-stage build to serve the Next.js frontend via the FastAPI backend:
```dockerfile
# Stage 1: Build Frontend
FROM node:18-slim AS frontend-builder
WORKDIR /app/frontend
COPY src/phase8_ui/frontend/package*.json ./
RUN npm install
COPY src/phase8_ui/frontend/ .
RUN npm run build

# Stage 2: Backend & Runner
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Copy static frontend build to a directory FastAPI can serve
COPY --from=frontend-builder /app/frontend/out /app/src/phase8_ui/static
EXPOSE 7860
CMD ["uvicorn", "src.phase8_ui.app:app", "--host", "0.0.0.0", "--port", "7860"]
```

### 4.3 GitHub-to-HuggingFace Sync
The `.github/workflows/daily_corpus_refresh.yml` will be extended with a sync job:
```yaml
sync-to-hub:
  needs: refresh-corpus
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
        lfs: true
    - name: Push to Hub
      env:
        HF_TOKEN: ${{ secrets.HUGGINGFACE_API_KEY }}
      run: git push --force https://shubhamgrwl17:$HF_TOKEN@huggingface.co/spaces/shubhamgrwl17/Mutual-Fund_RAG_Chatbot main
```

## 5. Verification Plan
- [ ] **Automation**: Trigger `workflow_dispatch` manually; verify logs show "Changes detected" or "Skipping re-index" correctly.
- [ ] **Safety**: Simulate a data corruption (e.g., empty NAV) to verify the **Quality Gate** blocks the commit.
- [ ] **Hosting**: Verify the Hugging Face Space URL loads correctly and displays the "Last Updated" timestamp.
- [ ] **End-to-End**: Perform a live query and check if the citation link matches the latest source URL.
