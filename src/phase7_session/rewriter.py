import os
import logging
from groq import Groq
from typing import List, Dict

logger = logging.getLogger(__name__)

REWRITE_PROMPT = """
Given the following conversation history and a new user question, rewrite the question to be a standalone, factual search query. 
Resolve all pronouns (like 'it', 'its', 'they', 'this fund') using the history.

History:
{history_text}

New Question: {query}

Standalone Query:
"""

class QueryRewriter:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    def rewrite(self, query: str, history: List[Dict[str, str]]) -> str:
        """Resolves pronouns and context to create a self-contained query."""
        if not history:
            return query

        # Format history for the prompt
        history_text = ""
        for msg in history[-3:]: # Only need last 3 turns for pronoun resolution
            history_text += f"{msg['role'].upper()}: {msg['content']}\n"

        try:
            logger.info("Rewriting query for context resolution...")
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant", # Faster 8B model for rewriting
                messages=[
                    {"role": "system", "content": "You are a query expansion assistant. Rewrite the user question to be self-contained. Do not answer it."},
                    {"role": "user", "content": REWRITE_PROMPT.format(history_text=history_text, query=query)}
                ],
                temperature=0.0,
                max_tokens=100
            )
            rewritten = response.choices[0].message.content.strip().strip('"')
            logger.info(f"Original: '{query}' -> Rewritten: '{rewritten}'")
            return rewritten
        except Exception as e:
            logger.warning(f"Query rewrite failed: {e}. Using original query.")
            return query
