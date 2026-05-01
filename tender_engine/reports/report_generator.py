"""
Report Generator
----------------
Generates the full output package for a tender:
  - Rate Check Excel (color-coded)
  - Summary PDF / text report
  - Per-document status list
"""

import pathlib
from typing import List
from ..checker.rate_checker import CheckSummary, STATUS_COLORS


def generate_rate_check_excel(summary: CheckSummary, output_path: str) -> str:
    """Generate color-coded Excel rate check report."""
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
        from openpyxl.utils import get_column_letter
    except ImportError:
        raise ImportError("openpyxl is required. Run: pip install openpyxl")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Rate Check"

    thin  = Side(style="thin")
    bdr   = Border(left=thin, right=thin, top=thin, bottom=thin)
    bold  = Font(bold=True, size=11)
    ctr   = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left  = Alignment(horizontal="left",   vertical="center", wrap_text=True)

    def fill(hex_color):
        return PatternFill("solid", fgColor=hex_color.replace("#", ""))

    # ── Title row ───────────────────────────────────────────────────
    ws.merge_cells("A1:L1")
    c = ws["A1"]
    c.value = f"BOQ Rate Check Report — Tender ID: {summary.tender_id}  |  Zone: {summary.zone}"
    c.font  = Font(bold=True, size=13)
    c.alignment = ctr
    c.fill  = fill("#1F4E79")
    c.font  = Font(bold=True, size=13, color="FFFFFF")
    ws.row_dimensions[1].height = 24

    # ── Summary block ────────────────────────────────────────────────
    summary_data = [
        ("Total Items", summary.total_items),
        ("MATCH",       summary.match_count),
        ("MISMATCH",    summary.mismatch_count),
        ("MISSING",     summary.missing_count),
        ("ABOVE SOR",   summary.above_sor_count),
        ("BELOW SOR",   summary.below_sor_count),
        ("Risk Level",  summary.risk_level),
        ("Total BOQ",   f"Tk. {summary.total_boq_amount:,.0f}"),
        ("Total Quoted",f"Tk. {summary.total_quoted_amount:,.0f}"),
        ("Total SOR",   f"Tk. {summary.total_sor_amount:,.0f}"),
        ("Overall Diff",f"{summary.overall_diff_pct:+.2f}%"),
    ]
    ws["A2"].value = "SUMMARY"
    ws["A2"].font  = bold
    for i, (label, val) in enumerate(summary_data):
        r = 3 + i
        ws.cell(row=r, column=1, value=label).font = bold
        ws.cell(row=r, column=2, value=val)

    # ── Column headers ────────────────────────────────────────────────
    hdr_row = 16
    headers = [
        "Item No", "Item Code", "Description", "Unit", "Quantity",
        "BOQ Rate", "Quoted Rate", "SOR Rate", "Zone",
        "Diff %", "Status", "Note"
    ]
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=hdr_row, column=col, value=h)
        c.font      = Font(bold=True, color="FFFFFF")
        c.fill      = fill("2E75B6")
        c.alignment = ctr
        c.border    = bdr
    ws.row_dimensions[hdr_row].height = 18

    # ── Data rows ────────────────────────────────────────────────────
    for idx, r in enumerate(summary.results):
        row = hdr_row + 1 + idx
        row_data = [
            r.item_no, r.item_code, r.description, r.unit, r.quantity,
            r.boq_rate, r.quoted_rate, r.sor_rate, r.zone,
            f"{r.diff_pct:+.2f}%", r.status, r.note
        ]
        row_fill = fill(r.color.replace("#","").zfill(6))
        for col, val in enumerate(row_data, 1):
            cell = ws.cell(row=row, column=col, value=val)
            cell.fill      = row_fill
            cell.border    = bdr
            cell.alignment = left if col == 3 else ctr
        ws.row_dimensions[row].height = 15

    # ── Column widths ─────────────────────────────────────────────────
    widths = [8, 14, 55, 8, 12, 12, 12, 12, 6, 10, 12, 45]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    # ── Legend ───────────────────────────────────────────────────────
    last_row = hdr_row + 1 + len(summary.results) + 2
    ws.cell(row=last_row, column=1, value="LEGEND:").font = bold
    legend = [
        ("MATCH",     "#92D050", "Rate within +/-5% of SOR"),
        ("MISMATCH",  "#FFFF00", "Rate differs from SOR (needs review)"),
        ("ABOVE_SOR", "#FF0000", "Quoted HIGHER than SOR — justification required"),
        ("BELOW_SOR", "#FFC000", "Quoted much lower — check for data entry error"),
        ("MISSING",   "#D9D9D9", "Item code not found in SOR database"),
    ]
    for i, (status, color, desc) in enumerate(legend):
        r = last_row + 1 + i
        c = ws.cell(row=r, column=1, value=status)
        c.fill = fill(color.replace("#",""))
        c.font = bold
        c.border = bdr
        ws.cell(row=r, column=2, value=desc)

    wb.save(output_path)
    print(f"  [OK] Rate check report: {pathlib.Path(output_path).name}")
    return output_path


def generate_summary_txt(summary: CheckSummary, output_path: str) -> str:
    """Generate a plain-text summary report."""
    lines = [
        "=" * 65,
        f"  BOQ RATE CHECK SUMMARY",
        f"  Tender ID : {summary.tender_id}",
        f"  Zone      : {summary.zone}",
        "=" * 65,
        f"  Total items   : {summary.total_items}",
        f"  MATCH         : {summary.match_count}",
        f"  MISMATCH      : {summary.mismatch_count}",
        f"  MISSING       : {summary.missing_count}",
        f"  ABOVE SOR     : {summary.above_sor_count}  (RED FLAG)",
        f"  BELOW SOR     : {summary.below_sor_count}  (CHECK)",
        f"  Risk Level    : {summary.risk_level}",
        "-" * 65,
        f"  Total BOQ Amt : Tk. {summary.total_boq_amount:>15,.0f}",
        f"  Total Quoted  : Tk. {summary.total_quoted_amount:>15,.0f}",
        f"  Total SOR Amt : Tk. {summary.total_sor_amount:>15,.0f}",
        f"  Overall Diff  : {summary.overall_diff_pct:+.2f}%",
        "=" * 65,
        "",
        "ITEMS REQUIRING ATTENTION:",
        "-" * 65,
    ]
    attention = [r for r in summary.results if r.status != "MATCH"]
    if attention:
        for r in attention:
            lines.append(
                f"  [{r.status:<10}] #{r.item_no} {r.item_code:<14} "
                f"Quoted:{r.quoted_rate:>10.2f}  SOR:{r.sor_rate:>10.2f}  "
                f"Diff:{r.diff_pct:+.1f}%"
            )
            if r.note:
                lines.append(f"             NOTE: {r.note}")
    else:
        lines.append("  All items MATCH SOR rates.")
    lines += ["", "=" * 65]
    text = "\n".join(lines)
    pathlib.Path(output_path).write_text(text, encoding="utf-8")
    print(f"  [OK] Summary report: {pathlib.Path(output_path).name}")
    return output_path
