# Mutual Fund RAG Chatbot

A production-ready, facts-only Retrieval-Augmented Generation (RAG) assistant for Mutual Funds. This assistant provides accurate information about mutual fund schemes, NAVs, and holdings using data scraped from Groww.

## 🚀 Phase 0: Automation & Scheduled Refresh
The project features a fully automated data pipeline that refreshes the corpus every day at **09:00 AM IST**.
- **Orchestration**: Chained scraping, chunking, and indexing.
- **Quality Gate**: Automated sanity checks to ensure 100% data integrity.
- **Infrastructure**: Powered by GitHub Actions.

## 🏗️ Architecture
The system is built on a 10-phase modular architecture:
1.  **Phase 0**: Automation & Scheduler
2.  **Phase 1**: Ingestion (Scraping __NEXT_DATA__)
3.  **Phase 2**: Section-Based Chunking
4.  **Phase 3**: Embedding & Vector Storage (BGE-Small + ChromaDB)
5.  **Phase 4**: Semantic Retrieval
6.  **Phase 5**: Guardrails (PII & Out-of-Scope Detection)
7.  **Phase 6**: Factual Generation (Groq/LLAMA-3)
8.  **Phase 7**: Session Management
9.  **Phase 8**: User Interface
10. **Phase 9**: Evaluation
11. **Phase 10**: Deployment & Monitoring

For detailed technical details, see [docs/rag_architecture.md](docs/rag_architecture.md).

## 🛠️ Local Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your `.env` file (see `.env.example`).
4. Run the daily refresh manually:
   ```bash
   python src/phase0_scheduler/daily_refresh.py
   ```

## 🛡️ Defensive Engineering
This project follows strict defensive engineering principles to prevent hallucinations and ensure 100% factual accuracy. See [docs/defensive_engineering_guide.md](docs/defensive_engineering_guide.md) for more details.
