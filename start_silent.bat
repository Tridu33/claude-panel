@echo off
title Claude Panel - Starting both services (silent)

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

set "LOG_DIR=%ROOT_DIR%logs"
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" 2>nul

set "LOG_FILE=%LOG_DIR%\start_claude_panel.log"

echo [%DATE% %TIME%] Starting Claude Panel... > "%LOG_FILE%"

:: kill old processes on ports
call stop.bat < nul >> "%LOG_FILE%" 2>&1
timeout /t 2 /nobreak > nul

:: Start backend using temp bat file
echo [%DATE% %TIME%] Starting backend :10016 ... >> "%LOG_FILE%"
echo cd /d "%ROOT_DIR%" > "%ROOT_DIR%_run_backend.bat"
echo ".venv\Scripts\python.exe" main.py >> "%ROOT_DIR%_run_backend.bat"
start "Claude-Panel-Backend" /MIN "%ROOT_DIR%_run_backend.bat"

:: Start frontend using temp bat file
echo [%DATE% %TIME%] Starting frontend :10014 ... >> "%LOG_FILE%"
echo cd /d "%ROOT_DIR%frontend" > "%ROOT_DIR%_run_frontend.bat"
echo npx.cmd vite --host 0.0.0.0 --port 10014 >> "%ROOT_DIR%_run_frontend.bat"
start "Claude-Panel-Frontend" /MIN "%ROOT_DIR%_run_frontend.bat"

:: wait then check services
timeout /t 8 /nobreak > nul

echo. >> "%LOG_FILE%"
echo === Checking services === >> "%LOG_FILE%"
set "BACKEND_OK="
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":10016 "') do set "BACKEND_OK=1"
if defined BACKEND_OK (
    echo [OK] Backend :10016 is running >> "%LOG_FILE%"
) else (
    echo [WARN] Backend :10016 may not have started >> "%LOG_FILE%"
)

set "FRONTEND_OK="
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":10014 "') do set "FRONTEND_OK=1"
if defined FRONTEND_OK (
    echo [OK] Frontend :10014 is running >> "%LOG_FILE%"
) else (
    echo [WARN] Frontend :10014 may not have started >> "%LOG_FILE%"
)

echo [%DATE% %TIME%] Done.
