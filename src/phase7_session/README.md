# Phase 7 — Session Management & Context Window

## Overview
Maintains conversation threads (session state) allowing the RAG system to handle multi-turn follow-up questions intelligently.

## Responsibilities
- Manages chat history per thread (session).
- Implements a Query Rewriter to resolve pronouns (e.g., "What is its NAV?") into standalone queries before retrieval.
- Enforces Context Window Management (e.g., keeping only the last 10 messages).
