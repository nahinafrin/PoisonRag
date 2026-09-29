@echo off
cd /d "C:\Users\sarke\Desktop\TrustRag\trustrag_benchmark"
set PYTHONIOENCODING=utf-8
set PY="C:\Users\sarke\Desktop\TrustRag\step4 dataset\.venv311\Scripts\python.exe"
set PG_ABLATE=
set BENCH_BACKBONE=
set BENCH_RESULTS=dev_v5b
for %%D in (nq msmarco) do (
  %PY% run_final.py --system poisonguard_v5 --ds %%D --poison 5 1 3 --variant without_q --limit 50 >> dev_v5b.log 2>&1
  %PY% run_final.py --system poisonguard_v5 --ds %%D --poison 0 --variant with_q --limit 50 >> dev_v5b.log 2>&1
)
