@echo off
cd /d "%~dp0"
python -m compileall -q . > syntax_check_all.log 2>&1
echo EXITCODE:%ERRORLEVEL% >> syntax_check_all.log
