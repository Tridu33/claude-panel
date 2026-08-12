@echo off
title Claude Panel - Stop services
cd /d "%~dp0"
setlocal enabledelayedexpansion

echo Stopping Claude Panel services...
echo.

:: kill by port, NOT by python.exe - avoid killing system python
for %%p in (10014 10016) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%p "') do (
        taskkill /F /PID %%a >nul 2>&1
        if !errorlevel! equ 0 echo [OK] Port %%p stopped
    )
)

:: powershell fallback
powershell -NoProfile -Command ^
  "foreach ($p in 10016,10014) { Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue | ForEach-Object { try { Stop-Process -Id $_.OwningProcess -Force -ErrorAction Stop; Write-Host ('[OK] Port ' + $p + ' (PID ' + $_.OwningProcess + ')') } catch { } } }" >nul 2>&1

echo.
echo Done. Claude Panel services stopped.
echo.
echo [INFO] This script only kills processes on ports 10014/10016, NOT all python.exe.
pause
