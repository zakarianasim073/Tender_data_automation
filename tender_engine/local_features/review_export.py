"""Local review report export."""

from __future__ import annotations

import json
import pathlib
from datetime import datetime

BASE = pathlib.Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE / "output"


def export_review_markdown(tender_id: str) -> str:
    folder = OUTPUT_DIR / tender_id
    folder.mkdir(parents=True, exist_ok=True)
    data_path = folder / "extracted_data.json"
    summary_path = folder / f"Summary-{tender_id}.json"
    data = json.loads(data_path.read_text(encoding="utf-8")) if data_path.exists() else {}
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}

    lines = [
        f"# Tender Review Summary - {tender_id}",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Tender Data",
        f"- Package: {data.get('package_no', '')}",
        f"- Work: {data.get('work_name', '')}",
        f"- Location: {data.get('location', '')}",
        f"- Procuring Entity: {data.get('procuring_entity', '')}",
        f"- Tender Security: {data.get('tender_security_bdt', '')}",
        "",
        "## Rate Check",
        f"- Risk Level: {summary.get('risk_level', 'Not checked')}",
        f"- Match: {summary.get('match', 0)}",
        f"- Mismatch: {summary.get('mismatch', 0)}",
        f"- Missing: {summary.get('missing', 0)}",
        f"- Above SOR: {summary.get('above_sor', 0)}",
        f"- Below SOR: {summary.get('below_sor', 0)}",
        "",
        "## Generated Files",
    ]
    for file in sorted(folder.iterdir()):
        if file.is_file():
            lines.append(f"- {file.name}")
    out = folder / f"Review-{tender_id}.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return str(out)
