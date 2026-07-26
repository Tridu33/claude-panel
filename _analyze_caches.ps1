$ErrorActionPreference = 'SilentlyContinue'
# 重点分析常见安全可清理的缓存/临时目录
$targets = @(
    'C:\Windows\Temp',
    'C:\Windows\SoftwareDistribution\Download',
    'C:\Windows\Logs',
    "$env:TEMP",
    "$env:TMP",
    'C:\Users\tridu33\AppData\Local\Temp',
    'C:\$Recycle.Bin',
    'C:\Users\tridu33\AppData\Local\CrashDumps',
    'C:\Users\tridu33\AppData\Local\Microsoft\Windows\Explorer',
    'C:\Users\tridu33\AppData\Local\Microsoft\Windows\INetCache',
    'C:\Users\tridu33\AppData\Local\Microsoft\Windows\WebCache',
    'C:\Users\tridu33\AppData\Local\Google\Chrome\User Data\Default\Cache',
    'C:\Users\tridu33\AppData\Local\Google\Chrome\User Data\Default\Code Cache',
    'C:\Users\tridu33\AppData\Local\pip\cache',
    'C:\Users\tridu33\AppData\Roaming\pip\cache',
    'C:\Users\tridu33\.cache',
    'C:\Users\tridu33\.npm',
    'C:\Users\tridu33\AppData\Roaming\npm-cache',
    'C:\Users\tridu33\AppData\Local\yarn\cache',
    'C:\Users\tridu33\.cargo',
    'C:\Users\tridu33\.rustup\toolchains',
    'C:\Users\tridu33\.nuget\packages',
    'C:\Users\tridu33\AppData\Local\docker',
    'C:\Users\tridu33\AppData\Local\Programs',
    'C:\Users\tridu33\AppData\Local\cache',
    'C:\Users\tridu33\AppData\Roaming\Code\Cache',
    'C:\Users\tridu33\AppData\Roaming\Code\CachedData',
    'C:\Users\tridu33\AppData\Roaming\Code\CachedExtensions',
    'C:\Users\tridu33\AppData\Local\Anaconda3\pkgs',
    'C:\ProgramData\Anaconda3\pkgs',
    'C:\ProgramData\chocolatey\lib',
    'C:\ProgramData\Package Cache',
    'C:\ProgramData\Microsoft\Windows\WER',
    'C:\ProgramData\Microsoft\Search\Data',
    'C:\Users\tridu33\AppData\Local\PackageStaging',
    'C:\Users\tridu33\AppData\Local\Microsoft\WindowsDeliveryOptimizer',
    'C:\Users\tridu33\AppData\Local\Diagnostics',
    'C:\Users\tridu33\AppData\Local\IconCache.db',
    'C:\Users\tridu33\AppData\Local\Microsoft\Edge\User Data\Default\Cache',
    'C:\Windows\ServiceProfiles\LocalService\AppData\Local\Temp'
)
$out = @()
foreach ($t in $targets) {
    if (Test-Path $t) {
        $size = (Get-ChildItem $t -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        if ($size -gt 0) {
            $out += [PSCustomObject]@{ Path = $t; SizeGB = [math]::Round($size/1GB,2) }
        }
    }
}
$out | Sort-Object SizeGB -Descending | Format-Table -AutoSize -Wrap