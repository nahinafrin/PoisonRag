@echo off
cd /d "C:\Users\sarke\Desktop\TrustRag\trustrag_benchmark"
set PYTHONIOENCODING=utf-8
set PG_ABLATE=
set BENCH_BACKBONE=
if not exist results_general mkdir results_general
"C:\Users\sarke\Desktop\TrustRag\step4 dataset\.venv311\Scripts\python.exe" gen\run_general.py >> general.log 2>&1
