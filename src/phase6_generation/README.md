# Phase 6 — Prompt Engineering & Generation

## Overview
Takes the retrieved context and formats a highly restrictive prompt for Groq AI to generate a factual, source-cited response.

## Responsibilities
- Constructs the System Prompt with anti-hallucination and anti-advice rules.
- Injects retrieved context strings.
- Calls the Groq AI API (`llama-3.3-70b-versatile`).
- Formats the final response, guaranteeing exactly ONE source citation and a "Last updated" footer.
