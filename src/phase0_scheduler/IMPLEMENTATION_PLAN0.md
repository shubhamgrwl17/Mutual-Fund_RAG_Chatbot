# Implementation Plan - Phase 0: Automation & Scheduled Refresh

## 1. Goal
Establish an automated "Data Heartbeat" that keeps the chatbot's knowledge fresh without manual intervention. This phase builds the orchestration layer that ensures the assistant always answers from the most recent NAV and fund data.

## 2. Automation Architecture (GitHub Actions)
- **Host**: GitHub Actions (Cloud-native, zero infrastructure).
- **Trigger**: 
    - **Cron Job**: Daily at 09:00 AM IST (`30 3 * * *` UTC).
    - **Workflow Dispatch**: Manual trigger for ad-hoc refreshes.
- **Service Decoupling**: The scheduler runs independently of the FastAPI application, pushing updates to the repository and the vector store.

## 3. Implementation Steps (The Orchestration Flow)

### 3.1 Step 1: Scrape & Validate (Phase 1 Integration)
- Run `src/phase1_scraping/scraper.py`.
- **Defensive Gate**: Implement `fetch_with_retry` with exponential backoff and browser-like headers to bypass anti-bot measures.
- **Edge Case (1.3)**: After extraction, run `src/phase1_scraping/validator.py` to ensure the `__NEXT_DATA__` schema hasn't changed.

### 3.2 Step 2: Diff Detection & Processing (Phase 2 Integration)
- Compare the new scrape with the previous version stored in `data/raw/`.
- **Cost Optimization**: Only proceed to re-embedding if a meaningful diff is detected (e.g., NAV, AUM, or Expense Ratio changes).
- Run `src/phase2_chunking/chunker.py` using **null-safe formatters** to handle missing fields (Edge Case 2.1–2.5).

### 3.3 Step 3: Re-Embed & Index (Phase 3 Integration)
- Generate new vectors for changed chunks using `bge-small-en-v1.5`.
- **Upsert Strategy**: Update the Vector Store (ChromaDB/Pinecone) using `chunk_id` to overwrite stale data.

### 3.4 Step 4: The Quality Gate (src/phase0_scheduler/validate_data.py)
- **Critical Safety Step**: Before committing data back to the repo, run a final validation:
    - [ ] **Empty Data Check**: Fail if any scheme JSON is empty.
    - [ ] **Sanity Check**: Alert if NAV values swing > 20% in 24 hours.
    - [ ] **Completeness**: Ensure all 6 mandatory schemes are present.
    - [ ] **Link Integrity**: Periodically check that citation URLs are still valid (Edge Case 8.3).

### 3.5 Step 5: Commit & Notify
- Auto-commit updated `data/` files to the main branch.
- **Git Safety**: Use `git diff --cached --quiet` to avoid empty commits and handle push failures gracefully.
- **Alerting**: Configure GitHub Actions to send Slack/Email notifications on workflow failure.

## 4. Infrastructure (GitHub Secrets)
| Secret Name | Purpose |
|-------------|----------|
| `GROQ_API_KEY` | For LLM-based intent classification and generation. |
| `HUGGINGFACE_API_KEY` | For local/remote embedding inference. |
| `VECTOR_DB_API_KEY` | Authentication for managed vector store. |
| `SLACK_WEBHOOK_URL` | For failure notifications and quality alerts. |

## 5. Verification Plan
1. **Dry Run**: Run the `src/phase0_scheduler/daily_refresh.py` script locally with a mocked `__NEXT_DATA__` response.
2. **CI Validation**: Trigger the GitHub Action manually (`workflow_dispatch`) and verify:
    - [ ] The `last_updated` field in `data/processed/` is updated.
    - [ ] The vector store contains the new embeddings.
    - [ ] The commit is visible in the repo history.
3. **Recovery Test**: Intentionally delete a required field in a raw JSON and verify the "Quality Gate" blocks the commit.
