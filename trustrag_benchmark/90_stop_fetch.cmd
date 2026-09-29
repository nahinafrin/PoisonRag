@echo off
cd /d "%~dp0"
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*fetch_data.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; $_.ProcessId }" > stop_fetch.log 2>&1
