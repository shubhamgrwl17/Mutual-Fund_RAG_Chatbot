from typing import Tuple

MAX_QUERY_LENGTH = 500

def validate_input(query: str) -> Tuple[bool, str]:
    """
    Validates the raw user input before processing.
    Returns: (is_valid, error_message)
    """
    if not query or query.strip() == "":
        return False, "Please enter a question about mutual funds."
    
    if len(query) > MAX_QUERY_LENGTH:
        return False, f"Please keep your question under {MAX_QUERY_LENGTH} characters."
    
    return True, ""
