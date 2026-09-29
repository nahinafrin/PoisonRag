@echo off
cd /d "%~dp0"
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*streamB*' -or $_.CommandLine -like '*streamC*' } | Where-Object { $_.Name -eq 'cmd.exe' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; 'cmd ' + $_.ProcessId }; Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*run_ours.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; 'py ' + $_.ProcessId }" > stop_ours.log 2>&1
