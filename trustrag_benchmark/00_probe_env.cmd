@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
%PY% -m pip install rouge_score > probe_pip.log 2>&1
%PY% probe_env.py > probe_env.log 2>&1
echo DONE > probe_env.done
