@echo off
title DeepSpill AI - Enterprise Full-Stack Launcher
cd /d "%~dp0"
echo ===============================================================================
echo   DEEPSPILL AI: 3-TIER ENTERPRISE FULL-STACK LAUNCHER
echo   React Frontend (5173) + Express Backend (3001) + FastAPI Inference (8000)
echo ===============================================================================
echo.
deepspill-venv\Scripts\python.exe run_fullstack.py
pause
