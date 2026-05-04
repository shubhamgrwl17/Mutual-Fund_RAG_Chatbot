# 🚀 Mutual Fund RAG Chatbot: The Scaled Analytical Blueprint

This document outlines the architectural evolution required to scale the project from 6 schemes to a comprehensive, all-fund analytical engine. It follows the original 12-phase structure, highlighting upgrades and new steps (0.5 increments).

---

## 🗺️ The Scaled Architecture (V2)

```text
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 0: THE SCHEDULER (Alarm Clock)                 │
│  • What it does: Wakes up the system every day at 9:00 AM IST.             │
│  • Strategy: ~~Cron Job~~ -> **Distributed Task Queue Trigger**.           │
│  • Tools: GitHub Actions -> **Airflow / Prefect (for complex DAGs)**.       │
│  • APIs: None.                                                              │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                 PHASE 0.5: DISCOVERY (The Scout) [NEW]                     │
│  • What it does: Finds all 5,000+ mutual fund links from Groww sitemaps.    │
│  • Strategy: XML Sitemap Parsing + URL filtering.                           │
│  • Tools: Python (LXML), Scrapy Discovery.                                  │
│  • APIs: None.                                                              │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 1: SCRAPING (Data Collection)                  │
│  • What it does: Visits 5,000+ pages and extracts all facts.                │
│  • Strategy: ~~Single-threaded~~ -> **Distributed Headless Browsing**.      │
│  • Tools: ~~BS4 / Requests~~ -> **Playwright / Scrapy / Rotating Proxies**. │
│  • External Dependencies: Groww Website (Massive Scale).                    │
│  • APIs: None.                                                              │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 2: EXTRACTION (Data Organizing)                │
│  • What it does: Turns raw JSON into high-precision structured records.     │
│  • Strategy: ~~Section-based~~ -> **Schema-Strict Metric Extraction**.      │
│  • Tools: ~~Custom Formatters~~ -> **Pydantic / Structured Transformers**.   │
│  • APIs: None.                                                              │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│               PHASE 2.5: ANALYTICAL DB (Structured Store) [NEW]            │
│  • What it does: Stores NAV, Returns, AUM, and Metrics for math.            │
│  • Strategy: Relational Storage for "Computable Power".                     │
│  • Tools: **PostgreSQL (RDS / Managed)**.                                   │
│  • APIs: SQL Interface.                                                     │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 3.1: EMBEDDING (Translation)                   │
│  • What it does: Translates human text into high-dimensional vectors.       │
│  • Strategy: ~~Small Local Model~~ -> **High-Performance Large Model**.      │
│  • Tools: ~~bge-small-en-v1.5~~ -> **BAAI/bge-large-en-v1.5** or **OpenAI**.│
│  • APIs: ~~None~~ -> **Managed Embedding API (optional for scale)**.        │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 3.2: VECTOR DB (The Smart Library)             │
│  • What it does: Saves vectors in a horizontally scalable library.          │
│  • Strategy: ~~Local ChromaDB~~ -> **Cloud Vector DB (pgvector/Pinecone)**. │
│  • Tools: ~~ChromaDB~~ -> **pgvector (inside PostgreSQL)**.                 │
│  • External Dependencies: **Managed Cloud Database**.                       │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 4: RETRIEVAL (The Fact Finder)                 │
│  • What it does: Routes queries to either the Library or the SQL DB.        │
│  • Strategy: ~~Hybrid Search~~ -> **Agentic Router (Vector + SQL)**.        │
│  • Tools: ~~BM25~~ -> **Text-to-SQL Engine**.                               │
│  • APIs: None.                                                              │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 5: GUARDRAILS (The Security Guard)             │
│  • What it does: Classifies if the query is Fact, Comparison, or Aggregat.  │
│  • Strategy: ~~6-Category~~ -> **Advanced Multi-Intent Classification**.    │
│  • Tools: Groq API -> **Specialized Agentic Guardrails**.                  │
│  • Prompts: **🎯 Prompt #1: Advanced Intent (includes COMPARISON intent)**. │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 6: GENERATION (The AI Brain)                   │
│  • What it does: Synthesizes answers from both Text and SQL Data.           │
│  • Strategy: ~~Pure RAG~~ -> **Hybrid RAG + Structured Synthesis**.         │
│  • Tools: Groq API -> **Advanced Reasoning (Llama 3 70B / Gemini Pro)**.    │
│  • Prompts: **📝 Prompt #2: Tabular Reasoning Prompt**.                     │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 7: SESSION (The Short-Term Memory)              │
│  • What it does: Handles multi-turn complex comparisons.                    │
│  • Strategy: Contextual SQL query generation across schemes.                │
│  • Tools: ~~SQLite3~~ -> **PostgreSQL Session Store**.                      │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 8: UI (The User Interface)                     │
│  • What it does: Displays complex comparisons with charts and tables.       │
│  • Strategy: ~~Clean Chat~~ -> **Rich Dashboard Interaction**.              │
│  • Tools: Next.js + **Recharts / Shadcn Tables**.                           │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 9: EVALUATION (The Quality Audit)              │
│  • What it does: Audits mathematical accuracy of SQL aggregations.           │
│  • Strategy: ~~Latence Tracking~~ -> **SQL-Consistency & Math Validation**. │
│  • Tools: **DeepEval / RAGAS for structured data**.                         │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 10: DEPLOYMENT (Going Live)                    │
│  • What it does: Deploys to a scalable, production-grade cloud.             │
│  • Strategy: ~~Hugging Face~~ -> **Managed Kubernetes / AWS Fargate**.      │
│  • Tools: ~~Docker (Single)~~ -> **Microservices Architecture**.            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Upgrades for "Computable Power"

1. **Step 2.5 (SQL Brain)**: This is the biggest change. By adding a Relational Database, we move from "reading paragraphs" to "crunching numbers."
2. **Step 4 (Agentic Routing)**: The bot now decides: "Do I need to read the library (Vector) or do I need to calculate an average (SQL)?"
3. **Step 8 (Rich UI)**: Instead of just text, the bot can now send "JSON Tables" to the frontend, which the UI renders as beautiful, interactive comparison charts.
4. **~~Small Model~~ -> **Large Model**: At scale, we need higher reasoning capabilities for "Text-to-SQL" to ensure the math is always correct.

---

## 📜 Appendix: The New Scaling Prompts

### 1. Advanced Intent Classification (Phase 5 Update)
*Decides if the bot needs the library (RAG) or the calculator (SQL).*

```text
Classify the user query:
1. SEMANTIC: Policy details, exit loads, objectives. (Route to VECTOR)
2. ANALYTICAL: "Average returns", "Top 5 funds", "AUM growth". (Route to SQL)
3. COMPARATIVE: "HDFC vs ICICI", "Compare these two". (Route to HYBRID)
4. ADVISORY: Investment recommendations. (BLOCK)
```

### 2. Tabular Synthesis Prompt (Phase 6 Update)
*Handles the math data returned from the SQL database.*

```text
You have been provided with the following raw SQL data:
{JSON Data from Postgres}

Task: Summarize this data into a factual comparison table. 
Rules: 
- Do not add opinions. 
- Highlight the numerical differences clearly.
- If asking for averages, state the formula used.
```
