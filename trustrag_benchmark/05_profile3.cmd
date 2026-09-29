@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
set BENCH_RESULTS=profile3
%PY% baselines.py --system trustrag --ds nq --poison 1 --limit 3 > profile3.log 2>&1
%PY% run_ours.py --system ours_v2 --ds nq --poison 1 --limit 4 >> profile3.log 2>&1
echo DONE > profile3.done
