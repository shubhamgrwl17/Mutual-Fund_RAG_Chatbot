# Implementation Plan - Phase 9: Evaluation & Edge Case Testing

## Goal
Validate the system against a wide range of adversarial and factual queries before final delivery.

## 1. Test Matrix
- **Advisory Resistance**: 20 queries designed to trick the bot into giving advice.
- **Fact Verification**: 50 factual queries across 6 funds (NAV, Manager, Expense).
- **Format Compliance**: Ensure all 70 responses have citations and footers.
- **Latency Audit**: Measure P50 and P99 response times.

## 2. Tools
- `src/phase9_evaluation/evaluator.py`: Automated script to run queries and log results to a CSV.
- Manual review of the CSV to check for tone and accuracy.

## 3. Success Criteria
- 0% Advisory leak (no recommendations allowed).
- 100% Citation presence.
- < 3.5s average response time.
