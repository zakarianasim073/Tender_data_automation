@echo off
cd /d "%~dp0"
set PY=.venv\Scripts\python.exe
if not exist "%PY%" set PY=python
%PY% -m py_compile tender_engine\models\tender_data.py tender_engine\context\context_editor.py tender_engine\generators\docx_generator.py tender_engine\pipeline.py tender_engine\parser\pdf_lookup.py local_dashboard.py > verify_upgrade.log 2>&1
if errorlevel 1 goto done
%PY% -c "import json; json.load(open(r'tender_engine\input\601115\context.json', encoding='utf-8')); import local_dashboard; from tender_engine.pipeline import _build_tender_data; print('VERIFY_OK')" >> verify_upgrade.log 2>&1
:done
type verify_upgrade.log
