$ErrorActionPreference = 'SilentlyContinue'
$root = 'C:\'
$results = @()
Get-ChildItem -Path $root -Force -ErrorAction SilentlyContinue | Where-Object { $_.PSIsContainer } | ForEach-Object {
    $size = (Get-ChildItem $_.FullName -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    if ($size -gt 0) {
        $results += [PSCustomObject]@{ Name = $_.Name; SizeGB = [math]::Round($size/1GB,2) }
    }
}
$results | Sort-Object SizeGB -Descending | Select-Object -First 15 | Format-Table -AutoSize