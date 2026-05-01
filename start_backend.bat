@echo off
setlocal
cd /d "D:\Work space\Tender_data_automation-main\Tender_data_automation-main"

if not exist ".venv\Scripts\python.exe" (
  echo Creating local Python virtual environment in .venv ...
  py -3.10 -m venv .venv
  if errorlevel 1 python -m venv .venv
)

echo Installing/checking backend dependencies inside local .venv ...
".venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
if errorlevel 1 (
  echo.
  echo Dependency install failed. Check the error above.
  pause
  exit /b 1
)

echo.
echo Checking backend import ...
cd /d "D:\Work space\Tender_data_automation-main\Tender_data_automation-main\backend"
"..\.venv\Scripts\python.exe" -c "from app.main import app; print('backend import ok')"
if errorlevel 1 (
  echo.
  echo Backend import failed. Check the error above.
  pause
  exit /b 1
)

echo.
echo Starting FastAPI backend at http://127.0.0.1:8001
"..\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8001
pause
