@echo off
cd /d "%~dp0"
"%~dp0..\step4 dataset\.venv311\Scripts\python.exe" gen\probe_hf.py > gen\probe.log 2>&1
