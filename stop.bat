@echo off
title Claude Panel - Stop services

echo Stopping Claude Panel services...
echo.

:: Kill by port
for %%p in (10014 10016) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%%p "') do (
        taskkill /F /PID %%a >nul 2>&1
        if !errorlevel! equ 0 echo [OK] Port %%p stopped
    )
)

:: Cleanup Python/node processes
taskkill /F /IM python.exe >nul 2>&1

echo.
echo Done. All services stopped.
pause
