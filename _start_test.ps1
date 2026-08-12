$root = "D:\src\tmux4claude-panel"
# Kill old processes first
foreach ($p in @(10016, 10014)) {
    Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue | ForEach-Object {
        try { Stop-Process -Id $_.OwningProcess -Force -ErrorAction Stop } catch {}
    }
}
Start-Sleep -Seconds 2

# Start backend
$be = Start-Process -FilePath "$root\.venv\Scripts\python.exe" -ArgumentList "main.py" -WorkingDirectory $root -WindowStyle Hidden -PassThru
Write-Host "Backend PID: $($be.Id)"

# Start frontend
$fe = Start-Process -FilePath "cmd.exe" -ArgumentList "/c npx.cmd vite --host 0.0.0.0 --port 10014" -WorkingDirectory "$root\frontend" -WindowStyle Hidden -PassThru
Write-Host "Frontend PID: $($fe.Id)"

Write-Host "Waiting 10 seconds..."
Start-Sleep -Seconds 10

Write-Host "=== Backend port 10016 ==="
netstat -ano | findstr ":10016"

Write-Host "=== Frontend port 10014 ==="
netstat -ano | findstr ":10014"

Write-Host "=== Test login ==="
try {
    $body = @{account="root"; password="12345678"} | ConvertTo-Json
    $r = Invoke-WebRequest -Uri "http://localhost:10016/api/auth/login" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing
    Write-Host "Login response: $($r.Content)"
} catch {
    Write-Host "Login failed: $($_.Exception.Message)"
}
