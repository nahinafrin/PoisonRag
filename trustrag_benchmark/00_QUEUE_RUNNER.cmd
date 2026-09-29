@echo off
rem QUEUE RUNNER - double-click ONCE. Runs every job file dropped into queue\ (alphabetical), one at a time,
rem then moves it to queue\done\. Polls every 30 s. To stop after the current job: create an empty file queue\STOP.
title PoisonGuard queue runner
cd /d "%~dp0"
if not exist queue mkdir queue
if not exist queue\done mkdir queue\done
echo %date% %time% RUNNER STARTED >> queue\runner.log
:loop
if exist queue\STOP (
  del queue\STOP
  echo %date% %time% RUNNER STOPPED >> queue\runner.log
  exit /b
)
for %%F in (queue\*.cmd) do (
  echo %date% %time% START %%~nxF >> queue\runner.log
  call "%%F"
  cd /d "%~dp0"
  move /y "%%F" queue\done\ >nul
  echo %date% %time% END %%~nxF >> queue\runner.log
  goto loop
)
echo %date% %time% > queue\heartbeat.txt
timeout /t 30 /nobreak >nul
goto loop
