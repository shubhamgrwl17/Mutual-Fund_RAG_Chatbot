import os
import logging
from typing import Dict, Any, List
from groq import Groq
from dotenv import load_dotenv

from src.phase4_retrieval.retriever import HybridRetriever
from src.phase5_guardrails.guard import MasterGuard
from src.phase6_generation.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from src.phase6_generation.validator import ResponseValidator
from src.phase7_session.manager import SessionManager
from src.phase7_session.rewriter import QueryRewriter

logger = logging.getLogger(__name__)

class AnswerGenerator:
    def __init__(self):
        load_dotenv()
        self.guard = MasterGuard()
        self.retriever = HybridRetriever()
        self.validator = ResponseValidator()
        self.sessions = SessionManager()
        self.rewriter = QueryRewriter()
        
        api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=api_key)
        
        # Model Fallback Chain
        self.models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

    def _call_llm(self, system: str, user: str, history: List[Dict[str, str]] = None) -> str:
        """Call Groq API with fallback support and history injection."""
        last_error = None
        
        # Build message stack with history
        messages = [{"role": "system", "content": system}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user})

        for model in self.models:
            try:
                logger.info(f"Calling LLM ({model}) with history...")
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=400
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.warning(f"Model {model} failed: {e}")
                last_error = e
                continue
        raise last_error

    def generate_answer(self, query: str, thread_id: str = "default") -> Dict[str, Any]:
        """
        End-to-end generation flow with Memory: History -> Rewrite -> Guard -> Retrieve -> Generate.
        """
        # 1. Fetch History
        history = self.sessions.get_history(thread_id)
        
        # 2. Query Rewriting (Context Resolution)
        search_query = self.rewriter.rewrite(query, history) if history else query

        # 3. Guardrail Check (On Original Query for Intent)
        guard_result = self.guard.check(query)
        if not guard_result["is_safe"] or guard_result["action"] == "GREET":
            self.sessions.save_message(thread_id, "user", query)
            self.sessions.save_message(thread_id, "assistant", guard_result["refusal_message"])
            return {
                "answer": guard_result["refusal_message"],
                "source": "Guardrail",
                "status": guard_result["category"]
            }

        # 4. Retrieval (Using Rewritten Query)
        retrieval_result = self.retriever.retrieve(search_query)
        if retrieval_result["status"] != "SUCCESS":
            return {
                "answer": retrieval_result["message"],
                "source": "Retriever",
                "status": retrieval_result["status"]
            }
        
        context_chunks = retrieval_result["context"]
        if not context_chunks:
             return {
                "answer": "I don't have this information in my sources.",
                "source": "System",
                "status": "NO_CONTEXT"
            }

        # 5. Prompt Construction
        context_text = "\n\n".join([f"CHUNK:\n{c['content']}" for c in context_chunks])
        source_urls = "\n".join(list(set([c['source_url'] for c in context_chunks])))
        
        user_prompt = USER_PROMPT_TEMPLATE.format(
            context_text=context_text,
            source_urls=source_urls,
            query=query
        )

        # 6. Generation (Injecting History)
        raw_answer = self._call_llm(SYSTEM_PROMPT, user_prompt, history=history)

        # 7. Post-Validation & Auto-Fix
        validation = self.validator.validate(raw_answer, context_chunks, intent=guard_result["category"])
        final_answer = raw_answer
        
        if not validation["is_valid"]:
            logger.warning(f"Validation issues found: {validation['issues']}")
            if "MISSING_CITATION" in validation["issues"] or "MISSING_FOOTER" in validation["issues"]:
                final_answer = self.validator.auto_fix(raw_answer, context_chunks)
            
            if any("HALLUCINATION" in issue for issue in validation["issues"]):
                return {
                    "answer": "I'm sorry, I couldn't generate a high-confidence factual answer. Please check groww.in directly.",
                    "source": "Validator",
                    "status": "HALLUCINATION_REJECTED"
                }

        # 8. Save Turn to Session
        # Identify the scheme discussed for future context recovery
        active_scheme_id = retrieval_result["context"][0].get("scheme_id") if retrieval_result["context"] else None
        self.sessions.save_message(thread_id, "user", query, scheme_id=active_scheme_id)
        self.sessions.save_message(thread_id, "assistant", final_answer, scheme_id=active_scheme_id)

        return {
            "answer": final_answer,
            "source": "LLM",
            "status": "SUCCESS",
            "metadata": {
                "chunks_used": len(context_chunks),
                "intent": guard_result["category"],
                "validation_issues": validation["issues"],
                "rewritten_query": search_query if search_query != query else None
            }
        }
