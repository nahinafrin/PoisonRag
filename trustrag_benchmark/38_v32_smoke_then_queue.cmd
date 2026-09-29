@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
set BENCH_RESULTS=smoke_v32
%PY% run_final.py --system poisonguard_v32 --ds hotpotqa --poison 1 --variant without_q --limit 4 > smoke_v32.log 2>&1
echo DONE > smoke_v32.done
set BENCH_RESULTS=
start "v32-queue" /min cmd /c 37_v32_queue.cmd
