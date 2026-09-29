@echo off
rem DEV check of PoisonGuard v4 on the first 20 dev questions (targets 1-50 = development half).
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
set BENCH_RESULTS=dev_v4
%PY% run_final.py --system poisonguard_v4 --ds hotpotqa --poison 5 1 --variant without_q --limit 20 >> dev_v4.log 2>&1
%PY% run_final.py --system poisonguard_v4 --ds hotpotqa --poison 0 --variant with_q --limit 20 >> dev_v4.log 2>&1
%PY% run_final.py --system poisonguard_v4 --ds nq --poison 5 1 --variant without_q --limit 20 >> dev_v4.log 2>&1
%PY% run_final.py --system poisonguard_v4 --ds msmarco --poison 5 --variant without_q --limit 20 >> dev_v4.log 2>&1
echo DONE > dev_v4.done
