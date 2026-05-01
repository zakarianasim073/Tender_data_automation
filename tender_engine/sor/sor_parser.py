"""
SOR Parser
----------
Parses BWDB/LGED Schedule of Rates PDFs into SORItem lists.

This version avoids pdfplumber table parsing for BWDB SOR because large scanned
rate tables can be slow or inconsistent. PyMuPDF text extraction is faster and
stable enough for item-code/rate matching.
"""

import json
import pathlib
import re
from typing import Dict, List, Optional
from .sor_models import SORItem

_CACHE_DIR = pathlib.Path(__file__).parent / "_cache"
_CODE_RE = re.compile(r"^\d{1,3}-\d{1,3}(?:-\d{1,3})?$")
_RATE_RE = re.compile(r"^\d{1,3}(?:,\d{3})*(?:\.\d+)?$|^\d+(?:\.\d+)?$")
_ZONE_RE = re.compile(r"Zone\s*[-]?\s*([ABCD])", re.IGNORECASE)
_UNIT_WORDS = {
    "sqm", "cum", "cum/km", "m", "no", "nos", "each", "kg", "km", "pmt",
    "pspc", "pltcum", "hr", "day", "job", "ltr", "pcs", "section"
}


def _cache_path(label: str) -> pathlib.Path:
    _CACHE_DIR.mkdir(exist_ok=True)
    return _CACHE_DIR / f"{label}.json"


def _load_cache(label: str) -> Optional[List[dict]]:
    p = _cache_path(label)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if data else None
    except json.JSONDecodeError:
        return None


def _save_cache(label: str, data: List[dict]):
    _cache_path(label).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_bwdb_sor(pdf_path: str) -> List[SORItem]:
    """Parse BWDB SOR PDF and return list of SORItem."""
    cache = _load_cache("bwdb_sor")
    if cache:
        return [SORItem(**d) for d in cache]

    items = _parse_bwdb_with_pymupdf(pdf_path)
    if not items:
        items = _parse_bwdb_with_pdfplumber(pdf_path)

    unique = _dedupe(items)
    _save_cache("bwdb_sor", [i.as_dict() for i in unique])
    print(f"  [SOR] BWDB: parsed {len(unique)} items")
    return unique


def parse_lged_sor(pdf_path: str) -> List[SORItem]:
    """Parse LGED SOR PDF. Kept simple; current project mainly uses BWDB."""
    cache = _load_cache("lged_sor")
    if cache:
        return [SORItem(**d) for d in cache]
    return []


def build_sor_lookup(items: List[SORItem]) -> Dict[str, SORItem]:
    """Build a dict with exact and relaxed keys for item-code lookup."""
    lookup = {}
    for item in items:
        for key in _code_keys(item.item_code):
            lookup.setdefault(key, item)
    return lookup


def _parse_bwdb_with_pymupdf(pdf_path: str) -> List[SORItem]:
    try:
        import fitz
    except ImportError:
        return []

    items: List[SORItem] = []
    doc = fitz.open(pdf_path)
    for page_index in range(len(doc)):
        text = doc[page_index].get_text() or ""
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        zone_order = _detect_zone_order(lines)
        chapter = _detect_chapter(lines)

        code_indexes = [idx for idx, value in enumerate(lines) if _CODE_RE.fullmatch(value)]
        for pos, i in enumerate(code_indexes):
            line = lines[i]
            code = _normalise_sor_code(line)
            prev_i = code_indexes[pos - 1] if pos > 0 else max(0, i - 45)
            next_i = code_indexes[pos + 1] if pos + 1 < len(code_indexes) else min(len(lines), i + 45)
            after_segment = lines[i:next_i]
            before_segment = lines[prev_i:i + 1]

            # BWDB SOR pages are inconsistent: some rows put item code before
            # description/rates, others put the item code after the rates.
            segment = after_segment if _count_rates(after_segment) >= 4 else before_segment
            rates = [_to_float(x) for x in segment if _is_rate(x)]
            if len(rates) < 4:
                continue
            rates = rates[-4:] if segment is before_segment else rates[:4]
            unit = _find_unit(segment)
            desc = _find_description_from_segment(segment, line)
            zone_rates = _assign_zone_rates(zone_order, rates)
            items.append(SORItem(
                item_code=code,
                description=desc,
                unit=unit,
                zone_a=zone_rates.get("A", 0.0),
                zone_b=zone_rates.get("B", 0.0),
                zone_c=zone_rates.get("C", 0.0),
                zone_d=zone_rates.get("D", 0.0),
                source="BWDB_2023",
                chapter=chapter,
                sl_no=str(len(items) + 1),
            ))
    doc.close()
    return items


def _parse_bwdb_with_pdfplumber(pdf_path: str) -> List[SORItem]:
    try:
        import pdfplumber
    except ImportError:
        return []
    items = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            zone_order = _detect_zone_order(lines)
            for i, line in enumerate(lines):
                if not _CODE_RE.fullmatch(line):
                    continue
                window = lines[i:i + 35]
                rates = [_to_float(x) for x in window if _is_rate(x)]
                if len(rates) < 4:
                    continue
                zone_rates = _assign_zone_rates(zone_order, rates[:4])
                items.append(SORItem(
                    item_code=_normalise_sor_code(line),
                    description=_find_description(lines, i),
                    unit=_find_unit(window),
                    zone_a=zone_rates.get("A", 0.0),
                    zone_b=zone_rates.get("B", 0.0),
                    zone_c=zone_rates.get("C", 0.0),
                    zone_d=zone_rates.get("D", 0.0),
                    source="BWDB_2023",
                    chapter=_detect_chapter(lines),
                    sl_no=str(len(items) + 1),
                ))
    return items


def _detect_zone_order(lines: List[str]) -> List[str]:
    head = "\n".join(lines[:60])
    zones = [m.group(1).upper() for m in _ZONE_RE.finditer(head)]
    zones = [z for z in zones if z in {"A", "B", "C", "D"}]
    if len(zones) >= 4:
        return zones[:4]
    return ["A", "B", "C", "D"]


def _assign_zone_rates(zone_order: List[str], rates: List[float]) -> Dict[str, float]:
    assigned = {}
    for zone, rate in zip(zone_order, rates):
        assigned[zone] = rate
    return assigned


def _detect_chapter(lines: List[str]) -> str:
    for line in lines[:80]:
        if re.fullmatch(r"\d{2,3}\.\s+.+", line):
            return line
    return ""


def _find_unit(window: List[str]) -> str:
    for value in window:
        v = value.strip().lower()
        if v in _UNIT_WORDS:
            return v
    return ""


def _find_description(lines: List[str], code_index: int) -> str:
    return _find_description_from_segment(lines[max(0, code_index - 18):code_index + 1], lines[code_index])


def _find_description_from_segment(segment: List[str], code: str) -> str:
    pieces = []
    for line in segment:
        low = line.lower()
        if line == code or _is_rate(line) or _CODE_RE.fullmatch(line) or low in _UNIT_WORDS:
            continue
        if re.fullmatch(r"\d+|\d+\(\s*\d+\s*\)", line):
            continue
        if "bwdb standard" in low or "item rate" in low or "sl. no" in low:
            continue
        if "zone" in low or "note:" in low:
            continue
        pieces.append(line)
    desc = " ".join(pieces[-12:]).strip()
    return re.sub(r"\s+", " ", desc)[:250]


def _count_rates(values: List[str]) -> int:
    return sum(1 for value in values if _is_rate(value))


def _is_rate(value: str) -> bool:
    return bool(_RATE_RE.fullmatch(str(value).replace(" ", ""))) and _to_float(value) > 0


def _to_float(value) -> float:
    try:
        return float(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return 0.0


def _normalise_sor_code(code: str) -> str:
    parts = [p for p in code.replace(" ", "").split("-") if p]
    if not parts:
        return code
    parts[0] = parts[0].zfill(2)
    if len(parts) == 2:
        parts.append("00")
    return "-".join(parts)


def _code_keys(code: str) -> List[str]:
    norm = _normalise_sor_code(code).lower()
    parts = norm.split("-")
    keys = {norm, norm.replace("-", "")}
    if len(parts) == 3 and parts[2] == "00":
        short = "-".join(parts[:2])
        keys.add(short)
        keys.add(short.replace("-", ""))
    if parts and parts[0].startswith("0"):
        no_zero = "-".join([parts[0].lstrip("0") or "0"] + parts[1:])
        keys.add(no_zero)
        keys.add(no_zero.replace("-", ""))
        if len(parts) == 3 and parts[2] == "00":
            short_no_zero = "-".join([parts[0].lstrip("0") or "0"] + parts[1:2])
            keys.add(short_no_zero)
            keys.add(short_no_zero.replace("-", ""))
    return list(keys)


def _dedupe(items: List[SORItem]) -> List[SORItem]:
    seen = set()
    unique = []
    for item in items:
        key = _normalise_sor_code(item.item_code)
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique
