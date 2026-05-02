# Implementation Plan - Phase 6: Generation Pipeline

## Goal
Implement the final generation stage that converts retrieved chunks into accurate, concise, and cited answers using Groq AI.

## 1. Core Logic
The generation phase will follow these strict rules to ensure factual integrity:
- **Conciseness**: Maximum 3 sentences per answer (plus footer).
- **Citations**: Always include the `Source: [URL]` at the end.
- **Freshness**: Always include the `Last updated from sources: [Date]` at the end.
- **Hallucination Prevention**: Any number mentioned in the answer MUST exist in the retrieved context.

## 2. Proposed Changes

### [Phase 6: Generation Logic]

#### [MODIFY] src/phase6_generation/prompts.py
- **System Prompt**: 
    - Strictly factual, 3-5 sentences.
    - **Aggregation Permission**: Explicitly allow LLM to combine data from multiple context chunks to build tables/lists.
    - Mandatory Citation: "Source: [URL]"
    - Mandatory Footer: "Last updated from sources: [Date]"

#### [MODIFY] src/phase6_generation/validator.py
- **Hallucination Detector**:
    - **Number Normalization**: Remove symbols (%, ₹) and punctuation (trailing dots) before matching.
    - **Skip List**: Ignore 1-31 (dates/lists) and years (2024-2026).
- **Sentence Limit**: 
    - 5 sentences for FACTUAL.
    - 6 sentences for MULTI_INTENT (to allow for the advisory refusal).

#### [NEW] generator.py
- Implement `AnswerGenerator` class.
- **Model Fallback**: Implement a retry chain using `llama-3.3-70b-versatile` (Primary) and `llama-3.1-8b-instant` (Fallback).
- **Auto-Fix Logic**: If the validator flags a missing citation or footer, the generator will automatically append it using chunk metadata before returning the response to the user.

#### [NEW] validator.py (Defensive Engineering)
- Implement `ResponseValidator`.
- Logic:
    - **Sentence Count**: Fails if > 4 sentences.
    - **Citation & Footer Check**: Detects missing `Source:` or `Last updated:` lines.
    - **Advisory Scan**: Scans for "blacklisted" phrases like *"I recommend"*, *"better than"*, or *"good choice"*.
    - **Fact Check**: Compares all numbers in the response against the context text. If a number doesn't match, the answer is rejected.

#### [NEW] run_generation.py
- End-to-end test CLI to verify:
    - Happy path (Fact query -> Cited answer).
    - Hallucination prevention (simulated bad context).
    - Advisory refusal integration.

---

## 3. Verification Plan

### End-to-End Tests
1. **Fact Retrieval**: "NAV of HDFC Mid-cap?" -> Verify format: [Fact]. [Fact]. Source: [URL]. Last Updated: [Date].
2. **Advisory Rejection**: "Should I buy SBI?" -> Verify it returns the Phase 5 refusal message.
3. **Multi-Intent**: "What is the exit load of Nippon and is it a good buy?" -> Verify it answers the exit load but ignores the "is it good" part.

### Success Criteria
- **100% Citation Rate**: Every factual answer must have a source link.
- **Zero Hallucinations**: Post-generation validator must successfully catch any "invented" numbers.
