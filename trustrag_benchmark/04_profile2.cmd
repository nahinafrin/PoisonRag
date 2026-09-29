@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
set BENCH_RESULTS=profile2
%PY% ollama_speed.py > ollama_speed.log 2>&1
%PY% run_ours.py --system ours_v2 --ds nq --poison 1 --limit 5 > profile2.log 2>&1
echo DONE > profile2.done
