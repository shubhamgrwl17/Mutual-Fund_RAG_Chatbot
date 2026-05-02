# Implementation Plan - Phase 7: Multi-Thread Chat & Session Management

## Goal
Implement a persistent session and memory system to allow multi-turn conversations and follow-up questions.

## 1. Core Logic
- **Storage**: SQLite database (`data/sessions.db`) to store `thread_id`, `user_query`, `bot_response`, and `timestamp`.
- **Memory**: The system will pass the last **3-5 turns** of conversation to the LLM.
- **Context Awareness**: If a user asks about "it" or "the fund," the system will refer to the `active_scheme_id` stored in the session metadata.

## 2. Proposed Changes

### [Phase 7: Session Management]

#### [NEW] manager.py
- Implement `SessionManager` class with SQLite backend.
- **SQLite Schema**:
    - `messages`: (thread_id, role, content, scheme_id, timestamp)
- **Thread Isolation**: Strictly filter by `thread_id` to prevent history leakage.
- **Context Recovery**: If a query is vague (e.g., "What about exit load?"), pull the last `scheme_id` from history to apply as a metadata filter.

#### [NEW] rewriter.py (Defensive Pattern)
- Implement **Query Rewriter**:
    - Uses Llama-3 (8B) to transform vague follow-ups (e.g., "And its NAV?") into full, self-contained queries (e.g., "What is the NAV of Nippon India Growth Fund?") using history.
    - Prevents retrieval failures on pronouns.

#### [MODIFY] src/phase6_generation/generator.py
- Update `generate_answer(query, thread_id=None)`:
    - 1. Fetch history from `SessionManager`.
    - 2. If `thread_id` and history exist, run `QueryRewriter`.
    - 3. Pass rewritten query to `Retriever`.
    - 4. Append history to LLM System Prompt.
    - 5. Save the new turn to SQLite.

#### [NEW] run_session_test.py
- Test script for multi-turn chat:
    - Turn 1: "Tell me about HDFC Mid-cap."
    - Turn 2: "What is its NAV?" (Verify it knows "its" refers to HDFC).

---

## 3. Verification Plan

### Test Scenarios
1. **Thread Isolation**: Ensure messages from Thread A do not leak into Thread B.
2. **Follow-up Resolution**: Verify that asking "What is the exit load?" after a fund-specific question correctly retrieves data for that fund.
3. **Persistence**: Restart the test script and ensure history is still accessible via `thread_id`.

### Success Criteria
- **Contextual Accuracy**: The bot must correctly identify the subject of follow-up questions in 90%+ of cases.
- **Latency**: Adding SQLite lookups should add < 100ms to the total response time.
