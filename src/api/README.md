# API Layer

## Overview
FastAPI application that serves the mutual fund chat endpoints. It wires all the individual phases together into a functional backend.

## Responsibilities
- REST API endpoint for chat messages (`/chat`).
- Request/Response validation using Pydantic.
- Integration of the full RAG pipeline (Guardrails -> Rewrite -> Retrieval -> Generation).
