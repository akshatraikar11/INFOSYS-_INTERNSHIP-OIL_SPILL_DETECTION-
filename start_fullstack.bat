@echo off
title DeepSpill Full-Stack
cd /d "%~dp0"
echo Starting DeepSpill full-stack environment...
deepspill-venv\Scripts\python.exe run_fullstack.py
pause
