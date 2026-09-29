@echo off
rem Restart helper: stops the stuck queue runner + benchmark python workers, restarts Ollama, starts the queue runner again.
cd /d "%~dp0"
echo %date% %time% RESTART requested >> queue\runner.log
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match '(run_final|baselines|gen_adaptive)\.py' -or ($_.Name -eq 'cmd.exe' -and $_.CommandLine -match '00_QUEUE_RUNNER') } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; $_.ProcessId }" > queue\restart.log 2>&1
taskkill /f /im "ollama app.exe" >> queue\restart.log 2>&1
taskkill /f /im ollama.exe >> queue\restart.log 2>&1
taskkill /f /im ollama_llama_server.exe >> queue\restart.log 2>&1
timeout /t 5 /nobreak >nul
if exist "%LOCALAPPDATA%\Programs\Ollama\ollama app.exe" (start "" "%LOCALAPPDATA%\Programs\Ollama\ollama app.exe") else (start "" /min ollama serve)
timeout /t 15 /nobreak >nul
start "PoisonGuard queue runner" cmd /c "%~dp000_QUEUE_RUNNER.cmd"
echo %date% %time% RESTART done >> queue\runner.log
