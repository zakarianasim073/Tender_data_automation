@echo off
cd /d "%~dp0"
python -m py_compile local_dashboard.py batch_GEN.py batch_GEN_552225.py tender_engine\enhanced_runner.py tender_engine\sor\sor_parser.py tender_engine\sor\sor_models.py tender_engine\checker\rate_checker.py tender_engine\reports\report_generator.py tender_engine\context\context_editor.py tender_engine\local_features\checklist.py tender_engine\local_features\cache.py tender_engine\local_features\search_index.py tender_engine\local_features\compare.py tender_engine\local_features\approval.py tender_engine\local_features\review_export.py tender_engine\local_features\__init__.py > syntax_check.log 2>&1
echo EXITCODE:%ERRORLEVEL% >> syntax_check.log
