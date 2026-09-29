@echo off
cd /d "C:\Users\sarke\Desktop\TrustRag\trustrag_benchmark"
set PYTHONIOENCODING=utf-8
set PY="C:\Users\sarke\Desktop\TrustRag\step4 dataset\.venv311\Scripts\python.exe"
set PG_ABLATE=
set BENCH_BACKBONE=
set PG_ABLATE=no_arbitration
set BENCH_RESULTS=abl_no_arbitration
if not exist abl_no_arbitration mkdir abl_no_arbitration
for %%D in (nq hotpotqa) do %PY% run_final.py --system poisonguard_v5 --ds %%D --poison 5 3 1 --variant without_q --offset 50 --limit 50 >> ablation.log 2>&1
set PG_ABLATE=no_internal
set BENCH_RESULTS=abl_no_internal
if not exist abl_no_internal mkdir abl_no_internal
for %%D in (nq hotpotqa) do %PY% run_final.py --system poisonguard_v5 --ds %%D --poison 5 3 1 --variant without_q --offset 50 --limit 50 >> ablation.log 2>&1
set PG_ABLATE=no_consensus
set BENCH_RESULTS=abl_no_consensus
if not exist abl_no_consensus mkdir abl_no_consensus
for %%D in (nq hotpotqa) do %PY% run_final.py --system poisonguard_v5 --ds %%D --poison 5 3 1 --variant without_q --offset 50 --limit 50 >> ablation.log 2>&1
set PG_ABLATE=no_decompose
set BENCH_RESULTS=abl_no_decompose
if not exist abl_no_decompose mkdir abl_no_decompose
%PY% run_final.py --system poisonguard_v5 --ds hotpotqa --poison 5 3 1 --variant without_q --offset 50 --limit 50 >> ablation.log 2>&1
set PG_ABLATE=no_lonefix
set BENCH_RESULTS=abl_no_lonefix
if not exist abl_no_lonefix mkdir abl_no_lonefix
%PY% run_final.py --system poisonguard_v5 --ds hotpotqa --poison 5 3 1 --variant without_q --offset 50 --limit 50 >> ablation.log 2>&1
set PG_ABLATE=
