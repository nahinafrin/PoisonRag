@echo off
rem Stops EVERY benchmark worker (all .cmd queues and all python runners). Results so far are kept.
cd /d "%~dp0"
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'cmd.exe' -and ($_.CommandLine -match '(_stream|_final_|_extra_|_v32_|_table2|_ours_sequential|RUN_)') } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; 'cmd ' + $_.ProcessId }; Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match '(run_final|baselines|run_ours)\.py' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; 'py ' + $_.ProcessId }" > stop_all.log 2>&1
