@echo off
cd /d "D:\Work space\Tender_data_automation-main\Tender_data_automation-main\backend"
python -c "from app.main import app; print('backend import ok')" > "D:\Work space\Tender_data_automation-main\Tender_data_automation-main\backend_import.log" 2>&1
echo EXITCODE:%ERRORLEVEL% >> "D:\Work space\Tender_data_automation-main\Tender_data_automation-main\backend_import.log"
