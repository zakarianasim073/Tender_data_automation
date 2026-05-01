"""Local browser dashboard for the Tender Document Automation Engine."""

from __future__ import annotations

import json
import pathlib
import shutil
from typing import Any, Iterable

try:
    import gradio as gr
except ImportError:
    gr = None

BASE = pathlib.Path(__file__).resolve().parent
ENGINE = BASE / "tender_engine"
INPUT_DIR = ENGINE / "input"
OUTPUT_DIR = ENGINE / "output"

from tender_engine.enhanced_runner import create_batch_script, generate_tender
from tender_engine.checker import suggest_for_tender
from tender_engine.parser import build_pdf_lookup, lookup_pdf_text
from tender_engine.local_features import (
    build_search_index,
    compare_tenders,
    detect_duplicates,
    export_review_markdown,
    kanban_board,
    list_cached_tenders,
    load_approval,
    load_cache,
    save_approval,
    scan_required_documents,
    search_tenders,
)
from tender_engine.sor.sor_uploads import active_sor_paths, save_uploaded_sor
from tender_engine.ai import (
    BOQCostModelError,
    model_status,
    predict_tender_costs,
    train_model_from_csv,
    train_model_from_outputs,
)


APP_CSS = """
.gradio-container {max-width: 1460px !important;}
#app-hero {padding: 16px 18px; border: 1px solid #d9e2ec; border-radius: 8px; background: #f8fafc;}
#app-hero h1 {margin: 0 0 4px 0; font-size: 24px; letter-spacing: 0;}
#app-hero p {margin: 0; color: #4b5563;}
.metric-card {border: 1px solid #e5e7eb; border-radius: 8px; padding: 10px; background: white;}
"""

DEFAULT_CONTEXT = {
    "_info": "Editable tender-specific values. These override auto-extracted PDF data.",
    "tender_id": "",
    "zone": "A",
    "firm_name": "M/S Hassan & Brothers",
    "firm_address": "Mahmud Tower (9th Floor) 19, Siddique Bazar North South Road, Bongshal, Dhaka",
    "proprietor_name": "Mahmudul Hassan",
    "egp_email": "info@handbl.com",
    "bank_name": "SBAC Bank Limited",
    "bank_branch": "Gulshan Branch, Dhaka, Bangladesh",
    "memo_no": "HB/____",
    "bank_guarantee_no": "",
    "is_jv": False,
    "jv_name": "",
    "jv_date": "",
    "jv_partner_count": 0,
    "jv_share_text": "",
    "jv_office_address": "",
    "jv_phone": "",
    "lead_partner": "",
    "nominated_partner": "",
    "partner_in_charge_name": "",
    "partner_in_charge_firm": "",
    "partner1_code": "",
    "partner1_firm_name": "",
    "partner1_legal_type": "",
    "partner1_address": "",
    "partner1_signatory_name": "",
    "partner1_position": "",
    "partner1_share_percent": 0,
    "partner1_share_words": "",
    "partner2_code": "",
    "partner2_firm_name": "",
    "partner2_legal_type": "",
    "partner2_address": "",
    "partner2_signatory_name": "",
    "partner2_position": "",
    "partner2_share_percent": 0,
    "partner2_share_words": "",
    "partner3_code": "",
    "partner3_firm_name": "",
    "partner3_legal_type": "",
    "partner3_address": "",
    "partner3_signatory_name": "",
    "partner3_position": "",
    "partner3_share_percent": 0,
    "partner3_share_words": "",
    "work_months": ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun"],
    "generate_docs": {
        "bg_hb": True,
        "bg_credit_line": True,
        "equipment_decl": True,
        "manpower_decl": True,
        "methodology": True,
        "work_plan": True,
        "boq_excel": True,
        "rate_check": True,
        "summary": True,
        "jv_deed": False,
        "jv_poa": False,
    },
}


def _json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def _file_paths(files: Iterable[Any] | None) -> list[str]:
    paths = []
    for file in files or []:
        if isinstance(file, str):
            paths.append(file)
            continue
        name = getattr(file, "name", None) or getattr(file, "path", None)
        if name:
            paths.append(str(name))
    return paths


def _tender_id(value: str) -> str:
    return (value or "").strip()


def tender_input_dir(tender_id: str) -> pathlib.Path:
    return INPUT_DIR / _tender_id(tender_id)


def tender_output_dir(tender_id: str) -> pathlib.Path:
    return OUTPUT_DIR / _tender_id(tender_id)


def context_path(tender_id: str) -> pathlib.Path:
    return tender_input_dir(tender_id) / "context.json"


def create_tender_folder(tender_id: str) -> str:
    tender_id = _tender_id(tender_id)
    if not tender_id:
        return "Tender ID is required."
    folder = tender_input_dir(tender_id)
    folder.mkdir(parents=True, exist_ok=True)
    ctx_path = context_path(tender_id)
    if not ctx_path.exists():
        ctx = dict(DEFAULT_CONTEXT)
        ctx["tender_id"] = tender_id
        ctx_path.write_text(_json(ctx), encoding="utf-8")
    return f"Created local tender folder: {folder}"


def upload_tender_documents(tender_id: str, files: list[Any] | None) -> str:
    tender_id = _tender_id(tender_id)
    if not tender_id:
        return "Tender ID is required before upload."
    paths = _file_paths(files)
    if not paths:
        return "No files selected."
    folder = tender_input_dir(tender_id)
    folder.mkdir(parents=True, exist_ok=True)
    copied = []
    for path in paths:
        src = pathlib.Path(path)
        if not src.exists():
            continue
        dest = folder / src.name
        shutil.copy2(src, dest)
        copied.append(dest.name)
    if not context_path(tender_id).exists():
        create_tender_folder(tender_id)
    return "Uploaded: " + ", ".join(copied)


def upload_sor_schedule(source: str, file: Any) -> str:
    paths = _file_paths([file])
    if not paths:
        return "Select a SOR PDF first."
    try:
        result = save_uploaded_sor(paths[0], source)
        return _json(result)
    except Exception as exc:
        return _json({"error": str(exc)})


def show_active_sor() -> str:
    return _json(active_sor_paths())


def load_context(tender_id: str) -> str:
    tender_id = _tender_id(tender_id)
    if not tender_id:
        return _json({"error": "Tender ID is required."})
    path = context_path(tender_id)
    if not path.exists():
        create_tender_folder(tender_id)
    return path.read_text(encoding="utf-8")


def save_context(tender_id: str, content: str) -> str:
    tender_id = _tender_id(tender_id)
    if not tender_id:
        return "Tender ID is required."
    try:
        parsed = json.loads(content or "{}")
    except json.JSONDecodeError as exc:
        return f"Invalid JSON: {exc}"
    path = context_path(tender_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json(parsed), encoding="utf-8")
    return f"Saved context: {path}"


def list_tenders() -> list[list[Any]]:
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ids = sorted({p.name for p in INPUT_DIR.iterdir() if p.is_dir()} | {p.name for p in OUTPUT_DIR.iterdir() if p.is_dir()})
    rows = []
    for tender_id in ids:
        in_dir = tender_input_dir(tender_id)
        out_dir = tender_output_dir(tender_id)
        rows.append([
            tender_id,
            in_dir.exists(),
            len(list(in_dir.glob("*.pdf"))) if in_dir.exists() else 0,
            out_dir.exists(),
            len([p for p in out_dir.iterdir() if p.is_file()]) if out_dir.exists() else 0,
            str(in_dir),
            str(out_dir),
        ])
    return rows


def dashboard_kpis() -> list[list[Any]]:
    tenders = list_tenders()
    approved = 0
    generated = 0
    rate_reports = 0
    prediction_reports = 0
    for row in tenders:
        tender_id = row[0]
        if row[4] > 0:
            generated += 1
        if (tender_output_dir(tender_id) / f"Summary-{tender_id}.json").exists():
            rate_reports += 1
        if (tender_output_dir(tender_id) / f"AI_Cost_Prediction-{tender_id}.json").exists():
            prediction_reports += 1
        approval_file = tender_input_dir(tender_id) / "approval.json"
        if approval_file.exists():
            try:
                data = json.loads(approval_file.read_text(encoding="utf-8"))
                if data.get("status") == "Approved":
                    approved += 1
            except Exception:
                pass
    return [
        ["Total tenders", len(tenders)],
        ["Generated tenders", generated],
        ["Rate-check reports", rate_reports],
        ["AI prediction reports", prediction_reports],
        ["Approved tenders", approved],
    ]


def generate_local_tender(tender_id: str, run_rate_check: bool) -> str:
    tender_id = _tender_id(tender_id)
    if not tender_id:
        return _json({"error": "Tender ID is required."})
    try:
        result = generate_tender(tender_id, run_rate_check=run_rate_check)
        return _json(result)
    except Exception as exc:
        return _json({"error": str(exc)})


def get_output_files(tender_id: str) -> list[str]:
    tender_id = _tender_id(tender_id)
    folder = tender_output_dir(tender_id)
    if not tender_id or not folder.exists():
        return []
    return [str(p) for p in sorted(folder.iterdir()) if p.is_file()]


def make_batch(tender_id: str) -> str:
    tender_id = _tender_id(tender_id)
    if not tender_id:
        return "Tender ID is required."
    try:
        return create_batch_script(tender_id)
    except Exception as exc:
        return str(exc)


def run_checklist(tender_id: str) -> str:
    tender_id = _tender_id(tender_id)
    if not tender_id:
        return _json({"error": "Tender ID is required."})
    return _json(scan_required_documents(str(tender_input_dir(tender_id))))


def run_search(query: str) -> list[list[Any]]:
    query = (query or "").strip()
    if not query:
        return []
    build_search_index()
    return [[r["tender_id"], r["file"], r["score"], r["snippet"]] for r in search_tenders(query)]


def run_pdf_lookup(tender_id: str, query: str) -> list[list[Any]]:
    tender_id = _tender_id(tender_id)
    if not tender_id or not query:
        return []
    build_pdf_lookup(tender_id)
    rows = lookup_pdf_text(tender_id, query, limit=25)
    return [[r["pdf_file"], r["page"], r["score"], r["snippet"]] for r in rows]


def run_duplicates(tender_id: str) -> str:
    tender_id = _tender_id(tender_id)
    if not tender_id:
        return _json({"error": "Tender ID is required."})
    return _json(detect_duplicates(tender_id))


def run_compare(left_id: str, right_id: str) -> str:
    left_id = _tender_id(left_id)
    right_id = _tender_id(right_id)
    if not left_id or not right_id:
        return _json({"error": "Both tender IDs are required."})
    return _json(compare_tenders(left_id, right_id))


def approval_view(tender_id: str) -> str:
    tender_id = _tender_id(tender_id)
    if not tender_id:
        return _json({"error": "Tender ID is required."})
    return _json(load_approval(tender_id))


def approval_update(tender_id: str, status: str, note: str) -> str:
    tender_id = _tender_id(tender_id)
    if not tender_id:
        return _json({"error": "Tender ID is required."})
    return _json(save_approval(tender_id, status, note or ""))


def approval_board() -> str:
    return _json(kanban_board())


def make_review(tender_id: str) -> str | None:
    tender_id = _tender_id(tender_id)
    if not tender_id:
        return None
    return export_review_markdown(tender_id)


def train_ai_history() -> str:
    try:
        return _json(train_model_from_outputs(OUTPUT_DIR))
    except Exception as exc:
        return _json({"error": str(exc), "status": model_status()})


def train_ai_csv(file: Any) -> str:
    paths = _file_paths([file])
    if not paths:
        return _json({"error": "Select a CSV file first."})
    try:
        return _json(train_model_from_csv(paths[0]))
    except Exception as exc:
        return _json({"error": str(exc)})


def ai_status() -> str:
    return _json(model_status())


def predict_ai_cost(tender_id: str) -> str:
    tender_id = _tender_id(tender_id)
    if not tender_id:
        return _json({"error": "Tender ID is required."})
    try:
        result = predict_tender_costs(tender_id, OUTPUT_DIR)
        return _json(result)
    except Exception as exc:
        return _json({"error": str(exc), "status": model_status()})


def quick_generate_from_uploads(tender_id: str, files: list[Any] | None, context_text: str, run_rate_check: bool):
    tender_id = _tender_id(tender_id)
    if not tender_id:
        return _json({"error": "Tender ID is required."}), [], []
    create_tender_folder(tender_id)
    if files:
        upload_tender_documents(tender_id, files)
    if context_text and context_text.strip():
        save_context(tender_id, context_text)
    result = generate_local_tender(tender_id, run_rate_check)
    return result, get_output_files(tender_id), list_tenders()


def load_extracted_boq(tender_id: str) -> list[list[Any]]:
    tender_id = _tender_id(tender_id)
    path = tender_output_dir(tender_id) / "extracted_data.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for item in data.get("boq_items", []):
        rows.append([
            item.get("item_no"), item.get("item_code"), item.get("description"),
            item.get("unit"), item.get("quantity"), item.get("bwdb_rate"),
            item.get("quoted_rate"), item.get("quoted_amount"),
        ])
    return rows


def load_rate_summary_text(tender_id: str) -> str:
    tender_id = _tender_id(tender_id)
    folder = tender_output_dir(tender_id)
    for name in [f"Rate_Check_Summary-{tender_id}.txt", f"Summary-{tender_id}.txt"]:
        path = folder / name
        if path.exists():
            return path.read_text(encoding="utf-8", errors="ignore")
    return "Generate the tender with rate check first."


def run_sor_suggestions(tender_id: str, source: str):
    tender_id = _tender_id(tender_id)
    if not tender_id:
        return [], _json({"error": "Tender ID is required."}), []
    try:
        payload = suggest_for_tender(tender_id, source=source)
        rows = [[
            r["item_no"], r["boq_code"], r["boq_description"], r["boq_unit"],
            r["suggested_code"], r["suggested_description"], r["suggested_unit"],
            r["sor_rate"], r["confidence"], r["status"],
        ] for r in payload.get("rows", [])]
        files = [payload.get("excel_path"), str(tender_output_dir(tender_id) / f"SOR_Suggestions-{tender_id}.json")]
        return rows, _json(payload), [f for f in files if f]
    except Exception as exc:
        return [], _json({"error": str(exc)}), []


def cached_tender_rows() -> list[list[Any]]:
    return [[row.get("tender_id"), row.get("saved_at")] for row in list_cached_tenders()]


def build_app() -> gr.Blocks:
    theme = gr.themes.Soft(primary_hue="blue", neutral_hue="slate")
    with gr.Blocks(title="Tender Automation Local", theme=theme, css=APP_CSS) as app:
        gr.Markdown(
            "<div id='app-hero'><h1>Tender Automation Local Console</h1>"
            "<p>PDF intake, DOCX/Excel generation, SOR rate review, document checklist, approval flow, search, comparison, and local AI cost prediction.</p></div>"
        )

        with gr.Tab("Dashboard"):
            refresh_btn = gr.Button("Refresh")
            kpi_table = gr.Dataframe(headers=["Metric", "Value"], interactive=False)
            tender_table = gr.Dataframe(
                headers=["Tender ID", "Input Folder", "PDF Count", "Output Folder", "Output Files", "Input Path", "Output Path"],
                interactive=False,
            )
            refresh_btn.click(dashboard_kpis, outputs=kpi_table)
            refresh_btn.click(list_tenders, outputs=tender_table)
            app.load(dashboard_kpis, outputs=kpi_table)
            app.load(list_tenders, outputs=tender_table)

        with gr.Tab("Operations Console"):
            gr.Markdown("Upload the tender PDFs, edit context values if needed, then generate the complete package in one run.")
            op_tender_id = gr.Textbox(label="Tender ID", placeholder="Example: 541339")
            op_files = gr.File(label="Notice, TDS and BOQ PDFs", file_count="multiple")
            op_context = gr.Code(label="Context overrides JSON", language="json", value=_json(DEFAULT_CONTEXT), lines=18)
            op_rate = gr.Checkbox(label="Run SOR rate check after generation", value=True)
            op_btn = gr.Button("Generate Complete Tender Package", variant="primary")
            op_result = gr.Code(label="Run result", language="json", lines=18)
            op_downloads = gr.File(label="Generated output files", file_count="multiple")
            op_table = gr.Dataframe(
                headers=["Tender ID", "Input Folder", "PDF Count", "Output Folder", "Output Files", "Input Path", "Output Path"],
                interactive=False,
            )
            op_btn.click(
                quick_generate_from_uploads,
                inputs=[op_tender_id, op_files, op_context, op_rate],
                outputs=[op_result, op_downloads, op_table],
            )

        with gr.Tab("Create / Upload"):
            tender_id = gr.Textbox(label="Tender ID")
            create_btn = gr.Button("Create Tender Folder")
            create_msg = gr.Textbox(label="Status")
            tender_files = gr.File(label="Upload Notice, TDS, BOQ PDFs", file_count="multiple")
            upload_btn = gr.Button("Upload Tender Documents")
            upload_msg = gr.Textbox(label="Upload Result")
            create_btn.click(create_tender_folder, inputs=tender_id, outputs=create_msg)
            upload_btn.click(upload_tender_documents, inputs=[tender_id, tender_files], outputs=upload_msg)

        with gr.Tab("SOR Upload"):
            gr.Markdown("Upload BWDB or LGED Schedule of Rates PDF. The active path is saved locally in firm_config.json.")
            sor_source = gr.Radio(["BWDB", "LGED"], label="SOR Source", value="BWDB")
            sor_file = gr.File(label="SOR Rate Schedule PDF")
            sor_upload_btn = gr.Button("Save SOR Schedule")
            sor_show_btn = gr.Button("Show Active SOR Paths")
            sor_result = gr.Code(label="SOR Status", language="json")
            sor_upload_btn.click(upload_sor_schedule, inputs=[sor_source, sor_file], outputs=sor_result)
            sor_show_btn.click(show_active_sor, outputs=sor_result)
            app.load(show_active_sor, outputs=sor_result)

        with gr.Tab("Context Editor"):
            ctx_tender_id = gr.Textbox(label="Tender ID")
            load_ctx_btn = gr.Button("Load Context")
            ctx_code = gr.Code(label="context.json", language="json", lines=22)
            save_ctx_btn = gr.Button("Save Context")
            save_ctx_msg = gr.Textbox(label="Status")
            load_ctx_btn.click(load_context, inputs=ctx_tender_id, outputs=ctx_code)
            save_ctx_btn.click(save_context, inputs=[ctx_tender_id, ctx_code], outputs=save_ctx_msg)

        with gr.Tab("Generate"):
            gen_tender_id = gr.Textbox(label="Tender ID")
            gen_rate = gr.Checkbox(label="Run SOR rate check", value=True)
            gen_btn = gr.Button("Generate DOCX and Excel Package")
            gen_result = gr.Code(label="Generation Result", language="json")
            gen_files_btn = gr.Button("Show Output Files")
            gen_files = gr.File(label="Generated files", file_count="multiple")
            gen_btn.click(generate_local_tender, inputs=[gen_tender_id, gen_rate], outputs=gen_result)
            gen_files_btn.click(get_output_files, inputs=gen_tender_id, outputs=gen_files)

        with gr.Tab("BOQ & Rate Review"):
            review_tender_id = gr.Textbox(label="Tender ID")
            review_load_btn = gr.Button("Load Extracted BOQ and Rate Summary")
            boq_grid = gr.Dataframe(
                headers=["Item", "Code", "Description", "Unit", "Qty", "BWDB Rate", "Quoted Rate", "Quoted Amount"],
                interactive=False,
                wrap=True,
            )
            rate_text = gr.Textbox(label="Rate-check summary", lines=16)
            review_load_btn.click(load_extracted_boq, inputs=review_tender_id, outputs=boq_grid)
            review_load_btn.click(load_rate_summary_text, inputs=review_tender_id, outputs=rate_text)

        with gr.Tab("SOR Suggestions"):
            sugg_tender_id = gr.Textbox(label="Tender ID")
            sugg_source = gr.Radio(["BWDB", "LGED"], label="SOR source", value="BWDB")
            sugg_btn = gr.Button("Suggest SOR Matches From Descriptions", variant="primary")
            sugg_grid = gr.Dataframe(
                headers=["Item", "BOQ Code", "BOQ Description", "BOQ Unit", "SOR Code", "SOR Description", "SOR Unit", "SOR Rate", "Confidence", "Status"],
                interactive=False,
                wrap=True,
            )
            sugg_json = gr.Code(label="Suggestion result", language="json", lines=14)
            sugg_files = gr.File(label="Suggestion exports", file_count="multiple")
            sugg_btn.click(run_sor_suggestions, inputs=[sugg_tender_id, sugg_source], outputs=[sugg_grid, sugg_json, sugg_files])

        with gr.Tab("AI Cost Prediction"):
            gr.Markdown("Train the local BOQ prediction model from previous generated tenders, or upload a historical CSV with columns: category, region, unit_type, month, year, rate.")
            ai_status_btn = gr.Button("Show Model Status")
            train_hist_btn = gr.Button("Train From Generated Tender History")
            hist_csv = gr.File(label="Optional Historical CSV")
            train_csv_btn = gr.Button("Train From CSV")
            ai_tender_id = gr.Textbox(label="Tender ID to Predict")
            predict_btn = gr.Button("Predict BOQ Costs")
            ai_result = gr.Code(label="AI Cost Prediction Result", language="json", lines=20)
            ai_status_btn.click(ai_status, outputs=ai_result)
            train_hist_btn.click(train_ai_history, outputs=ai_result)
            train_csv_btn.click(train_ai_csv, inputs=hist_csv, outputs=ai_result)
            predict_btn.click(predict_ai_cost, inputs=ai_tender_id, outputs=ai_result)
            app.load(ai_status, outputs=ai_result)

        with gr.Tab("Checklist"):
            chk_tender_id = gr.Textbox(label="Tender ID")
            chk_btn = gr.Button("Scan Required Documents")
            chk_json = gr.Code(label="Missing Document Checklist", language="json")
            chk_btn.click(run_checklist, inputs=chk_tender_id, outputs=chk_json)

        with gr.Tab("Search"):
            search_query = gr.Textbox(label="Search historical tenders")
            search_btn = gr.Button("Search")
            search_results = gr.Dataframe(headers=["Tender ID", "File", "Score", "Snippet"], interactive=False)
            search_btn.click(run_search, inputs=search_query, outputs=search_results)

        with gr.Tab("PDF Lookup"):
            pdf_lookup_tender_id = gr.Textbox(label="Tender ID")
            pdf_lookup_query = gr.Textbox(label="Search inside source PDFs", placeholder="Example: tender security, package no, liquid assets")
            pdf_lookup_btn = gr.Button("Search Tender PDFs")
            pdf_lookup_results = gr.Dataframe(headers=["PDF", "Page", "Score", "Snippet"], interactive=False, wrap=True)
            pdf_lookup_btn.click(run_pdf_lookup, inputs=[pdf_lookup_tender_id, pdf_lookup_query], outputs=pdf_lookup_results)

        with gr.Tab("Compare / Duplicates"):
            dup_tender_id = gr.Textbox(label="Tender ID for duplicate check")
            dup_btn = gr.Button("Detect Similar Tenders")
            dup_json = gr.Code(label="Duplicate Candidates", language="json")
            dup_btn.click(run_duplicates, inputs=dup_tender_id, outputs=dup_json)
            left_id = gr.Textbox(label="Left Tender ID")
            right_id = gr.Textbox(label="Right Tender ID")
            cmp_btn = gr.Button("Compare Two Tenders")
            cmp_json = gr.Code(label="Comparison", language="json")
            cmp_btn.click(run_compare, inputs=[left_id, right_id], outputs=cmp_json)

        with gr.Tab("Approval"):
            app_tender_id = gr.Textbox(label="Tender ID")
            app_status = gr.Radio(["Draft", "Review", "Approved"], label="Status", value="Draft")
            app_note = gr.Textbox(label="Note")
            app_load = gr.Button("Load Approval")
            app_save = gr.Button("Save Approval")
            app_board_btn = gr.Button("Show Kanban Board")
            app_json = gr.Code(label="Approval Data", language="json")
            app_load.click(approval_view, inputs=app_tender_id, outputs=app_json)
            app_save.click(approval_update, inputs=[app_tender_id, app_status, app_note], outputs=app_json)
            app_board_btn.click(approval_board, outputs=app_json)

        with gr.Tab("Review Export"):
            rev_tender_id = gr.Textbox(label="Tender ID")
            rev_btn = gr.Button("Create Review Markdown")
            rev_file = gr.File(label="Review file")
            rev_btn.click(make_review, inputs=rev_tender_id, outputs=rev_file)

        with gr.Tab("Batch Runner"):
            b_tender_id = gr.Textbox(label="Tender ID")
            b_btn = gr.Button("Create batch_GEN_<tender_id>.py")
            b_msg = gr.Textbox(label="Status")
            b_btn.click(make_batch, inputs=b_tender_id, outputs=b_msg)

        with gr.Tab("Cache"):
            cache_refresh = gr.Button("Show Cached Tender Runs")
            cache_table = gr.Dataframe(headers=["Tender ID", "Saved At"], interactive=False)
            cache_id = gr.Textbox(label="Tender ID")
            cache_btn = gr.Button("Load Cached Status")
            cache_json = gr.Code(label="Cached status", language="json", lines=16)
            cache_refresh.click(cached_tender_rows, outputs=cache_table)
            cache_btn.click(lambda tid: _json(load_cache(_tender_id(tid)) or {"message": "No fresh cache found"}), inputs=cache_id, outputs=cache_json)
            app.load(cached_tender_rows, outputs=cache_table)

        with gr.Tab("Download Paths"):
            d_tender_id = gr.Textbox(label="Tender ID")
            d_btn = gr.Button("Show Output Files")
            d_files = gr.File(label="Output files", file_count="multiple")
            d_btn.click(get_output_files, inputs=d_tender_id, outputs=d_files)

    return app


if __name__ == "__main__":
    if gr is None or not hasattr(gr, "Blocks"):
        print("This dashboard needs Gradio 4.x or newer.")
        print("Install/upgrade local dependencies with:")
        print("  pip install -r requirements_engine.txt")
        raise SystemExit(1)
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    build_app().launch(server_name="127.0.0.1", server_port=7860)
