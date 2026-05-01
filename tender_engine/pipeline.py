"""PDF -> structured data -> DOCX/XLSX tender package pipeline."""

from __future__ import annotations

from pathlib import Path

from .checker.rate_checker import check_rates
from .generators import fill_docx_template, generate_boq_excel, generate_work_plan_excel
from .models import JVPartner, TenderData
from .parser import parse_boq, parse_notice, parse_tds
from .reports.report_generator import generate_rate_check_excel, generate_summary_txt
from .sor import active_sor_paths, build_sor_lookup, detect_bwdb_zone, parse_bwdb_sor
from .utils import amount_to_words_bd, date_to_document, date_to_long, ensure_output_folder, format_bdt, save_json, print_summary

DOCX_TEMPLATES = {
    "bg_hb": "BG_HB_template.docx",
    "bg_credit_line": "BG_Credit_Line_template.docx",
    "equipment_decl": "Equipment_Declaration_template.docx",
    "manpower_decl": "Manpower_Declaration_template.docx",
    "methodology": "Methodology_template.docx",
    "jv_deed": "JV_DEED_template.docx",
    "jv_poa": "JV_POA_template.docx",
}

OUTPUT_FILENAMES = {
    "bg_hb": "2. BG_HB-{tender_id}.docx",
    "bg_credit_line": "3. BG_Credit_Line-{tender_id}.docx",
    "equipment_decl": "4. Equipment_Declaration-{tender_id}.docx",
    "manpower_decl": "5. Manpower_Declaration-{tender_id}.docx",
    "methodology": "6. Methodology-{tender_id}.docx",
    "jv_deed": "JV_DEED-{jv_name}-{tender_id}.docx",
    "jv_poa": "JV_POA-{jv_name}-{tender_id}.docx",
}


def run_pipeline(input_folder: str, template_folder: str, output_base: str, firm_config: dict | None = None) -> Path:
    input_path = Path(input_folder)
    template_path = Path(template_folder)
    firm_config = firm_config or {}

    notice_pdf = _find_pdf(input_path, ["notice", "ift", "1."])
    tds1_pdf = _find_pdf(input_path, ["tds_1", "tds1", "2.tds", "2."])
    tds2_pdf = _find_pdf(input_path, ["tds_2", "tds2", "3.tds", "3."])
    boq_pdf = _find_pdf(input_path, ["boq", "4.boq", "4."])

    print(f"\n[PARSING] {input_path}")
    print(f"  Notice: {notice_pdf.name if notice_pdf else 'NOT FOUND'}")
    print(f"  TDS 1 : {tds1_pdf.name if tds1_pdf else 'NOT FOUND'}")
    print(f"  TDS 2 : {tds2_pdf.name if tds2_pdf else 'NOT FOUND'}")
    print(f"  BOQ   : {boq_pdf.name if boq_pdf else 'NOT FOUND'}")

    notice = parse_notice(str(notice_pdf)) if notice_pdf else {}
    tds = parse_tds(str(tds1_pdf or notice_pdf), str(tds2_pdf) if tds2_pdf else None) if (tds1_pdf or notice_pdf) else {}
    boq = parse_boq(str(boq_pdf)) if boq_pdf else {"boq_items": [], "departmental_estimate": 0}

    td = _build_tender_data(notice, tds, boq, firm_config)
    output_folder = ensure_output_folder(output_base, td.tender_id or "unknown")
    save_json(td, output_folder)
    generate_docs = firm_config.get("generate_docs", {}) or {}
    if _doc_enabled("boq_excel", generate_docs):
        generate_boq_excel(str(output_folder / f"BOQ-{td.tender_id}.xlsx"), td)
    if _doc_enabled("work_plan", generate_docs):
        generate_work_plan_excel(str(output_folder / f"7. Work_Plan-{td.tender_id}.xlsx"), td)
    if _doc_enabled("rate_check", generate_docs):
        _generate_rate_reports(td, output_folder)

    docx_dir = template_path / "docx"
    for key, template_name in DOCX_TEMPLATES.items():
        if not _doc_enabled(key, generate_docs):
            continue
        if key in {"jv_deed", "jv_poa"} and not td.is_jv:
            continue
        template_file = docx_dir / template_name
        if not template_file.exists():
            print(f"  [SKIP] Template missing: {template_name}")
            continue
        output_name = OUTPUT_FILENAMES[key].format(tender_id=td.tender_id, jv_name=td.jv_name or "JV")
        fill_docx_template(str(template_file), str(output_folder / output_name), td)

    print_summary(output_folder)
    return output_folder


def _doc_enabled(key: str, generate_docs: dict) -> bool:
    if not generate_docs:
        return True
    aliases = {
        "bg_hb": ["bg_hb", "bg_hb_sbac", "bg_hb-sinamm-ti"],
        "bg_credit_line": ["bg_credit_line", "bg_credit_line_hb", "bg_credit_line_HB"],
        "equipment_decl": ["equipment_decl", "equipment_declaration"],
        "manpower_decl": ["manpower_decl", "manpower_declaration"],
        "boq_excel": ["boq_excel", "boq"],
        "work_plan": ["work_plan"],
        "rate_check": ["rate_check"],
        "methodology": ["methodology"],
        "jv_deed": ["jv_deed"],
        "jv_poa": ["jv_poa"],
    }
    return any(bool(generate_docs.get(alias)) for alias in aliases.get(key, [key]))


def _generate_rate_reports(td: TenderData, output_folder: Path) -> None:
    try:
        bwdb_pdf = active_sor_paths().get("BWDB", "")
        sor_items = parse_bwdb_sor(str(bwdb_pdf or ""))
        if not sor_items:
            print("  [SKIP] No BWDB SOR data found.")
            return
        zone = detect_bwdb_zone(td.location or td.pe_division or td.procuring_entity)
        summary = check_rates(td.boq_items, build_sor_lookup(sor_items), zone, td.tender_id)
        generate_rate_check_excel(summary, str(output_folder / f"Rate_Check-{td.tender_id}.xlsx"))
        generate_summary_txt(summary, str(output_folder / f"Rate_Check_Summary-{td.tender_id}.txt"))
    except Exception as exc:
        print(f"  [SKIP] Rate check failed: {exc}")


def _build_tender_data(notice: dict, tds: dict, boq: dict, firm: dict) -> TenderData:
    tender_id = _first(firm, notice, "tender_id")
    start_date = _first(firm, notice, "start_date")
    completion_date = _first(firm, notice, "completion_date")
    tender_security = float(_first(firm, notice, "tender_security_amount", 0) or 0)
    quoted_pct = float(_first(firm, boq, "quoted_rate_percent", 0) or 0)
    dept_estimate = float(_first(firm, boq, "departmental_estimate", 0) or 0)
    quoted_total = float(_first(firm, boq, "quoted_total", 0) or 0) or dept_estimate * (1 + quoted_pct)
    work_name = _first(firm, notice, "work_name")
    partners = _partners_from_context(firm)

    return TenderData(
        tender_id=tender_id,
        invitation_ref_no=_first(firm, notice, "invitation_ref_no"),
        package_no=_first(firm, notice, "package_no"),
        project_code=_first(firm, notice, "project_code"),
        procuring_entity=_first(firm, notice, "procuring_entity"),
        procuring_entity_short=firm.get("procuring_entity_short", "BWDB"),
        executive_engineer=_first(firm, notice, "executive_engineer"),
        pe_address=_first(firm, notice, "pe_address"),
        pe_division=firm.get("pe_division") or _first(firm, notice, "procuring_entity"),
        work_name=work_name,
        work_name_short=work_name[:80] + "..." if len(work_name) > 80 else work_name,
        location=_first(firm, notice, "location"),
        project_name=_first(firm, notice, "project_name"),
        publication_date=_first(firm, notice, "publication_date"),
        closing_date=_first(firm, notice, "closing_date"),
        start_date=start_date,
        completion_date=completion_date,
        completion_date_long=date_to_long(completion_date) if completion_date else "",
        bg_validity_date=firm.get("bg_validity_date") or "",
        document_date=firm.get("document_date") or date_to_document(_first(firm, notice, "closing_date")),
        tender_security_amount=tender_security,
        tender_security_amount_words=amount_to_words_bd(tender_security),
        tender_security_bdt=format_bdt(tender_security),
        liquid_assets_required_lakh=float(tds.get("liquid_assets_required_lakh", 0) or 0),
        annual_turnover_required_lakh=float(tds.get("annual_turnover_required_lakh", 0) or 0),
        tender_capacity_lakh=float(tds.get("tender_capacity_lakh", 0) or 0),
        document_fee_bdt=float(_first(firm, notice, "document_fee_bdt", 4000) or 4000),
        quoted_rate_percent=quoted_pct,
        departmental_estimate=dept_estimate,
        quoted_total=quoted_total,
        general_exp_years=int(tds.get("general_exp_years", 5) or 5),
        specific_exp_contracts=int(firm.get("specific_exp_contracts", 1) or 1),
        specific_exp_value_lakh=float(tds.get("specific_exp_value_lakh", 0) or 0),
        specific_exp_years=int(tds.get("specific_exp_years", 5) or 5),
        specific_exp_nature=tds.get("specific_exp_nature", ""),
        bank_name=firm.get("bank_name", ""),
        bank_branch=firm.get("bank_branch", ""),
        bank_guarantee_no=firm.get("bank_guarantee_no", ""),
        bg_date=firm.get("bg_date") or date_to_document(_first(firm, notice, "closing_date")),
        firm_name=firm.get("firm_name", ""),
        firm_address=firm.get("firm_address", ""),
        proprietor_name=firm.get("proprietor_name", ""),
        egp_email=firm.get("egp_email", ""),
        memo_no=firm.get("memo_no", ""),
        is_jv=bool(firm.get("is_jv", False)),
        jv_name=firm.get("jv_name", ""),
        jv_date=firm.get("jv_date", ""),
        jv_partner_count=int(firm.get("jv_partner_count", firm.get("jb_partner", 0)) or 0),
        jv_share_text=firm.get("jv_share_text", firm.get("jv_share", "")),
        jv_partners=partners,
        jv_office_address=firm.get("jv_office_address", firm.get("firm_address", "")),
        jv_phone=firm.get("jv_phone", ""),
        lead_partner=firm.get("lead_partner", firm.get("Lead Partner", "")),
        nominated_partner=firm.get("nominated_partner", firm.get("Nominated Partner", firm.get("Nminated Partner", ""))),
        partner_in_charge_name=firm.get("partner_in_charge_name", ""),
        partner_in_charge_firm=firm.get("partner_in_charge_firm", ""),
        equipment=tds.get("equipment", []),
        manpower=tds.get("manpower", []),
        boq_items=boq.get("boq_items", []),
        rate_schedule_ref=firm.get("rate_schedule_ref", "BWDB, 2019-20 Rate Schedule"),
        work_activities=firm.get("work_activities", []),
        work_start_year=_year(start_date, 2021),
        work_end_year=_year(completion_date, 2022),
        work_months=firm.get("work_months", [
            "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        ]),
        **_partner_kwargs(firm),
    )


def _partners_from_context(firm: dict) -> list[JVPartner]:
    partners = []
    for idx in range(1, 4):
        name = firm.get(f"partner{idx}_firm_name", "")
        if not name:
            continue
        partners.append(JVPartner(
            code=firm.get(f"partner{idx}_code", ""),
            name=name,
            legal_type=firm.get(f"partner{idx}_legal_type", ""),
            address=firm.get(f"partner{idx}_address", ""),
            signatory_name=firm.get(f"partner{idx}_signatory_name", ""),
            position=firm.get(f"partner{idx}_position", ""),
            role="lead" if idx == 1 else "partner",
            share_percent=float(firm.get(f"partner{idx}_share_percent", 0) or 0),
            share_words=firm.get(f"partner{idx}_share_words", ""),
        ))
    return partners


def _partner_kwargs(firm: dict) -> dict:
    data = {}
    for idx in range(1, 4):
        prefix = f"partner{idx}_"
        data[prefix + "code"] = firm.get(prefix + "code", "")
        data[prefix + "firm_name"] = firm.get(prefix + "firm_name", "")
        data[prefix + "legal_type"] = firm.get(prefix + "legal_type", "")
        data[prefix + "address"] = firm.get(prefix + "address", "")
        data[prefix + "signatory_name"] = firm.get(prefix + "signatory_name", "")
        data[prefix + "position"] = firm.get(prefix + "position", "")
        data[prefix + "share_percent"] = float(firm.get(prefix + "share_percent", 0) or 0)
        data[prefix + "share_words"] = firm.get(prefix + "share_words", "")
    return data


def _first(primary: dict, secondary: dict, key: str, default=""):
    value = primary.get(key)
    if value not in (None, "", []):
        return value
    value = secondary.get(key)
    return default if value in (None, "", []) else value


def _year(date_value: str, default: int) -> int:
    try:
        return int(str(date_value).split("-")[-1])
    except Exception:
        return default


def _find_pdf(folder: Path, keywords: list[str]) -> Path | None:
    for pdf in sorted(folder.glob("*.pdf")):
        name = pdf.name.lower().replace(" ", "")
        for key in keywords:
            key = key.lower()
            if key[0].isdigit():
                if name.startswith(key):
                    return pdf
            elif key in name:
                return pdf
    return None
