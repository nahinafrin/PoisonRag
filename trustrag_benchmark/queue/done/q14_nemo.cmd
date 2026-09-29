@echo off
cd /d "C:\Users\sarke\Desktop\TrustRag\trustrag_benchmark"
set PYTHONIOENCODING=utf-8
set PY="C:\Users\sarke\Desktop\TrustRag\step4 dataset\.venv311\Scripts\python.exe"
set PG_ABLATE=
set BENCH_BACKBONE=
ollama pull mistral-nemo >> nemo.log 2>&1
set BENCH_BACKBONE=mistral-nemo
set BENCH_RESULTS=results_nemo
if not exist results_nemo mkdir results_nemo
for %%D in (nq hotpotqa msmarco) do %PY% baselines.py --system closedbook --ds %%D --poison 0 --variant with_q --offset 50 --limit 50 >> nemo.log 2>&1
for %%D in (nq hotpotqa msmarco) do (
  %PY% run_final.py --system poisonguard_v5 --ds %%D --poison 5 4 3 2 1 --variant without_q --offset 50 --limit 50 >> nemo.log 2>&1
  %PY% run_final.py --system poisonguard_v5 --ds %%D --poison 0 --variant with_q --offset 50 --limit 50 >> nemo.log 2>&1
)
for %%D in (nq hotpotqa msmarco) do %PY% baselines.py --system vanilla --ds %%D --poison 5 3 1 0 --variant without_q --offset 50 --limit 50 >> nemo.log 2>&1
set BENCH_BACKBONE=
