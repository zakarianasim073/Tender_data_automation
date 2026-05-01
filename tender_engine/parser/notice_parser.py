"""
Notice Parser
-------------
Extracts core tender fields from e-GP Notice PDFs.
Handles both compact text PDFs and line-by-line browser print PDFs.
"""

import re
from .pdf_reader import read_pdf_text, clean_text


def parse_notice(pdf_path: str) -> dict:
    """Parse Notice PDF and return a dict of extracted fields."""
    raw = _read_text_fast(pdf_path)
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    flat = clean_text(raw)
    result = {}

    result["tender_id"] = _after_label(lines, "Tender/Proposal ID") or _regex(flat, r"Tender[/\s]*Proposal ID\s*[:\-]?\s*(\d+)")
    result["invitation_ref_no"] = _after_label(lines, "Invitation Reference No") or _regex(flat, r"Invitation Reference No\.?\s*[:\-]?\s*(.+?)(?:Tender/Proposal Status|App ID)")
    result["procuring_entity"] = _after_label(lines, "Procuring Entity Name") or _regex(flat, r"Procuring Entity Name\s*[:\-]?\s*(.+?)(?:Procuring Entity Code|$)")
    result["project_code"] = _after_label(lines, "Project Code") or _regex(flat, r"Project Code\s*[:\-]?\s*(\S+)")
    result["project_name"] = _collect_after(lines, "Project Name", ["Tender/Proposal Package No", "Tender/Proposal Package No. and"])

    package_no, work_name = _extract_package_and_work(lines)
    result["package_no"] = package_no
    result["work_name"] = work_name

    result["publication_date"] = _date_after_multiline_label(lines, "Scheduled Tender/Proposal Publication")
    result["closing_date"] = _date_after_multiline_label(lines, "Tender/Proposal Closing")
    result["document_fee_bdt"] = _extract_document_fee(lines) or 4000.0

    lot = _extract_lot_details(lines)
    result["location"] = lot.get("location", "")
    result["tender_security_amount"] = lot.get("tender_security_amount", 0.0)
    result["start_date"] = lot.get("start_date", "")
    result["completion_date"] = lot.get("completion_date", "")

    result["executive_engineer"] = _after_label(lines, "Name of Official Inviting") or ""
    result["pe_address"] = _extract_pe_address(lines)

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


def _after_label(lines: list, label: str) -> str:
    label_low = label.lower()
    for i, line in enumerate(lines):
        if label_low in line.lower():
            if ":" in line and line.split(":", 1)[1].strip():
                return line.split(":", 1)[1].strip()
            for j in range(i + 1, min(i + 5, len(lines))):
                if lines[j] != ":" and not lines[j].endswith(":"):
                    return lines[j].strip()
    return ""


def _collect_after(lines: list, label: str, stop_labels: list) -> str:
    start = None
    for i, line in enumerate(lines):
        if label.lower() in line.lower():
            start = i + 1
            break
    if start is None:
        return ""
    pieces = []
    for line in lines[start:]:
        if any(stop.lower() in line.lower() for stop in stop_labels):
            break
        if line != ":":
            pieces.append(line)
    return " ".join(pieces).strip()


def _extract_package_and_work(lines: list) -> tuple[str, str]:
    for i, line in enumerate(lines):
        if "description" in line.lower() and i > 0 and "package" in " ".join(lines[max(0, i-3):i+1]).lower():
            package_no = ""
            work_parts = []
            cursor = i + 1
            while cursor < len(lines) and lines[cursor] == ":":
                cursor += 1
            if cursor < len(lines):
                package_no = lines[cursor]
                cursor += 1
            while cursor < len(lines):
                current = lines[cursor]
                if current.lower().startswith("category"):
                    break
                work_parts.append(current)
                cursor += 1
            return package_no.strip(), " ".join(work_parts).strip()
    return "", ""


def _date_after_multiline_label(lines: list, label: str) -> str:
    label_low = label.lower()
    date_re = re.compile(r"\d{2}-[A-Za-z]{3}-\d{4}")
    for i, line in enumerate(lines):
        if label_low in line.lower():
            for j in range(i, min(i + 8, len(lines))):
                m = date_re.search(lines[j])
                if m:
                    return m.group(0)
    return ""


def _extract_document_fee(lines: list) -> float:
    for i, line in enumerate(lines):
        if "Tender/Proposal Document Price" in line:
            for j in range(i, min(i + 8, len(lines))):
                if re.fullmatch(r"\d+(?:\.\d+)?", lines[j]):
                    return float(lines[j])
    return 0.0


def _extract_lot_details(lines: list) -> dict:
    date_re = re.compile(r"\d{2}-[A-Za-z]{3}-\d{4}")
    for i in range(len(lines) - 3):
        if re.fullmatch(r"\d{5,}", lines[i]) and date_re.fullmatch(lines[i + 1]) and date_re.fullmatch(lines[i + 2]):
            location = lines[i - 1] if i > 0 else ""
            return {
                "location": location,
                "tender_security_amount": float(lines[i]),
                "start_date": lines[i + 1],
                "completion_date": lines[i + 2],
            }
    return {}


def _extract_pe_address(lines: list) -> str:
    for i, line in enumerate(lines):
        if line.strip().lower() == "address":
            if i + 1 < len(lines) and lines[i + 1].startswith(":"):
                return lines[i + 1].split(":", 1)[1].strip()
            if i + 2 < len(lines) and lines[i + 1] == ":":
                return lines[i + 2]
    return ""


def _regex(text: str, pattern: str) -> str:
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else ""
