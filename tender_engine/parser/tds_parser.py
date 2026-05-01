"""
TDS Parser
----------
Extracts qualification criteria, manpower, and equipment from e-GP TDS PDFs.
"""

import re
from typing import List
from .pdf_reader import read_pdf_text, clean_text
from ..models.tender_data import EquipmentItem, ManpowerItem


def parse_tds(pdf_path_1: str, pdf_path_2: str = None) -> dict:
    text1 = _read_text_fast(pdf_path_1)
    text2 = _read_text_fast(pdf_path_2) if pdf_path_2 else ""
    text = clean_text(text1 + " " + text2)
    lines = _clean_lines(text1 + "\n" + text2)

    result = {
        "general_exp_years": _int_match(text, r"general experience.*?shall be\s+(\d+)\s*\(" , 5),
        "specific_exp_value_lakh": _float_match(text, r"value of at least\s*Tk\.?\s*([\d,.]+)\s*lac", 0.0),
        "specific_exp_years": _int_match(text, r"within the last\s*(\d+)\s*\(", 5),
        "specific_exp_nature": _specific_nature(text),
        "liquid_assets_required_lakh": _float_match(text, r"liquid assets.*?Tk\s*([\d,.]+)\s*lac", 0.0),
        "annual_turnover_required_lakh": _float_match(text, r"annual construction turnover.*?Tk\s*([\d,.]+)\s*lac", 0.0),
        "tender_capacity_lakh": _float_match(text, r"minimum capacity shall be\s*Tk\s*([\d,.]+)\s*lac", 0.0),
    }

    manpower = _parse_manpower_lines(lines)
    equipment = _parse_equipment_lines(lines)
    result["manpower"] = manpower if manpower else _default_manpower()
    result["equipment"] = equipment if equipment else _default_equipment()
    return result


def _read_text_fast(pdf_path: str) -> str:
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text = "\n".join(page.get_text() or "" for page in doc)
        doc.close()
        return text
    except Exception:
        return read_pdf_text(pdf_path)


def _clean_lines(text: str) -> List[str]:
    return [ln.replace("\xa0", " ").strip() for ln in text.splitlines() if ln.replace("\xa0", " ").strip()]


def _parse_manpower_lines(lines: List[str]) -> List[ManpowerItem]:
    items = []
    try:
        start = next(i for i, line in enumerate(lines) if line.lower() == "position")
    except StopIteration:
        return []

    end = next((i for i in range(start, len(lines)) if "last login" in lines[i].lower()), min(start + 120, len(lines)))
    block = lines[start:end]
    i = 0
    while i < len(block):
        if not re.fullmatch(r"\d{1,2}", block[i]):
            i += 1
            continue
        sl_no = int(block[i])
        i += 1
        text_parts = []
        while i < len(block) and not re.fullmatch(r"\d+\s*Years?", block[i], re.IGNORECASE):
            if not _is_header_noise(block[i]):
                text_parts.append(block[i])
            i += 1
        if i >= len(block):
            break
        total_exp = block[i]
        similar_exp = block[i + 1] if i + 1 < len(block) and "year" in block[i + 1].lower() else ""
        i += 2

        combined = " ".join(text_parts).strip()
        post, qualification = _split_post_qualification(combined)
        nos = _extract_nos(combined)
        items.append(ManpowerItem(sl_no, post, qualification, nos, total_exp, similar_exp))
    return items


def _parse_equipment_lines(lines: List[str]) -> List[EquipmentItem]:
    starts = [i for i, line in enumerate(lines) if "equipment type and characteristics" in line.lower()]
    if not starts:
        return []
    start = starts[-1]
    end = next((i for i in range(start, len(lines)) if lines[i].startswith("19.") or "joint venture" in lines[i].lower()), len(lines))
    block = lines[start:end]
    items = []
    i = 0
    while i < len(block):
        if not re.fullmatch(r"\d{1,2}", block[i]):
            i += 1
            continue
        sl_no = int(block[i])
        i += 1
        desc_parts = []
        qty = ""
        while i < len(block):
            line = block[i]
            if re.fullmatch(r"\d{1,2}", line):
                break
            if "documentary evidence" in line.lower():
                break
            if _looks_like_equipment_qty(line):
                qty = line.strip()
                i += 1
                break
            if not _is_header_noise(line):
                desc_parts.append(line)
            i += 1
        desc = " ".join(desc_parts).strip()
        if desc:
            items.append(EquipmentItem(sl_no, desc, qty or "As required"))
    return items


def _looks_like_equipment_qty(line: str) -> bool:
    return bool(re.fullmatch(r"\d+\s*(nos?|sets?|each|no)\.?", line.strip(), re.IGNORECASE))


def _is_header_noise(line: str) -> bool:
    low = line.lower()
    return low in {"no", "position", "minimum number", "required", "works", "experience", "(years)"} or "equipment type" in low


def _split_post_qualification(text: str) -> tuple[str, str]:
    if ":" in text:
        post, rest = text.split(":", 1)
        qualification = re.sub(r"\([^)]*person[^)]*\)", "", rest, flags=re.IGNORECASE).strip()
        return post.strip(), qualification or "N/A"
    cleaned = re.sub(r"\([^)]*person[^)]*\)", "", text, flags=re.IGNORECASE).strip()
    return cleaned, "N/A"


def _extract_nos(text: str) -> str:
    m = re.search(r"\((\d+)\s*person\)", text, re.IGNORECASE)
    if m:
        n = m.group(1)
        return f"{n} Person"
    return "As required" if "as required" in text.lower() else "1 Person"


def _specific_nature(text: str) -> str:
    m = re.search(r"([A-Za-z,\s]+(?:Spur|Groyne|Revetment)[A-Za-z,\s.]+similar works)", text, re.IGNORECASE)
    return m.group(1).strip() if m else ""


def _int_match(text: str, pattern: str, default: int) -> int:
    m = re.search(pattern, text, re.IGNORECASE)
    return int(m.group(1)) if m else default


def _float_match(text: str, pattern: str, default: float) -> float:
    m = re.search(pattern, text, re.IGNORECASE)
    return float(m.group(1).replace(",", "")) if m else default


def _default_equipment() -> List[EquipmentItem]:
    return [
        EquipmentItem(1, "Mixture Machine", "6 nos"),
        EquipmentItem(2, "Concrete Vibrator", "8 nos"),
        EquipmentItem(3, "Nozzle -1.50 in", "12 nos"),
        EquipmentItem(4, "Water Measuring Instrument", "4 nos"),
        EquipmentItem(5, "Concrete Cylinder Mold", "9 nos"),
        EquipmentItem(6, "Slump Test Cone", "3 nos"),
        EquipmentItem(7, "Water Pump", "10 nos"),
        EquipmentItem(8, "Dump Truck", "1 no"),
        EquipmentItem(9, "Pay Loader", "1 no"),
        EquipmentItem(10, "Excavator", "2 nos"),
        EquipmentItem(11, "Power Driven Country Boat", "1 no"),
        EquipmentItem(12, "Generator, Minimum 20 kw capacity for site electrification", "3 sets"),
        EquipmentItem(13, "Leveling Instrument", "2 sets"),
        EquipmentItem(14, "Digital Camera", "1 no"),
        EquipmentItem(15, "Hand hold Geo-bag sewing machine (Double needle)", "6 nos"),
        EquipmentItem(16, "All others equipment required as and when necessary", "As required"),
    ]


def _default_manpower() -> List[ManpowerItem]:
    return [
        ManpowerItem(1, "Construction Project Manager", "Graduate", "1 Person", "7 Years", "3 Years"),
        ManpowerItem(2, "Project Engineer", "B.Sc Engineer (Civil)", "1 Person", "5 Years", "1 Years"),
        ManpowerItem(3, "Site Engineer", "Diploma in Civil", "1 Person", "3 Years", "1 Years"),
        ManpowerItem(4, "Surveyor", "Diploma in Surveying", "2 Person", "3 Years", "1 Years"),
        ManpowerItem(5, "Supervisor", "N/A", "6 Person", "3 Years", "1 Years"),
        ManpowerItem(6, "Other Manpower", "N/A", "As required", "", ""),
    ]
