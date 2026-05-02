# Implementation Plan - Phase 8: User Interface

## Goal
Build a professional, production-grade web interface and API for the Mutual Fund RAG Assistant.

## 1. Backend: FastAPI
- **File**: `src/phase8_ui/app.py`
- **Endpoints**:
    - `POST /api/chat`: Takes `query` and `thread_id`. Returns full RAG response.
    - `GET /api/threads`: Lists recent chat threads from SQLite.
    - `POST /api/threads`: Creates a new UUID-based thread.
    - `GET /api/history/{thread_id}`: Fetches history for a specific thread.

## 2. Frontend: React (Vite)
- **Tech Stack**: React + Vite + Vanilla CSS.
- **Design System**: 
    - Dark mode by default.
    - Primary Color: Emerald Green / Royal Blue (Financial trust).
    - Typography: Inter / Roboto.
- **Layout**:
    - **Sidebar**: Thread history, "New Chat" button.
    - **Main View**: 
        - Header with bot description.
        - Scrollable chat area.
        - Input box with auto-resize.
        - **Sticky Disclaimer**: "Facts-only. No investment advice."
    - **Features**:
        - Clickable example chips (e.g., "What is HDFC NAV?").
        - Loading skeletons/spinners for LLM latency.
        - Markdown rendering for tables and citations.

## 3. Deployment Flow
- UI and API will communicate via standard REST.
- Environment variables (`.env`) must be shared with the API.

## 4. Verification Plan
1. **API Test**: Verify `/api/chat` returns valid JSON with all RAG metadata.
2. **UI Test**: Verify dark mode renders correctly on mobile and desktop.
3. **Thread Test**: Create 2 threads in the UI and verify history is separate and persistent.
