"""
setup_and_run.py
Full setup: copy PDFs, create DOCX templates from samples, run pipeline.
"""
import sys, shutil, pathlib, re, json, traceback

BASE   = pathlib.Path(r"D:\Work space\Tender_data_automation-main\Tender_data_automation-main")
SAMPLE = pathlib.Path(r"D:\Work space\Tender_data_automation-main")
INPUT  = BASE / "tender_engine" / "input"  / "541339"
TPLS   = BASE / "tender_engine" / "templates" / "docx"
OUT    = BASE / "tender_engine" / "output"

sys.path.insert(0, str(BASE))

# ── Step 1: Copy PDFs ────────────────────────────────────────────────────────
print("\n=== STEP 1: Copy PDFs ===")
INPUT.mkdir(parents=True, exist_ok=True)
pdf_map = {
    "1. Notice_541339.pdf":  "1. Notice_541339.pdf",
    "2. TDS_1_541339.pdf":   "2. TDS_1_541339.pdf",
    "3. TDS_2_541339.pdf":   "3. TDS_2_541339.pdf",
    "4. BOQ_541339.pdf":     "4. BOQ_541339.pdf",
}
for src_name, dst_name in pdf_map.items():
    src = SAMPLE / src_name
    dst = INPUT / dst_name
    if src.exists():
        shutil.copy2(src, dst)
        print(f"  Copied: {dst_name}")
    else:
        print(f"  MISSING: {src}")

# ── Step 2: Create DOCX templates from samples ───────────────────────────────
print("\n=== STEP 2: Build DOCX templates ===")
try:
    from docx import Document
    from docx.oxml.ns import qn
    import copy, zipfile, io

    def make_template_from_sample(src_docx, dst_docx, replacements):
        """
        Load sample DOCX, do find-and-replace of real values -> placeholders,
        save as template.
        Uses zipfile approach to handle deeply split runs reliably.
        """
        with zipfile.ZipFile(str(src_docx), 'r') as zin:
            names = zin.namelist()
            out_buf = io.BytesIO()
            with zipfile.ZipFile(out_buf, 'w', zipfile.ZIP_DEFLATED) as zout:
                for name in names:
                    data = zin.read(name)
                    if name in ('word/document.xml', 'word/header1.xml',
                                'word/header2.xml', 'word/footer1.xml',
                                'word/footer2.xml'):
                        text = data.decode('utf-8')
                        for old, new in replacements.items():
                            text = text.replace(old, new)
                        data = text.encode('utf-8')
                    zout.writestr(name, data)
        with open(str(dst_docx), 'wb') as f:
            f.write(out_buf.getvalue())
        print(f"  Created template: {dst_docx.name}")

    # BG_HB template
    bg_replacements = {
        "541339":                          "{{TENDER_ID}}",
        "T-1/1757 Dated: 25/01/2021":     "{{INVITATION_REF_NO}}",
        "e-GP-50/PW/Anowara/Sea-Dyke":    "{{PACKAGE_NO}}",
        "Chittagong O&amp;M Division-1":   "{{PE_DIVISION}}",
        "BWDB, Chittagong.":               "{{PROCURING_ENTITY_SHORT}}, Chittagong.",
        "24-August-2021":                  "{{BG_VALIDITY_DATE}}",
        "75,0\n0,000":                     "{{TENDER_SECURITY_BDT_RAW}}",
        "Seventy Five":                    "{{TENDER_SECURITY_WORDS}}",
        "M/S Hassan &amp; Brothers":       "{{FIRM_NAME}}",
        "Mahmud Tower (9":                 "{{FIRM_ADDRESS_START}}",
        "24.02.2021":                      "{{BG_DATE}}",
        "info@handbl.com":                 "{{EGP_EMAIL}}",
        "SBAC Bank Limited":               "{{BANK_NAME}}",
        "Gulshan Branch, Dhaka":           "{{BANK_BRANCH}}",
        "Mahmudul Hassan":                 "{{PROPRIETOR_NAME}}",
    }

    src_bg  = SAMPLE / "2. BG_HB_SBAC-541339.docx"
    dst_bg  = TPLS   / "BG_HB_template.docx"
    if src_bg.exists():
        shutil.copy2(src_bg, dst_bg)
        print(f"  Copied as-is (template): {dst_bg.name}")

    # BG Credit Line template
    src_cl = SAMPLE / "3. BG & Credit Line Issue Application SBAC.docx"
    dst_cl = TPLS   / "BG_Credit_Line_template.docx"
    if src_cl.exists():
        shutil.copy2(src_cl, dst_cl)
        print(f"  Copied as-is (template): {dst_cl.name}")

    # Equipment Declaration template
    src_eq = SAMPLE / "4. Equipment  Declaration_541339.docx"
    dst_eq = TPLS   / "Equipment_Declaration_template.docx"
    if src_eq.exists():
        shutil.copy2(src_eq, dst_eq)
        print(f"  Copied as-is (template): {dst_eq.name}")

    # Manpower Declaration template
    src_mp = SAMPLE / "5. Manpower Declaration.docx"
    dst_mp = TPLS   / "Manpower_Declaration_template.docx"
    if src_mp.exists():
        shutil.copy2(src_mp, dst_mp)
        print(f"  Copied as-is (template): {dst_mp.name}")

    # Methodology template
    src_mt = SAMPLE / "6. Methodology_541339.docx"
    dst_mt = TPLS   / "Methodology_template.docx"
    if src_mt.exists():
        shutil.copy2(src_mt, dst_mt)
        print(f"  Copied as-is (template): {dst_mt.name}")

    # JV templates
    src_jd = SAMPLE / "JV DEED_LA-TI JV_541339.docx"
    dst_jd = TPLS   / "JV_DEED_template.docx"
    if src_jd.exists():
        shutil.copy2(src_jd, dst_jd)
        print(f"  Copied as-is (template): {dst_jd.name}")

    src_jp = SAMPLE / "JV POA_LA-TI JV_541339.docx"
    dst_jp = TPLS   / "JV_POA_template.docx"
    if src_jp.exists():
        shutil.copy2(src_jp, dst_jp)
        print(f"  Copied as-is (template): {dst_jp.name}")

except Exception as e:
    print(f"  Template setup error: {e}")
    traceback.print_exc()

# ── Step 3: Run the pipeline ─────────────────────────────────────────────────
print("\n=== STEP 3: Run pipeline ===")
try:
    from tender_engine.pipeline import run_pipeline

    FIRM_CONFIG = {
        "firm_name":              "M/S Hassan & Brothers",
        "firm_address":           "Mahmud Tower (9th Floor) 19, Siddique Bazar North South Road, Bongshal, Dhaka",
        "proprietor_name":        "Mahmudul Hassan",
        "egp_email":              "info@handbl.com",
        "memo_no":                "HB/4515",
        "bank_name":              "SBAC Bank Limited",
        "bank_branch":            "Gulshan Branch, Dhaka, Bangladesh",
        "bank_guarantee_no":      "",
        "procuring_entity_short": "BWDB",
        "pe_division":            "Chittagong O&M Division-1",
        "is_jv":                  False,
        "jv_name":                "",
        "rate_schedule_ref":      "BWDB, 2019-20 Rate Schedule",
        "work_months": [
            "Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec",
            "Jan","Feb","Mar","Apr","May","Jun"
        ],
    }

    run_pipeline(
        input_folder  = str(INPUT),
        template_folder = str(BASE / "tender_engine" / "templates"),
        output_base   = str(OUT),
        firm_config   = FIRM_CONFIG,
    )

except Exception as e:
    print(f"\n  Pipeline error: {e}")
    traceback.print_exc()

print("\n=== DONE ===")
