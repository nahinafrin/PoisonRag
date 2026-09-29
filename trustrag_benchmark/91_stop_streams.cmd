@echo off
rem Stops BOTH benchmark streams (the .cmd wrappers first, then their python workers). Results so far are kept; re-launch resumes.
cd /d "%~dp0"
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*_stream*' -and $_.Name -eq 'cmd.exe' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; 'cmd ' + $_.ProcessId }; Get-CimInstance Win32_Process | Where-Object { ($_.CommandLine -like '*run_ours.py*') -or ($_.CommandLine -like '*baselines.py*') } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; 'py ' + $_.ProcessId }" > stop_streams.log 2>&1
