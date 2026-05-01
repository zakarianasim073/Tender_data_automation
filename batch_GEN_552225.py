"""Generate all files for Tender ID 552225."""

import pathlib
import sys

BASE = pathlib.Path(__file__).parent
sys.path.insert(0, str(BASE))

from tender_engine.enhanced_runner import generate_tender


if __name__ == "__main__":
    result = generate_tender("552225", run_rate_check=True)
    print("Generated Tender:", result["tender_id"])
    print("Input folder:", result["input_folder"])
    print("Output folder:", result["output_folder"])
    print("Files:")
    for name in result["output_files"]:
        print(" -", name)
