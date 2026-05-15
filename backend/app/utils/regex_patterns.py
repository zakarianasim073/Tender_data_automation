class EGPPatterns:
    PATTERNS = {
        "tender_id": r"Tender\s*ID\s*[:\-]\s*(.+)",
        "closing_date": r"Closing\s*Date\s*[:\-]\s*(.+)",
        "opening_date": r"Opening\s*Date\s*[:\-]\s*(.+)",
    }
    PATTERNS_BN = {
        "tender_id": r"টেন্ডার\s*আইডি\s*[:\-]\s*(.+)",
        "closing_date": r"জমাদানের\s*শেষ\s*তারিখ\s*[:\-]\s*(.+)",
        "opening_date": r"খোলার\s*তারিখ\s*[:\-]\s*(.+)",
    }
