"""
Generic tender batch generator.

Usage:
    python batch_GEN.py 552225

Input folder must be:
    tender_engine/input/552225/

Output folder will be:
    tender_engine/output/552225/
"""

import pathlib
import sys

BASE = pathlib.Path(__file__).parent
sys.path.insert(0, str(BASE))

from tender_engine.enhanced_runner import create_batch_script, generate_tender


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python batch_GEN.py <tender_id>")
        raise SystemExit(1)

    tender_id = sys.argv[1].strip()
    create_batch_script(tender_id)
    result = generate_tender(tender_id, run_rate_check=True)

    print("Generated Tender:", result["tender_id"])
    print("Input folder:", result["input_folder"])
    print("Output folder:", result["output_folder"])
    print("Files:")
    for name in result["output_files"]:
        print(" -", name)
