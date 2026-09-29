@echo off
rem Stops the old ours_v1 run and smoke-tests the final PoisonGuard-RAG package on 3 questions.
cd /d "%~dp0"
call 92_stop_ours.cmd
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
set BENCH_RESULTS=smoke_final
%PY% run_final.py --ds nq --poison 5 --variant without_q --limit 3 > smoke_final.log 2>&1
%PY% run_final.py --ds nq --variant pia --limit 2 >> smoke_final.log 2>&1
echo DONE > smoke_final.done
