@echo off
rem Stops the v4 dev check (only run_final.py workers and the 40_v4_dev queue), then starts the 900-run v4 test.
cd /d "%~dp0"
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match '40_v4_dev' -or $_.CommandLine -match 'run_final\.py' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; $_.ProcessId }" > stop_dev.log 2>&1
start "v4-TEST-900" /min cmd /c 43_v4_test.cmd
