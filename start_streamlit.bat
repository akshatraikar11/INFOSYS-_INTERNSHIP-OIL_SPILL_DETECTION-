@echo off
title DeepSpill Streamlit
cd /d "%~dp0"
echo Starting DeepSpill Streamlit application on http://localhost:8501...
deepspill-venv\Scripts\streamlit.exe run streamlit_app.py --server.port 8501 --server.headless false
pause
