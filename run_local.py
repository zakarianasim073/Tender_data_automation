"""
run_local.py
============
One-command local runner for the Tender Document Automation Engine.

Usage:
    python run_local.py
      -- uses defaults below (edit FIRM_CONFIG for your office)

    python run_local.py --input "D:/path/to/tender/folder"
      -- process a specific tender folder

    python run_local.py --batch
      -- process ALL subfolders inside tender_engine/input/
"""

import argparse
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).parent
ENGINE_DIR      = BASE_DIR / "tender_engine"
TEMPLATE_DIR    = ENGINE_DIR / "templates"
INPUT_DIR       = ENGINE_DIR / "input"
OUTPUT_DIR      = ENGINE_DIR / "output"

# ── Your Firm Configuration ──────────────────────────────────────────────────
# Edit this block for your office. These values override extracted PDF data
# for fields that are not in the tender PDFs (firm name, bank details, etc.)
FIRM_CONFIG = {
    # Applicant firm
    "firm_name":         "M/S Hassan & Brothers",
    "firm_address":      "Mahmud Tower (9th Floor) 19, Siddique Bazar North South Road, Bongshal, Dhaka",
    "proprietor_name":   "Mahmudul Hassan",
    "egp_email":         "info@handbl.com",
    "memo_no":           "HB/",               # e.g. "HB/4515"

    # Bank
    "bank_name":         "SBAC Bank Limited",
    "bank_branch":       "Gulshan Branch, Dhaka, Bangladesh",
    "bank_guarantee_no": "",                   # filled manually per BG issuance

    # Procuring entity short form
    "procuring_entity_short": "BWDB",

    # JV details — set is_jv=True only if this is a joint venture tender
    "is_jv":             False,
    "jv_name":           "",
    "jv_date":           "",
    "jv_office_address": "",
    "jv_phone":          "",
    "partner_in_charge_name": "",
    "partner_in_charge_firm": "",

    # Work schedule months (edit to match the actual work period)
    "work_months": [
        "Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec",
        "Jan","Feb","Mar","Apr","May","Jun"
    ],

    # BOQ rate schedule reference
    "rate_schedule_ref": "BWDB, 2019-20 Rate Schedule",
}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Tender Document Automation Engine")
    parser.add_argument("--input", "-i", type=str, default=None,
                        help="Path to folder containing tender PDFs")
    parser.add_argument("--output", "-o", type=str, default=str(OUTPUT_DIR),
                        help="Base output folder (default: tender_engine/output)")
    parser.add_argument("--batch", "-b", action="store_true",
                        help="Process ALL subfolders in tender_engine/input/")
    args = parser.parse_args()

    try:
        from tender_engine.pipeline import run_pipeline
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed requirements:  pip install -r requirements_engine.txt")
        sys.exit(1)

    if args.batch:
        # Process every subfolder in INPUT_DIR
        subfolders = [f for f in INPUT_DIR.iterdir() if f.is_dir()]
        if not subfolders:
            print(f"⚠️  No subfolders found in {INPUT_DIR}")
            print(f"   Create one per tender, e.g.: {INPUT_DIR}/541339/")
            print(f"   Then drop the 4 PDFs inside it.")
            return
        print(f"\n🔄 Batch mode: processing {len(subfolders)} tender(s)...\n")
        for folder in subfolders:
            print(f"\n{'─'*60}")
            print(f"  Tender folder: {folder.name}")
            run_pipeline(str(folder), str(TEMPLATE_DIR), args.output, FIRM_CONFIG)

    else:
        # Single tender
        input_folder = args.input
        if not input_folder:
            # Default: use the first subfolder found in INPUT_DIR
            subfolders = [f for f in INPUT_DIR.iterdir() if f.is_dir()]
            if subfolders:
                input_folder = str(subfolders[0])
                print(f"📂 Auto-detected input: {input_folder}")
            else:
                print(f"\n⚠️  No input folder specified and none found in {INPUT_DIR}")
                print(f"\n  HOW TO USE:")
                print(f"  1. Create a folder:  {INPUT_DIR}\\<tender_id>\\")
                print(f"  2. Copy your 4 PDFs there (notice, tds_1, tds_2, boq)")
                print(f"  3. Run:  python run_local.py")
                print(f"\n  OR specify directly:")
                print(f"  python run_local.py --input \"D:\\path\\to\\tender_folder\"")
                return

        run_pipeline(input_folder, str(TEMPLATE_DIR), args.output, FIRM_CONFIG)


if __name__ == "__main__":
    main()
