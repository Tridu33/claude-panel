@echo off
title Claude Panel - Start frontend + backend

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

echo ========================================
echo   Claude Panel Starting...
echo   Frontend : http://localhost:10014
echo   Backend  : http://localhost:10016
echo ========================================
echo.

echo [1/2] Starting backend (FastAPI :10016)...
start "Claude-Panel-Backend" /B /MIN ".venv\Scripts\python" "%ROOT_DIR%main.py"

echo [2/2] Starting frontend (Vite :10014)...
cd /d "%ROOT_DIR%frontend"
start "Claude-Panel-Frontend" /B /MIN npx vite --host 0.0.0.0 --port 10014

cd /d "%ROOT_DIR%"
echo.
echo Done!
echo.
echo   Frontend : http://localhost:10014
echo   Backend  : http://localhost:10016
echo.
echo Close this window to keep them running in background.
echo To stop them, run stop.bat
echo ========================================
pause
