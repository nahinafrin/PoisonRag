@echo off
rem FINAL TEST: PoisonGuard-RAG v4 on the held-out TEST half (targets 51-100), 50 questions x 6 poison rates x 3 datasets = 900 runs. Resumable.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set BENCH_RESULTS=
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
for %%D in (nq hotpotqa msmarco) do (
  %PY% run_final.py --system poisonguard_v4 --ds %%D --poison 5 4 3 2 1 --variant without_q --offset 50 --limit 50 >> v4_test.log 2>&1
  %PY% run_final.py --system poisonguard_v4 --ds %%D --poison 0 --variant with_q --offset 50 --limit 50 >> v4_test.log 2>&1
)
%PY% score_v4_test.py > score_v4_test.log 2>&1
echo DONE > v4_test.done
