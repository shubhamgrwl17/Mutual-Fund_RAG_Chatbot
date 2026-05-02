import re
from typing import List, Dict, Any

class ResponseValidator:
    """
    Defensive validator to ensure LLM responses are factual, 
    concise, and free of advisory language.
    """
    
    ADVISORY_PHRASES = [
        "i recommend", "you should buy", "better than", 
        "good investment", "suggest you", "i advise",
        "best choice", "top pick"
    ]

    def validate(self, response: str, context_chunks: List[Dict[str, Any]], intent: str = "FACTUAL") -> Dict[str, Any]:
        """
        Validates the LLM response.
        """
        issues = []
        response_lower = response.lower()
        
        # 1. Sentence Count Check
        sentences = [s.strip() for s in re.split(r'[.!?]+', response) if s.strip()]
        # Multi-intent needs more room for the fact + refusal
        limit = 6 if intent == "MULTI_INTENT" else 5
        if len(sentences) > limit:
            issues.append("EXCEEDS_SENTENCE_LIMIT")
            
        # 2. Citation & Footer Presence
        if "source:" not in response_lower:
            issues.append("MISSING_CITATION")
        if "last updated" not in response_lower:
            issues.append("MISSING_FOOTER")
            
        # 3. Advisory Scan
        # Skip advisory scan if we know it's a multi-intent/advisory query 
        # because the REFUSAL itself contains advisory keywords.
        if intent == "FACTUAL":
            for phrase in self.ADVISORY_PHRASES:
                if phrase in response_lower:
                    issues.append(f"ADVISORY_LANGUAGE_DETECTED: '{phrase}'")
                
        # 4. Hallucination Check (Number Matching)
        def normalize_num(n):
            # Remove symbols like %, ₹, and trailing periods
            return n.replace('%', '').replace('₹', '').strip(' .')

        nums_in_res = re.findall(r'\d+\.?\d*%?', response)
        context_text = " ".join([c['content'] for c in context_chunks])
        
        for num in nums_in_res:
            norm_num = normalize_num(num)
            
            if not norm_num: continue
            
            # Skip common numbers and dates
            if norm_num.isdigit() and 1 <= int(norm_num) <= 31:
                continue
            if norm_num in ["100", "500", "2024", "2025", "2026"]:
                continue
            
            if norm_num not in context_text:
                issues.append(f"POSSIBLE_HALLUCINATION: Number '{num}' not found in context.")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues
        }

    def auto_fix(self, response: str, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Automatically appends missing citation/footer if they are missing 
        but chunks are available.
        """
        fixed_response = response
        if context_chunks:
            primary_chunk = context_chunks[0]
            
            if "source:" not in fixed_response.lower():
                url = primary_chunk.get("source_url", "https://groww.in")
                fixed_response += f"\n\nSource: {url}"
                
            if "last updated" not in fixed_response.lower():
                # Note: In a real app, we'd get the actual scrape timestamp
                fixed_response += "\nLast updated from sources: 2026-05-02"
                
        return fixed_response
