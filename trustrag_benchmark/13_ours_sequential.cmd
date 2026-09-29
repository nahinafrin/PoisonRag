@echo off
rem Our systems, run ONE at a time (two full pipelines in parallel deadlocked on this laptop). Resumable.
cd /d "%~dp0"
call 92_stop_ours.cmd
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
%PY% run_ours.py --system ours_v21 --ds nq --poison 5 1 --variant with_q >> streamBC.log 2>&1
%PY% run_ours.py --system ours_v2 --ds nq --poison 5 1 --variant without_q >> streamBC.log 2>&1
%PY% run_ours.py --system ours_v21 --ds nq --poison 5 1 --variant without_q >> streamBC.log 2>&1
%PY% run_ours.py --system ours_v21 --ds nq --poison 0 --variant with_q >> streamBC.log 2>&1
%PY% run_ours.py --system ours_v2 --ds nq --poison 0 --variant with_q >> streamBC.log 2>&1
%PY% run_ours.py --system ours_v1 --ds nq --poison 5 1 0 --variant with_q >> streamBC.log 2>&1
%PY% score.py > score_latest.log 2>&1
echo DONE > streamBC.done
