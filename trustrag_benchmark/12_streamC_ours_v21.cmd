@echo off
rem Stream C: ours v2.1 (reasoned internal knowledge in Step 9d). Resumable.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
%PY% run_ours.py --system ours_v21 --ds nq --poison 5 1 --variant with_q >> streamC.log 2>&1
%PY% run_ours.py --system ours_v21 --ds nq --poison 5 1 --variant without_q >> streamC.log 2>&1
%PY% run_ours.py --system ours_v21 --ds nq --poison 0 --variant with_q >> streamC.log 2>&1
%PY% score.py > score_latest.log 2>&1
echo DONE > streamC.done
