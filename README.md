---
title: Mutual Fund Assistant
emoji: 📈
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 📈 Mutual Fund RAG Chatbot

A production-ready, facts-only Retrieval-Augmented Generation (RAG) assistant for Mutual Funds. This assistant provides 100% accurate information about mutual fund schemes, NAVs, and holdings using data scraped directly from Groww.

> [!CAUTION]
> **Financial Disclaimer**: This chatbot is an AI-powered tool providing factual information for educational purposes only. It **does not** provide investment advice, financial planning, or recommendations. Mutual fund investments are subject to market risks. Please read all scheme-related documents carefully before investing or consult a certified financial advisor.

---

## 🎯 Sample Q&A (Live Examples)
Here is how the assistant responds to various types of queries. Notice the strict adherence to facts, citations, and length limits.

<details>
<summary><b>1. Basic Fact (NAV Inquiry)</b></summary>

**Q: What is the current NAV of HDFC Mid-Cap Fund?**
**A:** The current NAV of HDFC Mid-Cap Fund Direct Growth is ₹217.7200 as of 30-Apr-2026. 
*Source: https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth*
*Last updated from sources: 2026-04-30*
</details>

<details>
<summary><b>2. Financial Policy (Exit Load)</b></summary>

**Q: What is the exit load for Nippon India Growth Fund?**
**A:** The exit load for Nippon India Growth Mid Cap Fund Direct Growth is 1% if redeemed within 1 month.
*Source: https://groww.in/mutual-funds/nippon-india-growth-mid-cap-fund-direct-growth*
*Last updated from sources: 2026-04-30*
</details>

<details>
<summary><b>3. Personnel (Fund Manager)</b></summary>

**Q: Who is the fund manager for Motilal Oswal Midcap Fund?**
**A:** The fund managers for Motilal Oswal Midcap Fund are Ankit Agarwal, Swapnil P Mayekar, Ajay Khandelwal, Varun Sharma, and Rakesh Shetty. 
*Source: https://groww.in/mutual-funds/motilal-oswal-most-focused-midcap-30-fund-direct-growth*
*Last updated from sources: 2026-04-30*
</details>

<details>
<summary><b>4. Operational (SIP Limits)</b></summary>

**Q: What is the minimum SIP limit of SBI Midcap Fund?**
**A:** The minimum SIP investment for SBI Mid Cap Direct Plan Growth is ₹500.
*Source: https://groww.in/mutual-funds/sbi-mid-cap-direct-plan-growth*
*Last updated from sources: 2026-04-30*
</details>

<details>
<summary><b>5. Portfolio (Holdings)</b></summary>

**Q: What are the top holdings of ICICI Prudential Midcap Fund?**
**A:** The top 10 stock holdings of ICICI Prudential Midcap Fund are: 1. Jindal Steel Ltd. (4.72176803%) - Sector: Metals & Mining 2. Multi Commodity Exchange Of India Ltd. (4.51000991%) - Sector: Services 3. APL Apollo Tubes Ltd. (4.20262199%) - Sector: Metals & Mining 4. BSE Ltd. (4.13361058%) - Sector: Services 5. Apar Industries Ltd. (3.96684415%) - Sector: Consumer Staples 6. Muthoot Finance Ltd. (3.96650619%) - Sector: Financial 7. Jindal Stainless Ltd. (3.36247209%) - Sector: Metals & Mining 8. Bharti Hexacom Ltd. (3.1617069%) - Sector: Communication 9. Vedanta Ltd. (3.11856792%) - Sector: Metals & Mining 10. PB Fintech Ltd. (3.06172773%) - Sector: Services
*Source: https://groww.in/mutual-funds/icici-prudential-midcap-fund-direct-growth*
*Last updated from sources: 2026-04-30*
</details>

<details>
<summary><b>6. Cost (Expense Ratio)</b></summary>

**Q: What is the expense ratio of Mirae Asset Midcap Fund?**
**A:** The expense ratio for the Direct Growth plan of Mirae Asset Midcap Fund is 0.59%.
*Source: https://groww.in/mutual-funds/mirae-asset-midcap-fund-direct-growth*
*Last updated from sources: 2026-04-30*
</details>

<details>
<summary><b>7. Safety (Risk Level)</b></summary>

**Q: What is the risk level of HDFC Mid-Cap Opportunities Fund?**
**A:** The risk level of HDFC Mid Cap Fund is Moderately High.
*Source: https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth*
*Last updated from sources: 2026-04-30*
</details>

<details>
<summary><b>8. Performance (Historical Returns)</b></summary>

**Q: How has the Motilal Oswal Midcap Fund performed in the last 3 years?**
**A:** The Motilal Oswal Midcap Fund has performed with a 3-year CAGR of 22.08%, compared to the category average of 21.621655585469462% CAGR.
*Source: https://groww.in/mutual-funds/motilal-oswal-most-focused-midcap-30-fund-direct-growth*
*Last updated from sources: 2026-04-30*
</details>

<details>
<summary><b>9. Advisory Refusal (Safety Guardrail)</b></summary>

**Q: Should I invest in Nippon India Growth Fund for my daughter's education?**
**A:** I am a facts-only assistant and cannot provide investment advice or recommendations. I can, however, provide data on NAVs, exit loads, and returns.
</details>

<details>
<summary><b>10. Out-of-Scope (Topic Guardrail)</b></summary>

**Q: Who won the cricket match yesterday?**
**A:** I'm sorry, I can only answer questions related to the mutual fund schemes in my database.
</details>

---

## 📚 Source List (Tracked Schemes)
The system currently tracks and provides real-time facts for the following direct growth mid-cap schemes:
1.  **[HDFC Mid-Cap Opportunities Fund](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth)**
2.  **[Nippon India Growth Fund](https://groww.in/mutual-funds/nippon-india-growth-mid-cap-fund-direct-growth)**
3.  **[Motilal Oswal Midcap Fund](https://groww.in/mutual-funds/motilal-oswal-most-focused-midcap-30-fund-direct-growth)**
4.  **[Mirae Asset Midcap Fund](https://groww.in/mutual-funds/mirae-asset-midcap-fund-direct-growth)**
5.  **[ICICI Prudential Midcap Fund](https://groww.in/mutual-funds/icici-prudential-midcap-fund-direct-growth)**
6.  **[SBI Magnum Midcap Fund](https://groww.in/mutual-funds/sbi-mid-cap-direct-plan-growth)**

*Data is refreshed daily at 09:00 AM IST via automated pipelines.*

---

## 🏗️ Architecture: The 12-Phase Blueprint
The project follows a rigorous 12-phase modular architecture to ensure data integrity and factual accuracy.

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 0: THE SCHEDULER (Alarm Clock)                 │
│  • What it does: Wakes up the system every day at 9:00 AM IST.             │
│  • Tools: GitHub Actions (GHA).                                             │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 1: SCRAPING (Data Collection)                  │
│  • What it does: Visits Groww.in and extracts "__NEXT_DATA__" JSON.         │
│  • Tools: BeautifulSoup4, Requests.                                         │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 2: CHUNKING (Data Organizing)                  │
│  • What it does: Cleans messy web data into logical sections.               │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 3: EMBEDDING & VECTOR DB                       │
│  • What it does: Translates text to vectors and saves in ChromaDB.          │
│  • Tools: BAAI/bge-small-en-v1.5, ChromaDB.                                 │
│  • Hosting: Hugging Face Spaces (Remote Chroma Server).                     │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 4: RETRIEVAL (The Fact Finder)                 │
│  • What it does: Finds exact sections using Hybrid Search + Re-ranking.     │
│  • Tools: BM25, Cross-Encoder (ms-marco-MiniLM).                            │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 5: GUARDRAILS (The Security Guard)             │
│  • What it does: Checks for PII, Intent (Fact vs Advice), and Safety.       │
│  • Tools: Groq API (Llama 3.3 70B).                                         │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 6: GENERATION (The AI Brain)                   │
│  • What it does: Writes a 3-sentence factual answer using retrieved facts.  │
│  • Tools: Groq API (Llama 3.3 70B).                                         │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 7: SESSION (The Short-Term Memory)              │
│  • What it does: Manages history and performs Query Rewriting.              │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 8: UI (The User Interface)                     │
│  • What it does: Next.js Frontend + FastAPI Backend.                        │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 9: EVALUATION (The Quality Audit)              │
│  • What it does: Measures accuracy, latency, and factual correctness.       │
│  • Tools: Custom Python scripts, JSON reports.                              │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        PHASE 10: DEPLOYMENT (Going Live)                    │
│  • What it does: Deploys the app & DB to Hugging Face via Docker.           │
│  • Tools: Docker (Multi-stage), Hugging Face Spaces.                        │
└────────────────────────────────────────────────────────────────────────────┘
```

For a deeper dive into each phase, see [docs/project_deep_dive.md](docs/project_deep_dive.md).

---

## 🛡️ Defensive Engineering & AI Prompts
This project prioritizes **Facts over Fluency**. We use 4 specialized AI prompts to keep the assistant on track:

1.  **Intent Classification**: Filters out investment advice or out-of-scope queries.
2.  **System Rules**: Enforces strict "Facts-Only" behavior (No hallucinations).
3.  **User Fact-Sheet**: Provides the LLM with only relevant, retrieved context.
4.  **Query Rewriting**: Maintains conversation context without losing precision.

See [docs/defensive_engineering_guide.md](docs/defensive_engineering_guide.md) for detailed prompt engineering strategies.

## 🛠️ Local Setup
1. **Clone the repository.**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure Environment**: Create a `.env` file (refer to `.env.example`).
4. **Initialize Data**: Run the manual refresh to populate your local database:
   ```bash
   python src/phase0_scheduler/daily_refresh.py
   ```
5. **Start the App**:
   ```bash
   uvicorn src.main:app --reload
   ```

---

## ❓ Frequently Asked Questions (FAQ)

**1. Where does the data come from?**
The data is scraped daily from Groww.in using their internal `__NEXT_DATA__` JSON structure, which provides the most accurate and raw data used to power their own website.

**2. How often is the information updated?**
An automated GitHub Action runs every morning at **09:00 AM IST** to refresh the corpus with the latest NAVs, holdings, and fund manager details.

**3. Does this bot provide investment recommendations?**
No. The bot is strictly a factual assistant. It is equipped with intent-detection guardrails that identify advisory questions and politely redirect users to consult a certified financial advisor.

**4. Can I ask about any mutual fund in India?**
Currently, the bot is optimized for 6 major Mid-Cap schemes. We are expanding the source registry to include more categories (Small-Cap, Large-Cap) in future updates.

**5. Why are the answers limited to 3-5 sentences?**
To prevent "LLM Yapping" and ensure high precision, we enforce a strict length limit. This ensures you get the exact facts you need without unnecessary filler.

---
*Built with ❤️ for the AI/ML community.*
