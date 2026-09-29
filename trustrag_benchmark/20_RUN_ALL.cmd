@echo off
rem ONE-CLICK: stops any running benchmark workers, then runs Stream A (Vanilla+TrustRAG) and Stream B (ours) in parallel.
rem Resumable: finished queries in results\ are skipped. Scores are written to RESULTS_trustrag_comparison.md.
cd /d "%~dp0"
call 91_stop_streams.cmd
start "StreamA-baselines" /min cmd /c 10_streamA_baselines.cmd
start "Ours-sequential" /min cmd /c 13_ours_sequential.cmd
