@echo off
setlocal
cd /d "%~dp0.."
set LOG=smoke_test_50\master_log.txt
echo === Smoke test launcher starting === > "%LOG%"
call .venv311\Scripts\activate.bat >> "%LOG%" 2>&1
echo Checking Ollama... >> "%LOG%"
powershell -NoProfile -Command "try { (Invoke-WebRequest -Uri http://localhost:11434/api/tags -UseBasicParsing -TimeoutSec 3) | Out-Null; Write-Output 'OLLAMA_UP' } catch { Write-Output 'OLLAMA_DOWN' }" >> "%LOG%" 2>&1
findstr /C:"OLLAMA_DOWN" "%LOG%" >nul
if %ERRORLEVEL%==0 (
    echo Ollama not reachable - attempting to start... >> "%LOG%"
    start "" ollama serve
    timeout /t 8 /nobreak >nul
)
echo Running smoke test PowerShell script... >> "%LOG%"
powershell -NoProfile -ExecutionPolicy Bypass -File "smoke_test_50\run_smoke_test.ps1" >> "%LOG%" 2>&1
echo DONE> "smoke_test_50\DONE.marker"
echo === Finished, see %LOG% and smoke_test_50\DONE.marker === >> "%LOG%"
pause
