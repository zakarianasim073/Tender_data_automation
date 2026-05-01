# JV Context Variables

Use these keys in `tender_engine/input/<tender_id>/context.json`.
Use the matching uppercase token in DOCX templates, for example `{{JV_NAME}}` or `{{PARTNER1_FIRM_NAME}}`.

## Main tender variables

- `tender_id`
- `zone`
- `firm_name`
- `firm_address`
- `proprietor_name`
- `egp_email`
- `bank_name`
- `bank_branch`
- `memo_no`
- `bank_guarantee_no`
- `work_months`

## JV variables

- `is_jv`
- `jv_name`
- `jv_date`
- `jv_partner_count`
- `jv_share_text`
- `jv_office_address`
- `jv_phone`
- `lead_partner`
- `nominated_partner`
- `partner_in_charge_name`
- `partner_in_charge_firm`

## Partner 1 variables

- `partner1_code`
- `partner1_firm_name`
- `partner1_legal_type`
- `partner1_address`
- `partner1_signatory_name`
- `partner1_position`
- `partner1_share_percent`
- `partner1_share_words`

## Partner 2 variables

- `partner2_code`
- `partner2_firm_name`
- `partner2_legal_type`
- `partner2_address`
- `partner2_signatory_name`
- `partner2_position`
- `partner2_share_percent`
- `partner2_share_words`

## Partner 3 variables

- `partner3_code`
- `partner3_firm_name`
- `partner3_legal_type`
- `partner3_address`
- `partner3_signatory_name`
- `partner3_position`
- `partner3_share_percent`
- `partner3_share_words`

## Repeating table placeholders

For DOCX tables, use these marker rows:

- `{{EQUIPMENT_ROWS}}` for equipment rows
- `{{MANPOWER_ROWS}}` for manpower rows
- `{{JV_PARTNER_ROWS}}` for JV partner rows

For normal fields, uppercase the key and wrap it in braces. Example: `partner2_address` becomes `{{PARTNER2_ADDRESS}}`.
