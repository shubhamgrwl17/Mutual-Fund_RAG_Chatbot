from typing import Dict, Any
from src.phase5_guardrails.input_validator import validate_input
from src.phase5_guardrails.pii_detector import contains_pii
from src.phase5_guardrails.classifier import IntentClassifier

class MasterGuard:
    def __init__(self):
        self.classifier = IntentClassifier()

    def check(self, query: str) -> Dict[str, Any]:
        """
        Full guardrail orchestration.
        Returns: {
            "is_safe": bool,
            "category": str,
            "refusal_message": str | None,
            "action": str (PROCEED | BLOCK | GREET)
        }
        """
        # 1. Basic Validation
        is_valid, err_msg = validate_input(query)
        if not is_valid:
            return {
                "is_safe": False,
                "category": "INVALID_INPUT",
                "refusal_message": err_msg,
                "action": "BLOCK"
            }

        # 2. PII Detection
        has_pii, pii_type = contains_pii(query)
        if has_pii:
            return {
                "is_safe": False,
                "category": "PII",
                "refusal_message": f"I cannot process queries containing sensitive information like {pii_type}. Please remove it and try again.",
                "action": "BLOCK"
            }

        # 3. Intent Classification (LLM)
        category = self.classifier.classify(query)
        
        # 4. Action Mapping
        if category == "FACTUAL":
            return {"is_safe": True, "category": category, "refusal_message": None, "action": "PROCEED"}
            
        elif category == "GREETING":
            return {"is_safe": True, "category": category, "refusal_message": "Hello! I can provide factual information about mutual funds. How can I help you today?", "action": "GREET"}
            
        elif category == "ADVISORY":
            return {
                "is_safe": False,
                "category": category,
                "refusal_message": "I am a facts-only assistant and cannot provide investment advice or recommendations. I can, however, provide data on NAVs, exit loads, and returns.",
                "action": "BLOCK"
            }
            
        elif category == "MULTI_INTENT":
            return {
                "is_safe": True,
                "category": category,
                "refusal_message": None, # Will be handled by prompt logic in Phase 6
                "action": "PROCEED",
                "warning": "Part of your query is advisory and will be ignored. I will only answer the factual portion."
            }
            
        elif category == "INJECTION":
            return {
                "is_safe": False,
                "category": category,
                "refusal_message": "I can only answer factual questions about mutual fund schemes.",
                "action": "BLOCK"
            }
            
        else: # OUT_OF_SCOPE
            return {
                "is_safe": False,
                "category": category,
                "refusal_message": "I'm sorry, I can only answer questions related to the mutual fund schemes in my database.",
                "action": "BLOCK"
            }
