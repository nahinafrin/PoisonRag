@echo off
rem Final evaluation, PoisonGuard-RAG. NQ (development set) then HotpotQA (held-out test set). Resumable.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
for %%D in (nq hotpotqa) do (
  %PY% run_final.py --ds %%D --poison 5 1 --variant without_q >> final_ours.log 2>&1
  %PY% run_final.py --ds %%D --poison 5 1 0 --variant with_q >> final_ours.log 2>&1
  %PY% run_final.py --ds %%D --variant pia >> final_ours.log 2>&1
)
%PY% score.py > score_latest.log 2>&1
echo DONE > final_ours.done
