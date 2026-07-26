@echo off
title Claude Panel - Silently start both services

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

:: Start backend (FastAPI :10016) using venv Python
start /B /MIN "" ".venv\Scripts\python" "%ROOT_DIR%main.py" > "%ROOT_DIR%backend.log" 2>&1

:: Start frontend (Vite :10014)
cd /d "%ROOT_DIR%frontend"
start /B /MIN "" npx vite --host 0.0.0.0 --port 10014 > "%ROOT_DIR%frontend.log" 2>&1

cd /d "%ROOT_DIR%"
echo Claude Panel started successfully.
echo Frontend: http://localhost:10014
echo Backend:  http://localhost:10016
