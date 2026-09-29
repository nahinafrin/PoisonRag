@echo off
rem Table-2 grid (poison 80/60/40%%) for Vanilla RAG and TrustRAG; waits for 33_final_baselines. Resumable.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
:wait
if not exist final_baselines.done ( timeout /t 60 /nobreak > nul & goto wait )
for %%S in (vanilla trustrag) do (
  %PY% baselines.py --system %%S --ds nq --poison 4 3 2 --variant without_q >> table2_baselines.log 2>&1
  %PY% baselines.py --system %%S --ds hotpotqa --poison 4 3 2 --variant without_q >> table2_baselines.log 2>&1
)
:wait2
if not exist data\msmarco_adv_scores.json ( timeout /t 60 /nobreak > nul & goto wait2 )
for %%S in (vanilla trustrag) do (
  %PY% baselines.py --system %%S --ds msmarco --poison 5 1 0 --variant without_q >> table2_baselines.log 2>&1
  %PY% baselines.py --system %%S --ds msmarco --poison 4 3 2 --variant without_q >> table2_baselines.log 2>&1
)
%PY% table2.py > table2.log 2>&1
echo DONE > table2_baselines.done
