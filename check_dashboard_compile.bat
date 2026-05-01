@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  set "PY=.venv\Scripts\python.exe"
) else (
  set "PY=python"
)
%PY% -m py_compile local_dashboard.py tender_engine\checker\description_matcher.py > dashboard_compile.log 2>&1
%PY% -c "import gradio as gr; print('gradio', gr.__version__, 'blocks', hasattr(gr, 'Blocks'))" >> dashboard_compile.log 2>&1
type dashboard_compile.log
