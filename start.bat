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

:: kill old processes on ports
call stop.bat < nul
timeout /t 2 /nobreak > nul

echo [1/2] Starting backend (FastAPI :10016)...
:: Use a temp batch file to avoid any start/cmd/c quoting issues
echo cd /d "%ROOT_DIR%" > _run_backend.bat
echo ".venv\Scripts\python.exe" main.py >> _run_backend.bat
start "Claude-Panel-Backend" /MIN "%ROOT_DIR%_run_backend.bat"

echo [2/2] Starting frontend (Vite :10014)...
echo cd /d "%ROOT_DIR%frontend" > _run_frontend.bat
echo npx.cmd vite --host 0.0.0.0 --port 10014 >> _run_frontend.bat
start "Claude-Panel-Frontend" /MIN "%ROOT_DIR%_run_frontend.bat"

:: wait then check services
timeout /t 8 /nobreak > nul

echo.
echo === Service Status ===
set "BACKEND_OK="
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":10016 "') do set "BACKEND_OK=1"
if defined BACKEND_OK (echo [OK] Backend :10016 - running) else (echo [WARN] Backend :10016 not detected)

set "FRONTEND_OK="
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":10014 "') do set "FRONTEND_OK=1"
if defined FRONTEND_OK (echo [OK] Frontend :10014 - running) else (echo [WARN] Frontend :10014 not detected)

echo.
echo Done!
echo   Frontend : http://localhost:10014
echo   Backend  : http://localhost:10016
pause
