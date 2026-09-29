@echo off
cd /d "%~dp0"
start "v4-dev" /min cmd /c 40_v4_dev.cmd
start "trustrag-fill" /min cmd /c 41_trustrag_msmarco_fill.cmd
