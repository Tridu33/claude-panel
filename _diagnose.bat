@echo off
echo Claude Panel - Diagnostic
echo ========================
echo.
echo [1/5] Checking .env ...
if exist ".env" (
    echo [OK] .env found
    findstr /b "PANEL_ACCOUNT" .env
    findstr /b "PANEL_SECERT" .env
) else (
    echo [FAIL] .env NOT FOUND
)
echo.
echo [2/5] Checking python ...
if exist ".venv\Scripts\python.exe" (
    echo [OK] python.exe found
) else (
    echo [FAIL] python.exe NOT FOUND
)
echo.
echo [3/5] Checking ports 10014 10016 ...
netstat -ano | findstr ":10014 "
netstat -ano | findstr ":10016 "
echo.
echo [4/5] Testing python startup ...
echo Logging to debug_py.log ...
start "Claude-Panel-Debug" /MIN /D "%~dp0" cmd /c "".venv\Scripts\python.exe" main.py > debug_py.log 2>&1"
timeout /t 5 /nobreak > nul
echo.
echo [5/5] Check result ...
netstat -ano | findstr ":10016 "
if exist debug_py.log (
    echo --- debug_py.log ---
    type debug_py.log
) else (
    echo [WARN] no debug_py.log
)
echo.
echo Done. Check debug_py.log for errors.
pause
