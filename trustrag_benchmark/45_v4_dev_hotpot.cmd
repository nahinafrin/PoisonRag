@echo off
rem DEV baseline: PoisonGuard v4 on ALL 50 HotpotQA dev questions (targets 1-50), 6 poison rates. Writes to dev_v4\ (test results untouched). Resumable.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
set BENCH_RESULTS=dev_v4
%PY% run_final.py --system poisonguard_v4 --ds hotpotqa --poison 5 4 3 2 1 --variant without_q --limit 50 >> dev_v4_full.log 2>&1
%PY% run_final.py --system poisonguard_v4 --ds hotpotqa --poison 0 --variant with_q --limit 50 >> dev_v4_full.log 2>&1
echo DONE > dev_v4_full.done
