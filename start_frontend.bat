@echo off
setlocal
cd /d "D:\Work space\Tender_data_automation-main\Tender_data_automation-main\frontend"
echo Frontend folder: %CD%
echo Installing/checking frontend dependencies...
call npm install --include=dev
if errorlevel 1 (
  echo.
  echo Frontend dependency install failed. Check the error above.
  pause
  exit /b 1
)

echo.
echo Starting Vite frontend at http://127.0.0.1:5173
call npm run start -- --host 127.0.0.1 --port 5173
pause
