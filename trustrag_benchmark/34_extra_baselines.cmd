@echo off
rem Table-2 extension (TrustRAG paper protocol = poison WITHOUT question prefix): 80/60/40% on NQ+HotpotQA, then all rates on MS-MARCO. Resumable.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
%PY% fetch_data.py msmarco >> extra_baselines.log 2>&1
for %%D in (nq hotpotqa) do (
  %PY% baselines.py --system vanilla --ds %%D --poison 4 3 2 --variant without_q >> extra_baselines.log 2>&1
  %PY% baselines.py --system trustrag --ds %%D --poison 4 3 2 --variant without_q >> extra_baselines.log 2>&1
)
%PY% baselines.py --system vanilla --ds msmarco --poison 5 4 3 2 1 --variant without_q >> extra_baselines.log 2>&1
%PY% baselines.py --system vanilla --ds msmarco --poison 0 --variant with_q >> extra_baselines.log 2>&1
%PY% baselines.py --system trustrag --ds msmarco --poison 5 4 3 2 1 --variant without_q >> extra_baselines.log 2>&1
%PY% baselines.py --system trustrag --ds msmarco --poison 0 --variant with_q >> extra_baselines.log 2>&1
%PY% score_table2.py > table2.log 2>&1
echo DONE > extra_baselines.done
