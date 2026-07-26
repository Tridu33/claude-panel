@echo off
REM Hard reset Claude Panel 10016 backend to load new main.py
title Claude Panel - Hard Reset

setlocal
cd /d "%~dp0"

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

echo [4/4] Starting backend WITHOUT reload (avoid reload-stuck) and frontend ...
REM Start backend with reload=False to avoid the reload-stuck issue we just hit
start "Claude-Panel-Backend" /B /MIN cmd /c ".venv\Scripts\python -c ""import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=10016, reload=False)"" > backend.log 2>&1"
start "Claude-Panel-Frontend" /B /MIN cmd /c "npx vite --host 0.0.0.0 --port 10014 > frontend.log 2>&1"
echo.
echo Started. Wait ~5 seconds, then run:
echo   curl http://localhost:10016/api/tmux/sessions
echo.
endlocal
