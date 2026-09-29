@echo off
rem Table-2 extension for PoisonGuard-RAG. Waits until 32_final_ours finishes (one pipeline at a time), then runs. Resumable.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
:wait
if exist final_ours.done goto go
timeout /t 60 /nobreak > nul
goto wait
:go
for %%D in (nq hotpotqa) do (
  %PY% run_final.py --ds %%D --poison 4 3 2 --variant without_q >> extra_ours.log 2>&1
)
:waitms
if exist data\msmarco_adv_scores.json goto goms
timeout /t 60 /nobreak > nul
goto waitms
:goms
%PY% run_final.py --ds msmarco --poison 5 4 3 2 1 --variant without_q >> extra_ours.log 2>&1
%PY% run_final.py --ds msmarco --poison 0 --variant with_q >> extra_ours.log 2>&1
%PY% score_table2.py > table2.log 2>&1
echo DONE > extra_ours.done
