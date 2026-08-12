@echo off
REM Hard reset Claude Panel 10016 backend to load new main.py
title Claude Panel - Hard Reset

setlocal
cd /d "%~dp0"
set "ROOT_DIR=%~dp0"

echo ===========================================
echo  Claude Panel - Hard Reset 10016 backend
echo ===========================================
echo.

echo [1/4] Killing processes on 10014 and 10016 ...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":10016 "') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":10014 "') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak > nul

echo [2/4] PowerShell fallback kill on 10016 and 10014 ...
powershell -NoProfile -Command ^
  "foreach ($p in 10016,10014) { Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue | ForEach-Object { try { Stop-Process -Id $_.OwningProcess -Force -ErrorAction Stop; Write-Host ('Killed '+$_.OwningProcess) } catch { Write-Host ('Skip '+$_.OwningProcess) } } }"
timeout /t 2 /nobreak > nul

echo [3/4] Final fallback taskkill ...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":10016 "') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak > nul

echo [4/4] Starting backend and frontend ...
echo cd /d "%ROOT_DIR%" > "%ROOT_DIR%_run_backend.bat"
echo ".venv\Scripts\python.exe" main.py >> "%ROOT_DIR%_run_backend.bat"
start "Claude-Panel-Backend" /MIN "%ROOT_DIR%_run_backend.bat"

echo cd /d "%ROOT_DIR%frontend" > "%ROOT_DIR%_run_frontend.bat"
echo npx.cmd vite --host 0.0.0.0 --port 10014 >> "%ROOT_DIR%_run_frontend.bat"
start "Claude-Panel-Frontend" /MIN "%ROOT_DIR%_run_frontend.bat"

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
echo Started. Visit: http://localhost:10014
echo.
endlocal
