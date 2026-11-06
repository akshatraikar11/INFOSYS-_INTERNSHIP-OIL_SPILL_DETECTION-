@echo off
title DeepSpill AI - Enterprise 3-Tier Full-Stack Launcher
cd /d "%~dp0"
echo ===============================================================================
echo   DEEPSPILL AI: 3-TIER ENTERPRISE FULL-STACK ARCHITECTURE
echo   React Frontend (5173) + Express Backend (3001) + FastAPI Inference (8000)
echo ===============================================================================
echo.
echo [1/3] Launching Python FastAPI Inference Microservice on http://127.0.0.1:8000 ...
start "DeepSpill Inference" cmd /k "deepspill-venv\Scripts\python.exe -m uvicorn inference.server:app --host 127.0.0.1 --port 8000"
timeout /t 3 /nobreak >nul

echo [2/3] Launching Node.js Express Backend API Gateway on http://localhost:3001 ...
start "DeepSpill Backend" cmd /k "cd /d "%~dp0backend" && npm start"
timeout /t 2 /nobreak >nul

echo [3/3] Launching React (Vite) Production Dashboard on http://localhost:5173 ...
start "DeepSpill React Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo All 3 tiers initiated successfully!
echo Opening http://localhost:5173 in your default browser...
timeout /t 3 /nobreak >nul
start http://localhost:5173
echo.
echo Close individual service windows to terminate servers.
pause
