@echo off
rem Completes TrustRAG on MS-MARCO for the TEST half (targets 51-100). Resumable.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
%PY% baselines.py --system trustrag --ds msmarco --poison 1 --variant without_q --offset 50 --limit 50 >> fill.log 2>&1
%PY% baselines.py --system trustrag --ds msmarco --poison 0 --variant with_q --offset 50 --limit 50 >> fill.log 2>&1
echo DONE > fill.done
