"""
Text Utilities
--------------
Helpers for number-to-words, date formatting, amount formatting etc.
Used by generators to fill human-readable fields.
"""

import re
from datetime import datetime


# ── Number to Bangladeshi words ──────────────────────────────────────────────

_ONES = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
         "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen",
         "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
_TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]


def _below_hundred(n: int) -> str:
    if n < 20:
        return _ONES[n]
    return (_TENS[n // 10] + (" " + _ONES[n % 10] if n % 10 else "")).strip()


def _below_thousand(n: int) -> str:
    if n < 100:
        return _below_hundred(n)
    return (_ONES[n // 100] + " Hundred" + (" " + _below_hundred(n % 100) if n % 100 else "")).strip()


def amount_to_words_bd(amount: float) -> str:
    """
    Convert amount to Bangladeshi words using Crore/Lac/Thousand system.
    e.g. 7500000 -> "Seven Crore Fifty Lac"
    """
    n = int(round(amount))
    if n == 0:
        return "Zero"

    parts = []
    crore = n // 10_000_000
    n %= 10_000_000
    lac = n // 100_000
    n %= 100_000
    thousand = n // 1000
    n %= 1000

    if crore:
        parts.append(_below_thousand(crore) + " Crore")
    if lac:
        parts.append(_below_thousand(lac) + " Lac")
    if thousand:
        parts.append(_below_thousand(thousand) + " Thousand")
    if n:
        parts.append(_below_thousand(n))

    return " ".join(parts)


def format_bdt(amount: float) -> str:
    """Format as 'Tk. 75,00,000.00' (Bangladeshi comma grouping)."""
    n = int(round(amount))
    s = str(n)
    # BD style: last 3 digits, then groups of 2
    if len(s) > 3:
        result = s[-3:]
        s = s[:-3]
        while s:
            result = s[-2:] + "," + result
            s = s[:-2]
        return f"Tk. {result}.00"
    return f"Tk. {s}.00"


# ── Date helpers ──────────────────────────────────────────────────────────────

_MONTH_MAP = {
    "jan": "January", "feb": "February", "mar": "March", "apr": "April",
    "may": "May", "jun": "June", "jul": "July", "aug": "August",
    "sep": "September", "oct": "October", "nov": "November", "dec": "December",
}


def parse_date_flexible(date_str: str) -> datetime:
    """Try multiple date formats and return a datetime object."""
    formats = [
        "%d-%b-%Y", "%d-%B-%Y", "%d/%m/%Y", "%Y-%m-%d",
        "%d-%m-%Y", "%d.%m.%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {date_str!r}")


def date_to_long(date_str: str) -> str:
    """Convert '30-Jun-2022' to '30th June 2022'."""
    try:
        dt = parse_date_flexible(date_str)
        day = dt.day
        suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return f"{day}{suffix} {dt.strftime('%B %Y')}"
    except ValueError:
        return date_str


def date_to_document(date_str: str) -> str:
    """Convert '15-Apr-2021' to '15-04-2021'."""
    try:
        dt = parse_date_flexible(date_str)
        return dt.strftime("%d-%m-%Y")
    except ValueError:
        return date_str


def bg_validity_date(completion_date_str: str, extra_days: int = 150) -> str:
    """
    Bank Guarantee validity = completion date + ~150 days (28 days after tender validity).
    Returns formatted date like '24-August-2021'.
    """
    try:
        dt = parse_date_flexible(completion_date_str)
        from datetime import timedelta
        dt2 = dt + timedelta(days=extra_days)
        return f"{dt2.day}-{dt2.strftime('%B')}-{dt2.year}"
    except ValueError:
        return ""


# ── String helpers ────────────────────────────────────────────────────────────

def work_period_label(start: str, end: str) -> str:
    """e.g. '15-Apr-2021 to 30-Jun-2022'"""
    return f"{start}\nto \n{end}\n"


def tender_id_label(tender_id: str) -> str:
    return f"Tender ID: {tender_id}"
