@echo off
rem Table-2 grid (poison 80/60/40%%) for PoisonGuard-RAG; waits for 32_final_ours to finish. Resumable.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
:wait
if not exist final_ours.done ( timeout /t 60 /nobreak > nul & goto wait )
%PY% fetch_data.py msmarco >> table2_ours.log 2>&1
%PY% run_final.py --ds nq --poison 4 3 2 --variant without_q >> table2_ours.log 2>&1
%PY% run_final.py --ds hotpotqa --poison 4 3 2 --variant without_q >> table2_ours.log 2>&1
%PY% run_final.py --ds msmarco --poison 5 1 0 --variant without_q >> table2_ours.log 2>&1
%PY% run_final.py --ds msmarco --poison 4 3 2 --variant without_q >> table2_ours.log 2>&1
%PY% table2.py > table2.log 2>&1
echo DONE > table2_ours.done
