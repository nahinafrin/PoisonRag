@echo off
rem DEV check: PoisonGuard v5 on HotpotQA dev questions (targets 1-50), 6 poison rates. Writes to dev_v5\. Resumable.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
set BENCH_RESULTS=dev_v5
if not exist dev_v5 mkdir dev_v5
%PY% run_final.py --system poisonguard_v5 --ds hotpotqa --poison 5 1 3 --variant without_q --limit 50 >> dev_v5.log 2>&1
%PY% run_final.py --system poisonguard_v5 --ds hotpotqa --poison 0 --variant with_q --limit 50 >> dev_v5.log 2>&1
%PY% run_final.py --system poisonguard_v5 --ds hotpotqa --poison 4 2 --variant without_q --limit 50 >> dev_v5.log 2>&1
echo DONE > dev_v5.done
