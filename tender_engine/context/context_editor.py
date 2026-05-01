"""Per-tender editable context management."""

import json
import pathlib

BASE = pathlib.Path(__file__).parent.parent


def get_context_path(tender_id: str) -> pathlib.Path:
    return BASE / "input" / str(tender_id) / "context.json"


def get_firm_config() -> dict:
    path = pathlib.Path(__file__).parent / "firm_config.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_context(tender_id: str) -> dict:
    path = get_context_path(tender_id)
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return create_default_context(tender_id)


def save_context(tender_id: str, data: dict) -> pathlib.Path:
    path = get_context_path(tender_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path


def _default_generate_docs() -> dict:
    return {
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
    }


def _default_work_months(firm: dict) -> list[str]:
    return firm.get("default_work_months", [
        "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    ])


def create_default_context(tender_id: str) -> dict:
    firm = get_firm_config()
    ctx = {
        "_info": "Edit these values before generation. They override PDF extraction.",
        "tender_id": str(tender_id),
        "zone": "A",
        "invitation_ref_no": "",
        "package_no": "",
        "work_name": "",
        "location": "",
        "procuring_entity": "",
        "executive_engineer": "",
        "pe_address": "",
        "start_date": "",
        "completion_date": "",
        "closing_date": "",
        "publication_date": "",
        "tender_security_amount": 0,
        "departmental_estimate": 0,
        "quoted_total": 0,
        "quoted_rate_percent": 0,
        "bg_date": "",
        "bg_validity_date": "",
        "bank_guarantee_no": "",
        "memo_no": firm.get("memo_no_prefix", "HB/") + "____",
        "document_date": "",
        "firm_name": firm.get("firm_name", ""),
        "firm_address": firm.get("firm_address", ""),
        "proprietor_name": firm.get("proprietor_name", ""),
        "egp_email": firm.get("egp_email", ""),
        "bank_name": firm.get("bank_name", ""),
        "bank_branch": firm.get("bank_branch", ""),
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
        "work_months": _default_work_months(firm),
        "generate_docs": _default_generate_docs(),
    }
    for idx in range(1, 4):
        ctx.update({
            f"partner{idx}_code": "",
            f"partner{idx}_firm_name": "",
            f"partner{idx}_legal_type": "",
            f"partner{idx}_address": "",
            f"partner{idx}_signatory_name": "",
            f"partner{idx}_position": "",
            f"partner{idx}_share_percent": 0,
            f"partner{idx}_share_words": "",
        })
    save_context(tender_id, ctx)
    return ctx


def merge_context_into_firm_config(tender_id: str) -> dict:
    return {**get_firm_config(), **load_context(tender_id)}


def list_tenders() -> list:
    folder = BASE / "input"
    if not folder.exists():
        return []
    return sorted(d.name for d in folder.iterdir() if d.is_dir())


def get_tender_status(tender_id: str) -> dict:
    input_dir = BASE / "input" / str(tender_id)
    output_dir = BASE / "output" / str(tender_id)
    context = get_context_path(str(tender_id))
    pdf_files = list(input_dir.glob("*.pdf")) if input_dir.exists() else []
    output_files = list(output_dir.iterdir()) if output_dir.exists() else []
    return {
        "tender_id": str(tender_id),
        "input_exists": input_dir.exists(),
        "pdf_count": len(pdf_files),
        "pdf_files": [p.name for p in pdf_files],
        "context_exists": context.exists(),
        "output_exists": output_dir.exists(),
        "output_files": [p.name for p in output_files],
        "output_count": len(output_files),
    }
