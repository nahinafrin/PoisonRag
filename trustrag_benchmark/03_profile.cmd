@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
set BENCH_RESULTS=profile
%PY% run_ours.py --system ours_v2 --ds nq --poison 1 --limit 6 > profile.log 2>&1
%PY% baselines.py --system trustrag --ds nq --poison 1 --limit 3 >> profile.log 2>&1
%PY% baselines.py --system vanilla --ds nq --poison 1 --limit 3 >> profile.log 2>&1
echo DONE > profile.done
