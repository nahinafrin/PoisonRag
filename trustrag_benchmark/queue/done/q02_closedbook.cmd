@echo off
cd /d "C:\Users\sarke\Desktop\TrustRag\trustrag_benchmark"
set PYTHONIOENCODING=utf-8
set PY="C:\Users\sarke\Desktop\TrustRag\step4 dataset\.venv311\Scripts\python.exe"
set PG_ABLATE=
set BENCH_BACKBONE=
set BENCH_RESULTS=results
for %%D in (nq hotpotqa msmarco) do %PY% baselines.py --system closedbook --ds %%D --poison 0 --variant with_q --limit 100 >> closedbook.log 2>&1
