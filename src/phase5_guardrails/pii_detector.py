import re
from typing import Tuple

# Regex Patterns
PAN_PATTERN = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'
AADHAAR_PATTERN = r'\d{4}\s\d{4}\s\d{4}'
PHONE_PATTERN = r'(\+91[\-\s]?)?[0-9]{10}'
EMAIL_PATTERN = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

def contains_pii(text: str) -> Tuple[bool, str | None]:
    """
    Checks if the text contains Personally Identifiable Information (PII).
    Returns: (contains_pii, pii_type)
    """
    # 1. PAN Check
    if re.search(PAN_PATTERN, text):
        return True, "PAN Card Number"
    
    # 2. Aadhaar Check
    if re.search(AADHAAR_PATTERN, text):
        return True, "Aadhaar Number"
        
    # 3. Email Check
    if re.search(EMAIL_PATTERN, text):
        return True, "Email Address"
        
    # 4. Phone Check (with False-Positive protection)
    phone_match = re.search(PHONE_PATTERN, text)
    if phone_match:
        # Check if the "phone" is just a long number that might be a scheme_id
        # In our case, scheme_ids are around 6 digits, so 10 digits is likely a phone.
        match_text = phone_match.group(0)
        if len(re.sub(r'\D', '', match_text)) >= 10:
            return True, "Phone Number"

    return False, None
