@echo off
rem Stream B: thesis pipeline v2 (with the new Steps 6b + 9d), then v1 as-locked. Resumable.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
%PY% run_ours.py --system ours_v2 --ds nq --poison 5 1 --variant with_q >> streamB.log 2>&1
%PY% run_ours.py --system ours_v2 --ds nq --poison 5 1 --variant without_q >> streamB.log 2>&1
%PY% run_ours.py --system ours_v2 --ds nq --poison 0 --variant with_q >> streamB.log 2>&1
%PY% run_ours.py --system ours_v1 --ds nq --poison 5 1 0 --variant with_q >> streamB.log 2>&1
%PY% score.py > score_latest.log 2>&1
echo DONE > streamB.done
