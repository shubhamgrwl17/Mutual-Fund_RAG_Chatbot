# Phase 5: Guardrails & Intent Classification

This phase implements the "Security Firewall" of the bot, ensuring compliance and data privacy.

## File Descriptions

| File | Description |
| :--- | :--- |
| `guard.py` | **Master Orchestrator**: The `MasterGuard` class that chains all validation steps (Input -> PII -> Intent). |
| `classifier.py` | **Intent Engine**: Uses Llama-3.3-70b (via Groq) to classify queries into `FACTUAL`, `ADVISORY`, `MULTI_INTENT`, etc. |
| `pii_detector.py` | **Privacy Shield**: Regex-based detection for PAN Cards, Aadhaar, Phone numbers, and Emails. |
| `input_validator.py` | **Basic Gate**: Rejects empty queries or those exceeding 500 characters. |
| `run_guardrails.py` | **Test CLI**: A battery of "Dangerous" queries to verify the system blocks advisory, PII, and injections. |
| `IMPLEMENTATION_PLAN5.md` | **Design Doc**: The detailed safety policy and refusal messages defined for the bot. |

## Safety Features
- **Strict Advisory Blocking**: Prevents investment advice as per regulatory requirements.
- **PII Protection**: Automatically redacts or blocks sensitive Indian ID formats.
- **Prompt Injection Defense**: Detects and thwarts attempts to bypass system instructions.
