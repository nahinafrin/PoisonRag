@echo off
rem Queue the Table-2 grid behind the running final runs (both wait automatically).
cd /d "%~dp0"
start "Table2-PoisonGuard" /min cmd /c 34_table2_ours.cmd
start "Table2-baselines" /min cmd /c 35_table2_baselines.cmd
