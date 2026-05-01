"""
BOQ Parser
----------
Extracts Bill of Quantities items from e-GP BOQ PDFs.

Important: e-GP BOQ PDFs usually do NOT contain quoted rates. They contain
item code, description, unit, and quantity, then the tenderer fills rates online.
So this parser extracts quantities and leaves rates as 0. Rate_Check later uses
SOR rates as the reference when quoted rates are not available.
"""

import re
from typing import List
from .pdf_reader import read_pdf_text, clean_text
from ..models.tender_data import BOQItem


UNIT_WORDS = {
    "sqm", "cum", "cum/km", "nos", "no", "each", "kg", "m", "meter",
    "pltcum", "pspc", "section", "job", "hr", "day", "ltr", "pcs"
}


def parse_boq(pdf_path: str) -> dict:
    """
    Parse BOQ PDF.
    Returns dict with keys: boq_items, departmental_estimate.
    """
    text = _read_text_fast(pdf_path)
    items = _extract_from_table_text(text)

    if not items:
        items = _extract_egp_items(text)

    if not items:
        text = clean_text(text)
        items = _extract_from_flat_text(text)

    return {
        "boq_items": items,
        "departmental_estimate": sum(i.bwdb_amount for i in items),
    }


def _read_text_fast(pdf_path: str) -> str:
    """Use PyMuPDF first because pdfplumber table extraction can hang on e-GP PDFs."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        parts = [page.get_text() or "" for page in doc]
        doc.close()
        return "\n".join(parts)
    except Exception:
        return read_pdf_text(pdf_path)


def _extract_from_table_text(text: str) -> List[BOQItem]:
    """Parse copied/exported BOQ table text with tab-separated columns.

    Handles rows like:
      1\t01\tLong description...\t3552818.781\tcum\t0\t0\t0\t-\t0\t0
    The description may contain quotes and punctuation, but tab boundaries keep
    quantity/unit/rates reliable.
    """
    items: List[BOQItem] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or "\t" not in line:
            continue

        columns = [col.strip() for col in line.split("\t")]
        if len(columns) < 5:
            continue
        if not _is_int(columns[0]) or not columns[1]:
            continue
        if not _is_number(columns[3]) or not _is_unit(columns[4]):
            continue

        item_no = int(columns[0])
        item_code = _normalise_boq_code(columns[1])
        description = _clean_description(columns[2])
        quantity = _to_float(columns[3])
        unit = columns[4].lower()
        bwdb_rate = _to_float(columns[5]) if len(columns) > 5 else 0.0
        bwdb_amount = _to_float(columns[6]) if len(columns) > 6 else quantity * bwdb_rate
        quoted_rate = _to_float(columns[7]) if len(columns) > 7 else 0.0
        quoted_amount = _to_float(columns[9]) if len(columns) > 9 else quantity * quoted_rate
        percent_diff = _to_float(columns[10]) if len(columns) > 10 else 0.0

        items.append(BOQItem(
            item_no=item_no,
            item_code=item_code,
            description=description,
            quantity=quantity,
            unit=unit,
            bwdb_rate=bwdb_rate,
            bwdb_amount=bwdb_amount,
            quoted_rate=quoted_rate,
            quoted_amount=quoted_amount,
            percent_diff=percent_diff,
        ))

    return _dedupe_items(items)


def _extract_egp_items(text: str) -> List[BOQItem]:
    """Parse e-GP line layout: item no, group, split item code, description, unit, quantity."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    items: List[BOQItem] = []
    i = 0

    while i < len(lines) - 5:
        if not _is_int(lines[i]):
            i += 1
            continue
        if lines[i + 1] != lines[i]:
            i += 1
            continue

        item_no = int(lines[i])
        cursor = i + 2
        code_parts = []

        while cursor < len(lines) and _looks_like_code_part(lines[cursor]):
            code_parts.append(lines[cursor])
            cursor += 1

        if not code_parts:
            i += 1
            continue

        item_code = _normalise_boq_code("".join(code_parts))
        desc_lines = []

        while cursor < len(lines):
            current = lines[cursor]
            if _is_unit(current):
                unit = current.lower()
                cursor += 1
                break
            if _looks_like_new_item(lines, cursor):
                unit = ""
                break
            desc_lines.append(current)
            cursor += 1
        else:
            break

        quantity = 0.0
        if cursor < len(lines) and _is_number(lines[cursor]):
            quantity = _to_float(lines[cursor])
            cursor += 1

        if quantity <= 0 or not item_code:
            i += 1
            continue

        description = " ".join(desc_lines).strip().strip('"')
        items.append(BOQItem(
            item_no=item_no,
            item_code=item_code,
            description=description,
            quantity=quantity,
            unit=unit,
            bwdb_rate=0.0,
            bwdb_amount=0.0,
            quoted_rate=0.0,
            quoted_amount=0.0,
            percent_diff=0.0,
        ))
        i = max(cursor, i + 1)

    return _dedupe_items(items)


def _extract_from_flat_text(text: str) -> List[BOQItem]:
    """Fallback for older PDFs where each BOQ item appears on one line."""
    items = []
    pattern = re.compile(
        r"(\d{1,3})\s+(\d{1,3})\s+((?:\d{1,3}-?){1,4}|MR)\s+(.+?)\s+"
        r"(sqm|cum/km|cum|nos|no|each|kg|m|pltcum|section)\s+([\d,]+\.?\d*)",
        re.IGNORECASE | re.DOTALL,
    )
    for m in pattern.finditer(text):
        item_no = int(m.group(1))
        items.append(BOQItem(
            item_no=item_no,
            item_code=_normalise_boq_code(m.group(3)),
            description=re.sub(r"\s+", " ", m.group(4)).strip(),
            quantity=_to_float(m.group(6)),
            unit=m.group(5).lower(),
            bwdb_rate=0.0,
            bwdb_amount=0.0,
            quoted_rate=0.0,
            quoted_amount=0.0,
            percent_diff=0.0,
        ))
    return _dedupe_items(items)


def _clean_description(value: str) -> str:
    value = value.replace("\n", " ").strip()
    value = re.sub(r"\s+", " ", value)
    return value.strip().strip('"')


def _normalise_boq_code(code: str) -> str:
    code = code.replace("\n", "").replace(" ", "").strip("-")
    if code.upper() == "MR":
        return "MR"
    parts = [p for p in code.split("-") if p]
    if not parts:
        return code
    if parts[0].isdigit():
        parts[0] = parts[0].zfill(2)
    if len(parts) == 2:
        return f"{parts[0]}-{parts[1]}"
    return "-".join(parts)


def _looks_like_code_part(value: str) -> bool:
    value = value.strip()
    return bool(re.fullmatch(r"MR|\d{1,3}-?", value, re.IGNORECASE))


def _looks_like_new_item(lines: list, idx: int) -> bool:
    return idx + 1 < len(lines) and _is_int(lines[idx]) and lines[idx + 1] == lines[idx]


def _is_unit(value: str) -> bool:
    return value.strip().lower() in UNIT_WORDS


def _is_int(value: str) -> bool:
    return bool(re.fullmatch(r"\d{1,3}", value.strip()))


def _is_number(value: str) -> bool:
    return bool(re.fullmatch(r"[\d,]+(?:\.\d+)?", value.strip()))


def _to_float(val) -> float:
    try:
        return float(str(val).replace(",", "").strip())
    except (ValueError, TypeError):
        return 0.0


def _dedupe_items(items: List[BOQItem]) -> List[BOQItem]:
    seen = set()
    result = []
    for item in items:
        key = item.item_no
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return sorted(result, key=lambda x: x.item_no)
