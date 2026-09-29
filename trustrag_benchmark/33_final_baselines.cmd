@echo off
rem Baselines for the final evaluation: PIA on NQ, then everything on HotpotQA (held-out). Resumable.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
%PY% baselines.py --system vanilla --ds nq --variant pia >> final_baselines.log 2>&1
%PY% baselines.py --system trustrag --ds nq --variant pia >> final_baselines.log 2>&1
%PY% baselines.py --system vanilla --ds hotpotqa --poison 5 1 --variant without_q >> final_baselines.log 2>&1
%PY% baselines.py --system vanilla --ds hotpotqa --poison 5 1 0 --variant with_q >> final_baselines.log 2>&1
%PY% baselines.py --system vanilla --ds hotpotqa --variant pia >> final_baselines.log 2>&1
%PY% baselines.py --system trustrag --ds hotpotqa --poison 5 1 --variant without_q >> final_baselines.log 2>&1
%PY% baselines.py --system trustrag --ds hotpotqa --poison 5 1 0 --variant with_q >> final_baselines.log 2>&1
%PY% baselines.py --system trustrag --ds hotpotqa --variant pia >> final_baselines.log 2>&1
%PY% score.py > score_latest.log 2>&1
echo DONE > final_baselines.done
