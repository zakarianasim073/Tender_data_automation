"""Local duplicate detection and side-by-side tender comparison."""

from __future__ import annotations

import difflib
import json
import pathlib

BASE = pathlib.Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE / "output"


def _load_data(tender_id: str) -> dict:
    p = OUTPUT_DIR / tender_id / "extracted_data.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def compare_tenders(left_id: str, right_id: str) -> dict:
    left = _load_data(left_id)
    right = _load_data(right_id)
    keys = sorted(set(left.keys()) | set(right.keys()))
    rows = []
    for key in keys:
        if key in {"boq_items", "equipment", "manpower", "work_activities", "jv_partners"}:
            continue
        lv = left.get(key, "")
        rv = right.get(key, "")
        rows.append({"field": key, "left": lv, "right": rv, "same": lv == rv})
    return {"left_id": left_id, "right_id": right_id, "fields": rows}


def detect_duplicates(target_id: str, threshold: float = 0.82) -> list[dict]:
    target = _load_data(target_id)
    target_text = " ".join(str(target.get(k, "")) for k in ["work_name", "package_no", "location", "procuring_entity"])
    matches = []
    for folder in OUTPUT_DIR.glob("*"):
        if not folder.is_dir() or folder.name == target_id:
            continue
        other = _load_data(folder.name)
        other_text = " ".join(str(other.get(k, "")) for k in ["work_name", "package_no", "location", "procuring_entity"])
        score = difflib.SequenceMatcher(None, target_text.lower(), other_text.lower()).ratio()
        if score >= threshold:
            matches.append({"tender_id": folder.name, "similarity": round(score, 3), "work_name": other.get("work_name", "")})
    return sorted(matches, key=lambda r: r["similarity"], reverse=True)
