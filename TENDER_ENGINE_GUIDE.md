# Tender Document Automation Engine
## Complete Local Setup & Usage Guide

---

## What this does

Takes your **4 tender PDFs** as input → automatically generates **all required DOCX and Excel files** ready for submission.

| Input (PDFs) | Output (auto-generated) |
|---|---|
| 1. Notice PDF | 2. BG_HB_SBAC-{ID}.docx |
| 2. TDS_1 PDF | 3. BG_Credit_Line_SBAC-{ID}.docx |
| 3. TDS_2 PDF | 4. Equipment_Declaration-{ID}.docx |
| 4. BOQ PDF | 5. Manpower_Declaration-{ID}.docx |
| | 6. Methodology-{ID}.docx |
| | 7. Work_Plan-{ID}.xlsx |
| | BOQ-{ID}.xlsx |
| | extracted_data.json |

---

## Step 1 — Install Python dependencies

Open a terminal (Command Prompt or PowerShell) in this folder:

```
cd "D:\Work space\Tender_data_automation-main\Tender_data_automation-main"
pip install -r requirements_engine.txt
```

---

## Step 2 — Set up your templates

The engine uses **template DOCX/XLSX files** with `{{PLACEHOLDER}}` tokens.

### Where to put templates

```
tender_engine/
  templates/
    docx/
      BG_HB_template.docx
      BG_Credit_Line_template.docx
      Equipment_Declaration_template.docx
      Manpower_Declaration_template.docx
      Methodology_template.docx
      JV_DEED_template.docx        (only needed for JV tenders)
      JV_POA_template.docx         (only needed for JV tenders)
    excel/
      (Excel files are generated from scratch — no template needed)
```

### How to create a template from your existing DOCX

1. Open your existing sample DOCX (e.g. `2. BG_HB_SBAC-541339.docx`)
2. Find and replace each specific value with the matching placeholder:

| Replace this | With this |
|---|---|
| `541339` | `{{TENDER_ID}}` |
| `T-1/1757 Dated: 25/01/2021` | `{{INVITATION_REF_NO}}` |
| `e-GP-50/PW/Anowara/Sea-Dyke` | `{{PACKAGE_NO}}` |
| `Slope Protection Work of Sea-Dyke...` | `{{WORK_NAME}}` |
| `Chattogram O&M Division-1, BWDB` | `{{PROCURING_ENTITY}}` |
| `Chittagong O&M Division-1` | `{{PE_DIVISION}}` |
| `24-August-2021` | `{{BG_VALIDITY_DATE}}` |
| `Tk. 75,00,000.00` | `{{TENDER_SECURITY_BDT}}` |
| `Seventy Five Lac` | `{{TENDER_SECURITY_WORDS}}` |
| `SBAC Bank Limited` | `{{BANK_NAME}}` |
| `Gulshan Branch, Dhaka, Bangladesh` | `{{BANK_BRANCH}}` |
| `M/S Hassan & Brothers` | `{{FIRM_NAME}}` |
| `Mahmud Tower (9th Floor)...` | `{{FIRM_ADDRESS}}` |
| `Mahmudul Hassan` | `{{PROPRIETOR_NAME}}` |
| `24.02.2021` | `{{BG_DATE}}` |
| `info@handbl.com` | `{{EGP_EMAIL}}` |
| `HB/4515` | `{{MEMO_NO}}` |

3. For equipment table: replace the rows with a single row containing `{{EQUIPMENT_ROWS}}`
4. For manpower table: replace the rows with a single row containing `{{MANPOWER_ROWS}}`
5. Save as the template filename listed above.

### Full placeholder reference

```
{{TENDER_ID}}               Tender/Proposal ID number
{{INVITATION_REF_NO}}       e.g. "T-1/1757 Dated: 25/01/2021"
{{PACKAGE_NO}}              e.g. "e-GP-50/PW/Anowara/Sea-Dyke"
{{WORK_NAME}}               Full work description
{{WORK_NAME_SHORT}}         Shortened work name for headers
{{LOCATION}}                e.g. "Anowara, Chattogram"
{{PROCURING_ENTITY}}        Full procuring entity name
{{PROCURING_ENTITY_SHORT}}  e.g. "BWDB"
{{PE_DIVISION}}             e.g. "Chittagong O&M Division-1"
{{PE_ADDRESS}}              PE office address
{{EXECUTIVE_ENGINEER}}      Name of Executive Engineer
{{START_DATE}}              e.g. "15-Apr-2021"
{{COMPLETION_DATE}}         e.g. "30-Jun-2022"
{{COMPLETION_DATE_LONG}}    e.g. "30th June 2022"
{{BG_VALIDITY_DATE}}        e.g. "24-August-2021"
{{DOCUMENT_DATE}}           Date of document e.g. "25-02-2021"
{{BG_DATE}}                 Bank Guarantee date
{{TENDER_SECURITY_BDT}}     e.g. "Tk. 75,00,000.00"
{{TENDER_SECURITY_WORDS}}   e.g. "Seventy Five Lac"
{{BANK_NAME}}               e.g. "SBAC Bank Limited"
{{BANK_BRANCH}}             Bank branch
{{BANK_GUARANTEE_NO}}       BG number (blank — fill manually)
{{FIRM_NAME}}               Your firm/company name
{{FIRM_ADDRESS}}            Firm address
{{PROPRIETOR_NAME}}         Proprietor/authorized signatory name
{{EGP_EMAIL}}               e-GP registered email
{{MEMO_NO}}                 Internal memo number
{{CLOSING_DATE}}            Tender closing date
{{PUBLICATION_DATE}}        Tender publication date
{{JV_NAME}}                 JV name (if JV tender)
{{JV_DATE}}                 JV agreement date
{{JV_OFFICE_ADDRESS}}       JV registered office
{{JV_PHONE}}                JV phone
{{PARTNER_IN_CHARGE_NAME}}  Authorized partner name
{{PARTNER_IN_CHARGE_FIRM}}  Authorized partner firm name
```

---

## Step 3 — Configure your firm details

Open `run_local.py` and edit the `FIRM_CONFIG` block at the top:

```python
FIRM_CONFIG = {
    "firm_name":       "M/S Hassan & Brothers",
    "firm_address":    "Mahmud Tower ...",
    "proprietor_name": "Mahmudul Hassan",
    "egp_email":       "info@handbl.com",
    "bank_name":       "SBAC Bank Limited",
    "bank_branch":     "Gulshan Branch, Dhaka, Bangladesh",
    ...
}
```

You only do this once. These values are reused for every tender you process.

---

## Step 4 — Process a tender

### Single tender

1. Create a folder:
   ```
   tender_engine\input\541339\
   ```

2. Copy your 4 PDFs into it:
   ```
   1. Notice_541339.pdf
   2. TDS_1_541339.pdf
   3. TDS_2_541339.pdf
   4. BOQ_541339.pdf
   ```

3. Run:
   ```
   python run_local.py
   ```

4. Find your output in:
   ```
   tender_engine\output\541339\
   ```

### Batch mode (multiple tenders at once)

Drop each tender into its own subfolder inside `tender_engine\input\`:
```
tender_engine\input\
  541339\  ← 4 PDFs here
  541500\  ← 4 PDFs here
  541601\  ← 4 PDFs here
```

Then run:
```
python run_local.py --batch
```

All tenders are processed automatically.

---

## Output folder structure

```
tender_engine\output\
  541339\
    extracted_data.json           ← all extracted fields (inspect/verify)
    2. BG_HB_SBAC-541339.docx
    3. BG_Credit_Line_SBAC-541339.docx
    4. Equipment_Declaration-541339.docx
    5. Manpower_Declaration-541339.docx
    6. Methodology-541339.docx
    7. Work_Plan-541339.xlsx
    BOQ-541339.xlsx
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `pdfplumber not found` | Run: `pip install pdfplumber` |
| `python-docx not found` | Run: `pip install python-docx` |
| `openpyxl not found` | Run: `pip install openpyxl` |
| Template not found | Copy template DOCX files to `tender_engine/templates/docx/` |
| Wrong data extracted | Check `extracted_data.json` — edit values there and re-run generators |
| Placeholder not replaced | Make sure token is exactly `{{TOKEN_NAME}}` with no extra spaces |

---

## Architecture overview

```
run_local.py               ← you run this
  └── tender_engine/
        pipeline.py        ← orchestrates everything
        parser/
          pdf_reader.py    ← opens PDFs, extracts text/tables
          notice_parser.py ← extracts tender ID, dates, amounts from Notice
          tds_parser.py    ← extracts qualifications, equipment, manpower from TDS
          boq_parser.py    ← extracts BOQ items from BOQ PDF
        models/
          tender_data.py   ← single data model for all fields
        generators/
          docx_generator.py  ← fills DOCX templates with real values
          excel_generator.py ← builds BOQ + Work Plan Excel from scratch
        utils/
          text_utils.py    ← amount_to_words, date formatting, BDT formatting
          file_manager.py  ← folder creation, JSON saving, path resolution
        config/
          field_mapping.json ← maps field names to placeholder tokens
        templates/
          docx/            ← your master DOCX templates go here
          excel/           ← (Excel generated from scratch, no template needed)
        input/             ← drop tender PDF folders here
        output/            ← generated files appear here
```
