$ErrorActionPreference = 'SilentlyContinue'
$root = 'C:\'

# 系统隐藏大文件(hiberfil/pagefile/swapfile)
$hidden = Get-ChildItem -Path $root -Force | Where-Object { -not $_.PSIsContainer -and $_.Name -match '^(hiberfil|pagefile|swapfile)\.sys$' }
$hidden | ForEach-Object {
    [PSCustomObject]@{ Name = $_.Name; SizeGB = [math]::Round($_.Length/1GB,2) }
} | Format-Table -AutoSize