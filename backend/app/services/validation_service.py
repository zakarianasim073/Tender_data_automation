from typing import Dict

REQUIRED_KEYS = ["tender_id", "title", "closing_date", "opening_date"]


def validate_tender_payload(payload: dict) -> Dict:
    missing = [k for k in REQUIRED_KEYS if not payload.get(k)]
    score = max(0, 100 - len(missing) * 20)
    return {
        "valid": len(missing) == 0,
        "missing": missing,
        "submission_readiness_score": score,
    }
