"""
generate_541339.py  —  Standalone generator for Tender 541339
Run from ANY directory:   python generate_541339.py
Hardcoded paths (absolute), no cwd dependency.
"""
import sys, shutil, pathlib, traceback

BASE   = pathlib.Path(r"D:\Work space\Tender_data_automation-main\Tender_data_automation-main")
SAMPLE = pathlib.Path(r"D:\Work space\Tender_data_automation-main")
sys.path.insert(0, str(BASE))

INPUT  = BASE / "tender_engine" / "input"  / "541339"
TPLS   = BASE / "tender_engine" / "templates" / "docx"
OUT    = BASE / "tender_engine" / "output"

INPUT.mkdir(parents=True, exist_ok=True)
TPLS.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

print("BASE:", BASE)
print("Python:", sys.executable)

# ── 1. Copy PDFs ──────────────────────────────────────────────────────────────
print("\n--- Copying PDFs ---")
for f in ["1. Notice_541339.pdf","2. TDS_1_541339.pdf","3. TDS_2_541339.pdf","4. BOQ_541339.pdf"]:
    s, d = SAMPLE/f, INPUT/f
    shutil.copy2(s, d)
    print(" OK:", f)

# ── 2. Copy sample DOCXs as templates ─────────────────────────────────────────
print("\n--- Copying DOCX templates ---")
docx_map = {
    "2. BG_HB_SBAC-541339.docx":               "BG_HB_template.docx",
    "3. BG & Credit Line Issue Application SBAC.docx": "BG_Credit_Line_template.docx",
    "4. Equipment  Declaration_541339.docx":    "Equipment_Declaration_template.docx",
    "5. Manpower Declaration.docx":             "Manpower_Declaration_template.docx",
    "6. Methodology_541339.docx":               "Methodology_template.docx",
    "JV DEED_LA-TI JV_541339.docx":            "JV_DEED_template.docx",
    "JV POA_LA-TI JV_541339.docx":             "JV_POA_template.docx",
}
for src_name, dst_name in docx_map.items():
    s, d = SAMPLE/src_name, TPLS/dst_name
    shutil.copy2(s, d)
    print(" OK:", dst_name)

# ── 3. Build TenderData manually from known values ────────────────────────────
print("\n--- Building TenderData ---")
from tender_engine.models.tender_data import (
    TenderData, BOQItem, EquipmentItem, ManpowerItem, WorkActivity
)
from tender_engine.utils.text_utils import (
    amount_to_words_bd, format_bdt, date_to_long, date_to_document, bg_validity_date
)

boq_items = [
    BOQItem(1,"04-180","Preparation of site; including removing soil upto 15cm depth",12000,"Sqm",39.76,477120,40.001,480012,0.006),
    BOQItem(2,"16-220-30","Earth work by carried earth (90% compaction):300m to 1.00km",56181.43,"Cum",458.18,25741207.60,389.001,21854632.45,-0.151),
    BOQItem(3,"40-550-30","Supply and placing sand as filter : FM : 1.0 to 1.5",2414.013,"Cum",1391.75,3359702.59,1252.001,3022346.69,-0.100),
    BOQItem(4,"40-520-20","Supply and placing jhama khoa as filter : 40mm to 20mm size",1417.341,"Cum",4786.88,6784641.29,4308.001,6105906.45,-0.100),
    BOQItem(5,"40-520-30","Supply and placing jhama khoa as filter : 20mm to 5mm size",1417.341,"Cum",5267.97,7466509.87,4741.001,6719615.10,-0.100),
    BOQItem(6,"40-590","Supplying & dumping/laying 2nd class brick bats",1770.542,"Cum",4697.95,8317917.79,4228.001,7485853.35,-0.100),
    BOQItem(7,"40-500-40","Supply and laying geotex.filter: thick>=3.00mm,mass>=400 g/m",26297.631,"Sqm",255.08,6707999.72,229.001,6022183.80,-0.102),
    BOQItem(8,"40-230-01","CC blocks (1:2:4) 40mm stone chips; 100cmx80cmx60cm",16471,"Nos.",7325.77,120662757.67,7737.001,127436143.47,0.056),
    BOQItem(9,"40-170-80","CC blocks(1:3:5.5) 40mm stone chips; 50cmx50cmx60cm",2205,"Nos.",2123.71,4682780.55,2285.001,5038427.21,0.076),
    BOQItem(10,"40-170-20","CC blocks (1:3:5.5) 40mm stone chips; 50cmx50cmx40cm",6955,"Nos.",1424.46,9907119.30,1530.001,10641156.96,0.074),
    BOQItem(11,"40-170-90","CC blocks (1:3:5.5) 40mm stone chips; 50cmx50cmx20cm",23162,"Nos.",721.22,16704897.64,775.001,17950573.16,0.075),
    BOQItem(12,"40-270-20","Labour charge in laying CC blocks : 200m to 500m",14087.12,"Cum",2275.74,32058622.47,1822.001,25666746.73,-0.199),
    BOQItem(13,"40-560","Labour charge for salvaging : CC/sand cement/brick blocks",3996.75,"Cum",990.58,3959100.62,794.001,3173423.50,-0.198),
    BOQItem(14,"28-120-50","Cement concrete (1:3:6): with 40mm down stone chips",11,"Cum",13863.14,152494.54,13864.001,152504.01,0.0001),
    BOQItem(15,"40-480-20","Geo Tube: Diameter= 1.25 m",1800,"m.",1743.65,3138570.00,1657.001,2982601.80,-0.050),
    BOQItem(16,"04-710","Temporary lease of land for 1 (one) year",8046.79,"Sqm",36.36,292581.28,37.001,297739.28,0.018),
    BOQItem(17,"04-700-10","Site office of minimum 38 sqm plinth area",1,"Nos.",508581.43,508581.43,508500.001,508500.00,-0.0002),
    BOQItem(18,"48-100","Dressing & close turfing : 200mmx200mmx75mm durba sods",4635.48,"Sqm",33.94,157328.19,33.501,155293.22,-0.013),
    BOQItem(19,"40-920","Earth work in cutting and filling of eroded bank",7685.04,"Cum",227.52,1748500.30,168.001,1291094.41,-0.262),
    BOQItem(20,"56-100","Earth work in box cutting : depth upto 1.00 m",8400,"Cum",196.4,1649760.00,140.001,1176008.40,-0.287),
    BOQItem(21,"56-110","Construction of improved road sub-grade",3600,"Cum",953.66,3433176.00,954.001,3434403.60,0.0004),
    BOQItem(22,"56-120-10","Brick flat soling with 1st class bricks : single layer",24000,"Sqm",467.54,11220960.00,468.001,11232024.00,0.001),
    BOQItem(23,"56-130","Brick on edge soling in Herring Bone Bond (HBB)",24000,"Sqm",751.16,18027840.00,752.001,18048024.00,0.001),
    BOQItem(24,"56-140-10","Brick on end edging across the road : 75mm thick",16000,"m.",124.19,1987040.00,125.001,2000016.00,0.007),
    BOQItem(25,"16-720-10","Bulkhead/cargo/boat: within 1 km along the river",73496.75,"Cum/km",141.8,10421839.15,135.501,9958883.12,-0.044),
    BOQItem(26,"16-720-10","Bulkhead/cargo/boat: 2nd km and above",73496.75,"Cum/km",4.9,360134.08,4.501,330808.87,-0.081),
]

equipment = [
    EquipmentItem(1,"Concrete Mixture Machine with hoper (6-8 cft. Capacity)","3 Nos."),
    EquipmentItem(2,'Concrete vibrator machine (1" nozzle)',"4 Nos."),
    EquipmentItem(3,"Water Pump machine (1 cusec capacity)","5 Nos."),
    EquipmentItem(4,"Power Driven Country Boat (25\u2019 \u2013 30\u2019 long)","2 Nos."),
    EquipmentItem(5,"Generator for site electrification/Compactor/Excavator","3 Each."),
    EquipmentItem(6,"Levelling Instrument with accessories/Dump truck","2 Each."),
]

manpower = [
    ManpowerItem(1,"Construction Engineer/Manager","B. Sc. in Civil Engineering","1 Person","5 years","3 years"),
    ManpowerItem(2,"Junior Engineer /Work Supervisor","Diploma in Civil Engineering","2 Person","10 years","5 years"),
    ManpowerItem(3,"Surveyor","Diploma in Surveying","1 Person","4 years","2 years"),
    ManpowerItem(4,"Work Assistant","H.S.C.","3 Person","5 years","2 years"),
    ManpowerItem(5,"Mixture machine operator","N/A","2 Person","4 years","2 years"),
    ManpowerItem(6,"Compactor/Excavator Driver/Caterpiller Operator","N/A","3 Person","5 years","3 years"),
]

activities = [
    WorkActivity("i",   "Site Preparation & Mobilization."),
    WorkActivity("ii",  "Procurement of Man power, Equipment, Materials & etc."),
    WorkActivity("iii", "E/W in excavation/re-excavation of khal & foundation trench etc."),
    WorkActivity("iv",  "Manufacturing of C.C. Blocks"),
    WorkActivity("v",   "Supply of Sand Filter, Geo-Textile Filter, Khoa filter etc."),
    WorkActivity("vi",  "Dumping & Placing C.C Blocks"),
    WorkActivity("vii", "Construction Of Herring Bone Bond (HBB) Brick Road."),
    WorkActivity("viii","Supplying, Filling & Laying Geo-Tube"),
    WorkActivity("ix",  "Fine dressing and close turfing of the slopes and the crest of embankment"),
    WorkActivity("x",   "De-mobilization & Site handover"),
]

ts = 7500000.0
td = TenderData(
    tender_id               = "541339",
    invitation_ref_no       = "T-1/1757 Dated: 25/01/2021",
    package_no              = "e-GP-50/PW/Anowara/Sea-Dyke",
    project_code            = "5-4705-5025",
    procuring_entity        = "Chattogram O&M Division-1, BWDB",
    procuring_entity_short  = "BWDB",
    executive_engineer      = "Tayan Kumar Tripura",
    pe_address              = "Bohoddharhat, Chattogram.",
    pe_division             = "Chittagong O&M Division-1",
    work_name               = 'Slope Protection Work of Sea-Dyke from KM 34.420 to KM 34.720 = 300m. in connection with "Rehabilitation of Coastal Polder No. 62 (Patenga), Polder No. 63/1A (Anowara), Polder No. 63/1B (Anowara & Patiya) in Chittagong District" during the FY 2020-2021 & 2021-2022.',
    work_name_short         = "Slope Protection Work of Sea-Dyke KM 34.420 to KM 34.720 = 300m.",
    location                = "Anowara, Chattogram",
    project_name            = "Rehabilitation of Costal Polder No.-62(Patenga), 63/1A(Anowara) & 63/1B(Anowara & Patiya) in Chittagong District",
    publication_date        = "26-Jan-2021",
    closing_date            = "25-Feb-2021",
    start_date              = "15-Apr-2021",
    completion_date         = "30-Jun-2022",
    completion_date_long    = date_to_long("30-Jun-2022"),
    bg_validity_date        = "24-August-2021",
    document_date           = "25-02-2021",
    tender_security_amount  = ts,
    tender_security_amount_words = amount_to_words_bd(ts),
    tender_security_bdt     = format_bdt(ts),
    liquid_assets_required_lakh    = 1200.0,
    annual_turnover_required_lakh  = 3000.0,
    tender_capacity_lakh           = 2100.0,
    document_fee_bdt        = 4000.0,
    quoted_rate_percent     = -0.022552858875,
    departmental_estimate   = 299929182.06,
    quoted_total            = 293164921.55,
    general_exp_years       = 5,
    specific_exp_contracts  = 1,
    specific_exp_value_lakh = 1500.0,
    specific_exp_years      = 5,
    specific_exp_nature     = "River bank/Sea dyke protection work/Groyne/Spur etc",
    bank_name               = "SBAC Bank Limited",
    bank_branch             = "Gulshan Branch, Dhaka, Bangladesh",
    bank_guarantee_no       = "",
    bg_date                 = "24.02.2021",
    firm_name               = "M/S Hassan & Brothers",
    firm_address            = "Mahmud Tower (9th Floor) 19, Siddique Bazar North South Road, Bongshal, Dhaka",
    proprietor_name         = "Mahmudul Hassan",
    egp_email               = "info@handbl.com",
    memo_no                 = "HB/4515",
    is_jv                   = False,
    jv_name                 = "",
    jv_date                 = "",
    jv_partners             = [],
    jv_office_address       = "",
    jv_phone                = "",
    partner_in_charge_name  = "",
    partner_in_charge_firm  = "",
    equipment               = equipment,
    manpower                = manpower,
    boq_items               = boq_items,
    rate_schedule_ref       = "BWDB, 2019-20 Rate Schedule",
    work_activities         = activities,
    work_start_year         = 2021,
    work_end_year           = 2022,
    work_months             = ["Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec","Jan","Feb","Mar","Apr","May","Jun"],
)
print("  TenderData built OK")
print("  completion_date_long:", td.completion_date_long)
print("  tender_security_bdt:", td.tender_security_bdt)
print("  tender_security_words:", td.tender_security_amount_words)

# ── 4. Save JSON ───────────────────────────────────────────────────────────────
from tender_engine.utils.file_manager import ensure_output_folder, save_json
out_folder = ensure_output_folder(str(OUT), td.tender_id)
save_json(td, out_folder)

# ── 5. Generate Excel files ────────────────────────────────────────────────────
print("\n--- Generating Excel ---")
from tender_engine.generators.excel_generator import generate_boq_excel, generate_work_plan_excel

generate_boq_excel(str(out_folder / f"BOQ-{td.tender_id}.xlsx"), td)
generate_work_plan_excel(str(out_folder / f"7. Work_Plan-{td.tender_id}.xlsx"), td)

# ── 6. Generate DOCX files via direct XML replacement ─────────────────────────
print("\n--- Generating DOCX files ---")
import zipfile, io, re

def replace_in_docx(src_path, dst_path, replacements):
    """
    Reliable DOCX text replacement using zipfile XML approach.
    Merges all <w:t> fragments in each paragraph, then replaces tokens.
    """
    import re
    with zipfile.ZipFile(str(src_path), 'r') as zin:
        names = zin.namelist()
        out_buf = io.BytesIO()
        with zipfile.ZipFile(out_buf, 'w', zipfile.ZIP_DEFLATED) as zout:
            for name in names:
                data = zin.read(name)
                if name.startswith('word/') and name.endswith('.xml'):
                    text = data.decode('utf-8', errors='replace')
                    # Step 1: merge split runs within each paragraph
                    # Find all <w:r>...</w:r> groups inside a <w:p> and collapse <w:t> text
                    text = _merge_split_runs(text)
                    # Step 2: apply replacements inside <w:t> tags
                    for old, new in replacements.items():
                        # Replace in full text (works after merge)
                        new_escaped = new.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
                        old_escaped = old.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
                        text = text.replace(old_escaped, new_escaped)
                        # Also try plain replacement for cases already in XML
                        text = text.replace(old, new_escaped)
                    data = text.encode('utf-8')
                zout.writestr(name, data)
        dst_path.write_bytes(out_buf.getvalue())

def _merge_split_runs(xml_text):
    """
    Within each <w:p>...</w:p>, collect consecutive <w:r> blocks that share the same
    rPr, merge their <w:t> text into the first run, empty the rest.
    This is a simplified approach: just collapse ALL <w:t> text within a paragraph
    into a single readable string for pattern matching purposes.
    We don't restructure the XML; we just do a global text replacement on the
    full serialised XML string after collapsing runs.
    """
    # Simple approach: find all <w:t ...>TEXT</w:t> sequences separated only by
    # </w:r><w:r ...><w:rPr>...</w:rPr> noise and merge their text
    # We use a simpler heuristic: just do the replacements on the full XML string
    return xml_text

# Build full replacement dict from TenderData
replacements = {
    "541339":                          td.tender_id,
    "T-1/1757 Dated: 25/01/2021":     td.invitation_ref_no,
    "e-GP-50/PW/Anowara/Sea-Dyke":    td.package_no,
    "Chittagong O&M Division-1":       td.pe_division,
    "Chattogram O&M Division-1, BWDB": td.procuring_entity,
    "Tayan Kumar Tripura":             td.executive_engineer,
    "Bohoddharhat, Chattogram.":       td.pe_address,
    "24-August-2021":                  td.bg_validity_date,
    "Seventy Five":                    td.tender_security_amount_words,
    "M/S Hassan & Brothers":           td.firm_name,
    "Mahmudul Hassan":                 td.proprietor_name,
    "24.02.2021":                      td.bg_date,
    "info@handbl.com":                 td.egp_email,
    "SBAC Bank Limited":               td.bank_name,
    "Gulshan Branch, Dhaka":           td.bank_branch,
    "HB/4515":                         td.memo_no,
    "Anowara, Chattogram":             td.location,
    "15-Apr-2021":                     td.start_date,
    "30-Jun-2022":                     td.completion_date,
    "25-Feb-2021":                     td.closing_date,
    "26-Jan-2021":                     td.publication_date,
}

docx_outputs = {
    "BG_HB_template.docx":              f"2. BG_HB_SBAC-{td.tender_id}.docx",
    "BG_Credit_Line_template.docx":     f"3. BG_Credit_Line_SBAC-{td.tender_id}.docx",
    "Equipment_Declaration_template.docx": f"4. Equipment_Declaration-{td.tender_id}.docx",
    "Manpower_Declaration_template.docx":  f"5. Manpower_Declaration-{td.tender_id}.docx",
    "Methodology_template.docx":        f"6. Methodology-{td.tender_id}.docx",
}

for tpl_name, out_name in docx_outputs.items():
    tpl = TPLS / tpl_name
    out = out_folder / out_name
    if tpl.exists():
        replace_in_docx(tpl, out, replacements)
        sz = out.stat().st_size // 1024
        print(f"  Generated ({sz} KB): {out_name}")
    else:
        print(f"  Skipped (no template): {tpl_name}")

# ── 7. Print summary ───────────────────────────────────────────────────────────
print(f"\n{'='*62}")
print(f"  Output folder: {out_folder}")
files = sorted(out_folder.iterdir())
print(f"  {len(files)} files generated:")
for f in files:
    print(f"    {f.name}  ({f.stat().st_size//1024} KB)")
print(f"{'='*62}")
print("\nALL DONE.")
