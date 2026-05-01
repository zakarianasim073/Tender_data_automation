@echo off
cd /d "D:\Work space\Tender_data_automation-main\Tender_data_automation-main"
python setup_and_run.py > setup_log.txt 2>&1
echo Exit code: %ERRORLEVEL%
