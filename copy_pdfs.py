import shutil, pathlib

src = pathlib.Path(r"D:\Work space\Tender_data_automation-main")
dst = pathlib.Path(r"D:\Work space\Tender_data_automation-main\Tender_data_automation-main\tender_engine\input\541339")
dst.mkdir(parents=True, exist_ok=True)

files = [
    "1. Notice_541339.pdf",
    "2. TDS_1_541339.pdf",
    "3. TDS_2_541339.pdf",
    "4. BOQ_541339.pdf",
]
for f in files:
    shutil.copy(src / f, dst / f)
    print(f"  Copied: {f}")

print("Done.")
