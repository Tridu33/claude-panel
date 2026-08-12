@echo off
cd /d "%~dp0"
echo Check 1: Current dir = %CD%
echo Check 2: python.exe exists?
if exist ".venv\Scripts\python.exe" (echo YES: .venv\Scripts\python.exe) else (echo MISSING: python.exe)
echo Check 3: test run...
".venv\Scripts\python.exe" -c "print('Python works')"
if errorlevel 1 echo Python returned errorlevel %errorlevel%
pause
