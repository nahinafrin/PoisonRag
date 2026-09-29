@echo off
cd /d "C:\Users\sarke\Desktop\TrustRag\trustrag_benchmark"
set PYTHONIOENCODING=utf-8
set PY="C:\Users\sarke\Desktop\TrustRag\step4 dataset\.venv311\Scripts\python.exe"
set PG_ABLATE=
set BENCH_BACKBONE=mistral-nemo
set BENCH_RESULTS=results_nemo
rem TrustRAG (official code) on Mistral-Nemo-12B, same threat model / questions 51-100 as PoisonGuard-RAG. Most informative rates first.
for %%D in (nq hotpotqa msmarco) do %PY% baselines.py --system trustrag --ds %%D --poison 5 1 3 --variant without_q --offset 50 --limit 50 >> nemo_trustrag.log 2>&1
for %%D in (nq hotpotqa msmarco) do %PY% baselines.py --system trustrag --ds %%D --poison 0 --variant with_q --offset 50 --limit 50 >> nemo_trustrag.log 2>&1
for %%D in (nq hotpotqa msmarco) do %PY% baselines.py --system trustrag --ds %%D --poison 4 2 --variant without_q --offset 50 --limit 50 >> nemo_trustrag.log 2>&1
set BENCH_BACKBONE=
