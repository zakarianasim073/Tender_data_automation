import re
from app.utils.regex_patterns import EGPPatterns


def extract_tender_fields(text: str, language: str = "en") -> dict:
    out = {}
    patterns = EGPPatterns.PATTERNS_BN if language == "bn" else EGPPatterns.PATTERNS
    for key, pattern in patterns.items():
        m = re.search(pattern, text, flags=re.IGNORECASE)
        if m:
            out[key] = m.group(1).strip()
    return out
