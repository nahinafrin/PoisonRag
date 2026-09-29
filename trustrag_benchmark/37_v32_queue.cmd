@echo off
rem PoisonGuard-RAG v3.2 (joint-reading fallback). MS-MARCO FIRST = the untouched held-out test; then HotpotQA and NQ for the before/after picture.
rem Waits for 35_extra_ours (one pipeline process at a time). Resumable.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
:wait
if exist extra_ours.done goto go
timeout /t 60 /nobreak > nul
goto wait
:go
set BENCH_RESULTS=
%PY% run_final.py --system poisonguard_v32 --ds msmarco --poison 5 4 3 2 1 --variant without_q >> v32.log 2>&1
%PY% run_final.py --system poisonguard_v32 --ds msmarco --poison 0 --variant with_q >> v32.log 2>&1
%PY% run_final.py --system poisonguard_v32 --ds hotpotqa --poison 5 4 3 2 1 --variant without_q >> v32.log 2>&1
%PY% run_final.py --system poisonguard_v32 --ds hotpotqa --poison 0 --variant with_q >> v32.log 2>&1
%PY% run_final.py --system poisonguard_v32 --ds nq --poison 5 4 3 2 1 --variant without_q >> v32.log 2>&1
%PY% run_final.py --system poisonguard_v32 --ds nq --poison 0 --variant with_q >> v32.log 2>&1
%PY% score_table2.py > table2.log 2>&1
echo DONE > v32.done
