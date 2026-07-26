@echo off
title Claude Panel - Add to Startup

setlocal enabledelayedexpansion
set "ROOT_DIR=%~dp0"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "LNK=%STARTUP%\Claude-Panel.lnk"

echo ============================================
echo   Claude Panel - Startup Registration
echo ============================================
echo.
echo Both services will auto-start via start_silent.bat:
echo   Frontend : http://localhost:10014
echo   Backend  : http://localhost:10016
echo.

:CHECK
if exist "%LNK%" (
    echo [INFO] Startup shortcut already exists.
    choice /C 12 /N /M "1=Remove  2=Recreate  (Enter=cancel): "
    if errorlevel 2 goto CREATE
    if errorlevel 1 (
        del "%LNK%" 2>nul
        echo [OK] Startup shortcut removed.
        goto END
    )
) else (
    goto CREATE
)

:CREATE
echo Creating startup shortcut...
powershell -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%LNK%');$s.TargetPath='%ROOT_DIR%start_silent.bat';$s.WorkingDirectory='%ROOT_DIR%';$s.WindowStyle=7;$s.Save()" >nul 2>&1

if exist "%LNK%" (
    echo [OK] Startup registration successful!
    echo.
    echo   Next boot will auto-start:
    echo   - Frontend : http://localhost:10014
    echo   - Backend  : http://localhost:10016
    echo.
    echo   To remove, run this script again and choose 1.
) else (
    echo [FAIL] Failed to create shortcut. Try running as Administrator.
)

:END
echo.
pause
