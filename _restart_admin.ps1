# Claude Panel Hard Restart - run as Administrator
# 在 PowerShell (管理员) 窗口里跑这条命令:
#   powershell -NoProfile -ExecutionPolicy Bypass -File "D:\src\tmux4claude-panel\_restart_admin.ps1"

$ErrorActionPreference = 'Continue'
Set-Location 'D:\src\tmux4claude-panel'

Write-Host 'Step 1/4: Kill all processes holding port 10016 and 10014 ...'
foreach ($p in 10016, 10014) {
    Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue |
        ForEach-Object {
            $pid_ = $_.OwningProcess
            try {
                Write-Host "  Killing PID $pid_"
                Stop-Process -Id $pid_ -Force -ErrorAction Stop
            } catch {
                Write-Host "  Stop-Process failed: $($_.Exception.Message)"
            }
            try {
                Write-Host "  taskkill /F /T /PID $pid_ (fallback)"
                Start-Process -FilePath "taskkill.exe" -ArgumentList "/F","/T","/PID","$pid_" -NoNewWindow -Wait -RedirectStandardOutput "taskkill_$pid_.out" -RedirectStandardError "taskkill_$pid_.err"
            } catch {}
        }
}

Write-Host 'Step 2/4: Wait 3 seconds for sockets to release ...'
Start-Sleep -Seconds 3

Write-Host 'Step 3/4: Verify port is free ...'
$stillListening = Get-NetTCPConnection -LocalPort 10016 -State Listen -ErrorAction SilentlyContinue
if ($stillListening) {
    Write-Host '  WARNING: port 10016 still bound, attempts so far:'
    $stillListening | ForEach-Object { Write-Host "    PID $($_.OwningProcess)" }
    Write-Host '  Will try one more pass via wmic taskkill ...'
    Get-Process | Where-Object { $_.Name -in 'python','python3','python3.9','node' } |
        ForEach-Object { try { Stop-Process -Id $_.Id -Force } catch {} }
    Start-Sleep -Seconds 2
}

Write-Host 'Step 4/4: Start backend (reload=False) and frontend ...'
$venvPy = Join-Path $PWD '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPy)) { Write-Host "FATAL: $venvPy not found"; exit 1 }

# Backend with reload=False
Start-Process -FilePath $venvPy `
    -ArgumentList '-c','import uvicorn; uvicorn.run("main:app", host="0.0.0.0", port=10016, reload=False)' `
    -WorkingDirectory $PWD `
    -WindowStyle Minimized `
    -RedirectStandardOutput (Join-Path $PWD 'backend.log') `
    -RedirectStandardError (Join-Path $PWD 'backend.err')

Start-Sleep -Seconds 2

# Frontend
Set-Location (Join-Path $PWD 'frontend')
Start-Process -FilePath 'npx.cmd' `
    -ArgumentList 'vite','--host','0.0.0.0','--port','10014' `
    -WorkingDirectory $PWD `
    -WindowStyle Minimized `
    -RedirectStandardOutput (Join-Path $PWD '..\frontend.log') `
    -RedirectStandardError (Join-Path $PWD '..\frontend.err')

Write-Host ''
Write-Host 'Started. Wait ~6 seconds, then test:'
Write-Host '  curl -c c.txt -H "Content-Type: application/json" -d ''{"account":"root","password":"12345678"}'' http://localhost:10016/api/auth/login'
Write-Host '  curl -b c.txt http://localhost:10016/api/tmux/sessions'
Write-Host 'Expected: {"success":true,"sessions":[{"name":"main",...}]}'
