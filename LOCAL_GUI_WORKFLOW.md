# Local GUI Tender Workflow

## Folder Rule

Each tender has its own input and output folder:

```text
tender_engine/
  input/
    552225/
      1. Notice-552225.pdf
      2. TDS_1_552225.pdf
      2. TDS_2_552225.pdf
      4.BOQ_552225.pdf
      context.json
  output/
    552225/
      generated DOCX, XLSX, rate check, summary files
```

## Run Browser Dashboard

Install requirements once:

```bash
pip install -r requirements_engine.txt
```

Start the local browser dashboard:

```bash
python local_dashboard.py
```

Or double-click:

```text
start_dashboard.bat
```

The app opens locally at:

```text
http://127.0.0.1:7860
```

## Dashboard Features

- Create tender folder by Tender ID
- Upload Notice, TDS, BOQ PDFs into `input/<tender_id>/`
- Edit `context.json` for adjustable values
- Generate all DOCX and Excel files
- Run BWDB/LGED Schedule of Rates cross-check
- Create `Rate_Check-<tender_id>.xlsx`
- Create `Summary-<tender_id>.txt` and `Summary-<tender_id>.json`
- Run a missing-document checklist before generation
- Search generated tender JSON, text, Markdown, and CSV files locally
- Detect similar previous tenders and compare two tenders side by side
- Track local approval status: `Draft`, `Review`, `Approved`
- Export a Markdown review report: `Review-<tender_id>.md`
- Cache generated tender status locally for faster dashboard use
- Show/download output files
- Create direct command runner: `batch_GEN_<tender_id>.py`

## Local-First Feature Notes

These features were added from the larger production roadmap, but implemented for local-machine use first:

- **Document checklist**: prevents generation when critical PDFs or `context.json` are missing.
- **Local search**: indexes generated text-based outputs in `tender_engine/cache/search_index.json`.
- **Duplicate detection**: compares package, work name, location, and procuring entity against previous outputs.
- **Tender comparison**: compares two `extracted_data.json` files field by field.
- **Approval workflow**: stores status in `tender_engine/input/<tender_id>/approval.json`.
- **Review export**: creates a reviewer-friendly Markdown summary in the tender output folder.
- **Local cache**: stores recent generation status in `tender_engine/cache/<tender_id>.json`.
- **SOR upload**: saves uploaded BWDB/LGED rate schedule PDFs under `tender_engine/sor/uploads/` and updates `tender_engine/context/firm_config.json`.
- **Local AI BOQ cost prediction**: trains a scikit-learn model from generated tender history or a CSV, then exports `AI_Cost_Prediction-<tender_id>.json` and `.xlsx`.

Cloud-only items such as subscriptions, Stripe billing, multi-user quotas, hosted Redis/Celery workers, and production deployment are intentionally not part of this local build.

## SOR Upload Workflow

1. Open the `SOR Upload` tab.
2. Choose `BWDB` or `LGED`.
3. Upload the Schedule of Rates PDF.
4. Click `Save SOR Schedule`.

The active SOR paths are saved in:

```text
tender_engine/context/firm_config.json
```

## AI BOQ Cost Prediction Workflow

1. Generate at least one tender package so `output/<tender_id>/extracted_data.json` exists.
2. Open the `AI Cost Prediction` tab.
3. Click `Train From Generated Tender History`, or upload a CSV with these columns:

```text
category,region,unit_type,month,year,rate
```

4. Enter a Tender ID and click `Predict BOQ Costs`.

Outputs are saved in:

```text
tender_engine/output/<tender_id>/AI_Cost_Prediction-<tender_id>.json
tender_engine/output/<tender_id>/AI_Cost_Prediction-<tender_id>.xlsx
```

## Command Line Options

Generate a specific tender:

```bash
python batch_GEN.py 552225
```

Or run the generated tender-specific file:

```bash
python batch_GEN_552225.py
```

## Context Editing

Most templates stay fixed. Only adjustable fields should be edited in:

```text
tender_engine/input/<tender_id>/context.json
```

Common fields:

- `zone`: BWDB/LGED rate zone: `A`, `B`, `C`, or `D`
- `bg_date`
- `bg_validity_date`
- `bank_guarantee_no`
- `memo_no`
- `firm_name`
- `firm_address`
- `proprietor_name`
- `egp_email`
- `is_jv`
- `jv_name`

## Schedule of Rates

The SOR parser uses these PDFs from the parent folder:

```text
D:/Work space/Tender_data_automation-main/BWDB Revised Rate Schedule,2023.pdf
D:/Work space/Tender_data_automation-main/LGED Revised Rate Schedule,2023.pdf
```

Rate checker output:

```text
output/<tender_id>/Rate_Check-<tender_id>.xlsx
output/<tender_id>/Summary-<tender_id>.txt
output/<tender_id>/Summary-<tender_id>.json
```

Statuses:

- `MATCH`: within accepted tolerance
- `MISMATCH`: needs review
- `ABOVE_SOR`: quoted rate is higher than SOR
- `BELOW_SOR`: quoted rate is much lower than SOR
- `MISSING`: item code not found in SOR
