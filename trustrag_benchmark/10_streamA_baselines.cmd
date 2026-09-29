@echo off
rem Stream A: Vanilla RAG + TrustRAG (GPU-bound). Resumable: re-running skips finished queries.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
%PY% baselines.py --system vanilla --ds nq --poison 5 1 0 --variant with_q >> streamA.log 2>&1
%PY% baselines.py --system vanilla --ds nq --poison 5 1 --variant without_q >> streamA.log 2>&1
%PY% baselines.py --system trustrag --ds nq --poison 5 1 --variant with_q >> streamA.log 2>&1
%PY% baselines.py --system trustrag --ds nq --poison 5 1 --variant without_q >> streamA.log 2>&1
%PY% baselines.py --system trustrag --ds nq --poison 0 --variant with_q >> streamA.log 2>&1
%PY% score.py > score_latest.log 2>&1
echo DONE > streamA.done
