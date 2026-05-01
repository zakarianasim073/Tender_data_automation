"""Local missing-document checklist for a tender folder."""

from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, asdict

REQUIRED_DOCS = [
    {"key": "notice", "label": "Tender Notice PDF", "critical": True, "patterns": ["notice", "ift", "1."]},
    {"key": "tds_1", "label": "TDS Part 1 PDF", "critical": True, "patterns": ["tds_1", "tds1", "tds", "2."]},
    {"key": "tds_2", "label": "TDS Part 2 PDF", "critical": False, "patterns": ["tds_2", "tds2", "3."]},
    {"key": "boq", "label": "BOQ PDF", "critical": True, "patterns": ["boq", "4."]},
    {"key": "context", "label": "Editable context.json", "critical": True, "patterns": ["context.json"]},
]

@dataclass
class ChecklistItem:
    key: str
    label: str
    critical: bool
    found: bool
    matched_file: str = ""


def scan_required_documents(input_folder: str) -> dict:
    folder = pathlib.Path(input_folder)
    files = [p.name for p in folder.iterdir() if p.is_file()] if folder.exists() else []
    lowered = {name.lower(): name for name in files}
    items = []

    for spec in REQUIRED_DOCS:
        matched = ""
        for low, real in lowered.items():
            if any(pattern.lower() in low for pattern in spec["patterns"]):
                matched = real
                break
        items.append(ChecklistItem(spec["key"], spec["label"], spec["critical"], bool(matched), matched))

    missing_critical = [i.label for i in items if i.critical and not i.found]
    missing_optional = [i.label for i in items if not i.critical and not i.found]
    return {
        "input_folder": str(folder),
        "ready_to_generate": len(missing_critical) == 0,
        "missing_critical": missing_critical,
        "missing_optional": missing_optional,
        "items": [asdict(i) for i in items],
    }


def save_checklist_report(input_folder: str, output_folder: str) -> str:
    report = scan_required_documents(input_folder)
    out = pathlib.Path(output_folder) / "missing_document_checklist.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return str(out)
