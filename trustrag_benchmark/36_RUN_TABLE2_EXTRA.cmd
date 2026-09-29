@echo off
rem Starts the Table-2 extension streams (does NOT stop the running final runs).
cd /d "%~dp0"
start "Extra-baselines" /min cmd /c 34_extra_baselines.cmd
start "Extra-PoisonGuard" /min cmd /c 35_extra_ours.cmd
