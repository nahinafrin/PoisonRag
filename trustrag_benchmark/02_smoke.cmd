@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set RESULTS_SUFFIX=
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
set BENCH_RESULTS=smoke
%PY% baselines.py --system vanilla --ds nq --poison 5 1 --limit 5 > smoke.log 2>&1
%PY% baselines.py --system trustrag --ds nq --poison 5 1 --limit 5 >> smoke.log 2>&1
%PY% run_ours.py --system ours_v2 --ds nq --poison 5 1 --limit 5 >> smoke.log 2>&1
%PY% run_ours.py --system ours_v1 --ds nq --poison 5 --limit 3 >> smoke.log 2>&1
%PY% score.py >> smoke.log 2>&1
echo DONE > smoke.done
