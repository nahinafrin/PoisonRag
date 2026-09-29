@echo off
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PY="%~dp0..\step4 dataset\.venv311\Scripts\python.exe"
set GEN_SEEDS=99
set GEN_N=2
%PY% gen\build_general.py > gen\smoke.log 2>&1
set BENCH_RESULTS=smoke_general
if not exist smoke_general mkdir smoke_general
for %%D in (triviaqa_s99 twowiki_s99 squad_s99) do (
 %PY% run_final.py --system poisonguard_v5 --ds %%D --poison 5 --variant without_q >> gen\smoke.log 2>&1
 %PY% baselines.py --system closedbook --ds %%D --poison 0 --variant with_q >> gen\smoke.log 2>&1
)
%PY% baselines.py --system trustrag --ds squad_s99 --poison 5 --variant without_q >> gen\smoke.log 2>&1
echo SMOKE DONE >> gen\smoke.log
