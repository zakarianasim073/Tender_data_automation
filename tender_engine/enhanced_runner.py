"""
Enhanced Tender Runner
----------------------
One high-level API for local use and the Gradio dashboard.

Rules:
  - input files live in:  tender_engine/input/<tender_id>/
  - output files go to:   tender_engine/output/<tender_id>/
  - each tender may have: tender_engine/input/<tender_id>/context.json
"""

from __future__ import annotations

import json
import pathlib
import shutil
from dataclasses import asdict
from typing import Dict, List, Optional

from .context import create_default_context, load_context, merge_context_into_firm_config, save_context
from .pipeline import run_pipeline
from .checker import check_rates, summary_to_dict
from .reports import generate_rate_check_excel, generate_summary_txt
from .sor import parse_bwdb_sor, parse_lged_sor, build_sor_lookup, detect_bwdb_zone
from .models import BOQItem
from .local_features import (
    scan_required_documents, save_checklist_report, save_cache,
    build_search_index, detect_duplicates, export_review_markdown,
)

BASE_DIR = pathlib.Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
TEMPLATE_DIR = BASE_DIR / "templates"

ROOT_DIR = BASE_DIR.parent


def ensure_tender_folders(tender_id: str) -> Dict[str, pathlib.Path]:
    """Create input/<tender_id> and output/<tender_id>."""
    in_dir = INPUT_DIR / tender_id
    out_dir = OUTPUT_DIR / tender_id
    in_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    ctx_path = in_dir / "context.json"
    if not ctx_path.exists():
        create_default_context(tender_id)
    return {"input": in_dir, "output": out_dir, "context": ctx_path}


def copy_uploaded_files(tender_id: str, file_paths: List[str]) -> List[str]:
    """Copy uploaded PDFs into input/<tender_id>."""
    folders = ensure_tender_folders(tender_id)
    copied = []
    for fp in file_paths or []:
        src = pathlib.Path(fp)
        if not src.exists():
            continue
        dst = folders["input"] / src.name
        shutil.copy2(src, dst)
        copied.append(dst.name)
    return copied


def generate_tender(tender_id: str, context_updates: Optional[dict] = None, run_rate_check: bool = True) -> dict:
    """
    Generate all documents for a tender.
    Returns a structured status dict for CLI and GUI.
    """
    folders = ensure_tender_folders(tender_id)

    ctx = load_context(tender_id)
    if context_updates:
        ctx.update({k: v for k, v in context_updates.items() if v is not None})
        save_context(tender_id, ctx)

    checklist = scan_required_documents(str(folders["input"]))
    if not checklist["ready_to_generate"]:
        return build_status(tender_id, extra={"error": "Missing critical documents", "checklist": checklist})

    firm_config = merge_context_into_firm_config(tender_id)

    output_folder = run_pipeline(
        input_folder=str(folders["input"]),
        template_folder=str(TEMPLATE_DIR),
        output_base=str(OUTPUT_DIR),
        firm_config=firm_config,
    )

    save_checklist_report(str(folders["input"]), str(folders["output"]))

    rate_summary = None
    if run_rate_check:
        try:
            rate_summary = run_rate_cross_check(tender_id)
        except Exception as exc:
            rate_summary = {"error": str(exc)}

    duplicate_matches = detect_duplicates(tender_id)
    review_report = export_review_markdown(tender_id)
    status = build_status(tender_id, extra={
        "rate_check": rate_summary,
        "duplicates": duplicate_matches,
        "review_report": review_report,
    })
    save_cache(tender_id, status)
    build_search_index()
    return status


def run_rate_cross_check(tender_id: str, sor_source: str = "BWDB") -> dict:
    """Create rate check Excel + text summary for an already generated tender."""
    folders = ensure_tender_folders(tender_id)
    data_path = folders["output"] / "extracted_data.json"
    if not data_path.exists():
        raise FileNotFoundError("Generate documents first; extracted_data.json is missing.")

    data = json.loads(data_path.read_text(encoding="utf-8"))
    ctx = load_context(tender_id)

    location = ctx.get("location") or data.get("location") or ""
    zone = (ctx.get("zone") or detect_bwdb_zone(location) or "A").upper()

    boq_items = [_boq_item_from_dict(x) for x in data.get("boq_items", [])]
    if not boq_items:
        raise ValueError("No BOQ items found in extracted_data.json.")

    firm = merge_context_into_firm_config(tender_id)
    if sor_source.upper() == "LGED":
        sor_pdf = firm.get("sor_pdf_lged") or str(ROOT_DIR.parent / "LGED Revised Rate Schedule,2023.pdf")
        sor_items = parse_lged_sor(sor_pdf)
    else:
        sor_pdf = firm.get("sor_pdf_bwdb") or str(ROOT_DIR.parent / "BWDB Revised Rate Schedule,2023.pdf")
        sor_items = parse_bwdb_sor(sor_pdf)

    lookup = build_sor_lookup(sor_items)
    summary = check_rates(boq_items, lookup, zone, tender_id)

    report_xlsx = folders["output"] / f"Rate_Check-{tender_id}.xlsx"
    report_txt = folders["output"] / f"Summary-{tender_id}.txt"
    generate_rate_check_excel(summary, str(report_xlsx))
    generate_summary_txt(summary, str(report_txt))

    summary_json = folders["output"] / f"Summary-{tender_id}.json"
    summary_json.write_text(json.dumps(summary_to_dict(summary), indent=2), encoding="utf-8")

    return summary_to_dict(summary)


def build_status(tender_id: str, extra: Optional[dict] = None) -> dict:
    folders = ensure_tender_folders(tender_id)
    input_files = sorted([p.name for p in folders["input"].glob("*") if p.is_file()])
    output_files = sorted([p.name for p in folders["output"].glob("*") if p.is_file()])
    result = {
        "tender_id": tender_id,
        "input_folder": str(folders["input"]),
        "output_folder": str(folders["output"]),
        "context_file": str(folders["context"]),
        "input_files": input_files,
        "output_files": output_files,
        "output_count": len(output_files),
    }
    if extra:
        result.update(extra)
    return result


def list_all_tender_statuses() -> List[dict]:
    if not INPUT_DIR.exists():
        return []
    ids = sorted([p.name for p in INPUT_DIR.iterdir() if p.is_dir()])
    return [build_status(tid) for tid in ids]


def create_batch_script(tender_id: str) -> pathlib.Path:
    """Create batch_GEN_<tender_id>.py at project root."""
    ensure_tender_folders(tender_id)
    script = ROOT_DIR / f"batch_GEN_{tender_id}.py"
    content = f'''"""Generate all tender files for Tender ID {tender_id}."""
import pathlib, sys
BASE = pathlib.Path(__file__).parent
sys.path.insert(0, str(BASE))

from tender_engine.enhanced_runner import generate_tender

if __name__ == "__main__":
    result = generate_tender("{tender_id}", run_rate_check=True)
    print("Generated Tender:", result["tender_id"])
    print("Output folder:", result["output_folder"])
    print("Files:")
    for name in result["output_files"]:
        print(" -", name)
'''
    script.write_text(content, encoding="utf-8")
    return script


def _boq_item_from_dict(d: dict) -> BOQItem:
    return BOQItem(
        item_no=int(d.get("item_no", 0)),
        item_code=str(d.get("item_code", "")),
        description=str(d.get("description", "")),
        quantity=float(d.get("quantity", 0) or 0),
        unit=str(d.get("unit", "")),
        bwdb_rate=float(d.get("bwdb_rate", 0) or 0),
        bwdb_amount=float(d.get("bwdb_amount", 0) or 0),
        quoted_rate=float(d.get("quoted_rate", 0) or d.get("bwdb_rate", 0) or 0),
        quoted_amount=float(d.get("quoted_amount", 0) or 0),
        percent_diff=float(d.get("percent_diff", 0) or 0),
    )
