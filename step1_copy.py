import shutil, pathlib
SAMPLE = pathlib.Path(r"D:\Work space\Tender_data_automation-main")
INPUT  = pathlib.Path(r"D:\Work space\Tender_data_automation-main\Tender_data_automation-main\tender_engine\input\541339")
INPUT.mkdir(parents=True, exist_ok=True)
for f in ["1. Notice_541339.pdf","2. TDS_1_541339.pdf","3. TDS_2_541339.pdf","4. BOQ_541339.pdf"]:
    shutil.copy2(SAMPLE/f, INPUT/f)
    print("Copied:", f)
print("STEP1 OK")
