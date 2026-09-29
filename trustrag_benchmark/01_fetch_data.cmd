@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
%PY% fetch_data.py nq hotpotqa msmarco > fetch_data.log 2>&1
echo DONE > fetch_data.done
