@echo off
title DeepSpill AI - Cyber-Maritime Mission Control
cd /d "%~dp0"
echo ===============================================================================
echo   DEEPSPILL AI: AUTONOMOUS SATELLITE RADAR AND OPTICAL OIL SPILL HUD
echo   Infosys Springboard AI 6.0 -- Master Project Milestone 4 Streamlit System
echo ===============================================================================
echo.
echo Launching Streamlit mission control dashboard on http://localhost:8501 ...
echo.
deepspill-venv\Scripts\streamlit.exe run streamlit_app.py --server.port 8501 --server.headless false
pause
