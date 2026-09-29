@echo off
rem ONE-CLICK final evaluation: stops old workers, runs baselines and PoisonGuard-RAG in parallel. Resumable.
cd /d "%~dp0"
call 91_stop_streams.cmd
call 92_stop_ours.cmd
start "Final-baselines" /min cmd /c 33_final_baselines.cmd
start "Final-PoisonGuard" /min cmd /c 32_final_ours.cmd
