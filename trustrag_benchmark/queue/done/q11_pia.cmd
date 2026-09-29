@echo off
cd /d "C:\Users\sarke\Desktop\TrustRag\trustrag_benchmark"
set PYTHONIOENCODING=utf-8
set PY="C:\Users\sarke\Desktop\TrustRag\step4 dataset\.venv311\Scripts\python.exe"
set PG_ABLATE=
set BENCH_BACKBONE=
set BENCH_RESULTS=results
for %%D in (nq hotpotqa msmarco) do %PY% run_final.py --system poisonguard_v5 --ds %%D --variant pia --offset 50 --limit 50 >> v5_pia.log 2>&1
%PY% baselines.py --system vanilla --ds msmarco --variant pia --offset 50 --limit 50 >> v5_pia.log 2>&1
%PY% baselines.py --system trustrag --ds msmarco --variant pia --offset 50 --limit 50 >> v5_pia.log 2>&1
