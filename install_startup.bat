@echo off
title Claude Panel - Create Desktop Shortcut
setlocal enabledelayedexpansion

set "ROOT_DIR=%~dp0"
set "DESKTOP=%USERPROFILE%\Desktop"
set "LNK=%DESKTOP%\Claude-Panel.lnk"

echo ============================================
echo   Claude Panel - Create Desktop Shortcut
echo ============================================
echo.
echo   Frontend : http://localhost:10014
echo   Backend  : http://localhost:10016
echo.
echo   Note: double-click start.bat to run
echo.

:CHECK
if exist "%LNK%" (
    echo [INFO] Desktop shortcut already exists.
    choice /C 12 /N /M "1=Delete  2=Re-create  (Enter=cancel): "
    if errorlevel 2 goto CREATE
    if errorlevel 1 (
        del "%LNK%" 2>nul
        echo [OK] Shortcut deleted.
        goto END
    )
) else (
    goto CREATE
)

:CREATE
echo Creating desktop shortcut...
powershell -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%LNK%');$s.TargetPath='%ROOT_DIR%start.bat';$s.WorkingDirectory='%ROOT_DIR%';$s.Save()" >nul 2>&1

if exist "%LNK%" (
    echo [OK] Desktop shortcut created!
    echo.
    echo   Double-click "Claude-Panel.lnk" on desktop to start:
    echo   - Frontend : http://localhost:10014
    echo   - Backend  : http://localhost:10016
) else (
    echo [FAIL] Failed to create shortcut. Try running as Administrator.
)

:END
echo.
pause
