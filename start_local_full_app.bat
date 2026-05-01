@echo off
set "ROOT=D:\Work space\Tender_data_automation-main\Tender_data_automation-main"

echo Starting TenderFlow Local...
echo.
start "TenderFlow Backend" "%ROOT%\start_backend.bat"
timeout /t 5 /nobreak >nul
start "TenderFlow Frontend" "%ROOT%\start_frontend.bat"

echo.
echo Open this in your browser after both windows finish starting:
echo http://127.0.0.1:5173
echo.
echo Backend health page:
echo http://127.0.0.1:8001/health
echo.
pause
