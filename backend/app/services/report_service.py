def ai_risk_flags(validation, comparisons, contractor=None):
    flags = []
    if validation.get("submission_readiness_score", 0) < 80:
        flags.append("Low submission readiness")
    if comparisons.get("summary", {}).get("mismatches", 0) > 0:
        flags.append("BOQ mismatch risk")
    if contractor and contractor.get("blacklist_flag"):
        flags.append("Contractor risk flag")
    return flags


def submission_report(validation, comparisons, contractor=None):
    flags = ai_risk_flags(validation, comparisons, contractor)
    return {
        "ready_for_submission": validation.get("valid", False) and len(flags) == 0,
        "issues": validation.get("missing", []),
        "submission_readiness_score": validation.get("submission_readiness_score", 0),
        "boq_items": comparisons.get("summary", {}).get("items_checked", 0),
        "mismatches": comparisons.get("summary", {}).get("mismatches", 0),
        "ai_risk_flags": flags,
    }
