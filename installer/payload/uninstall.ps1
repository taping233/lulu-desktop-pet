$ErrorActionPreference = "SilentlyContinue"

$appName = "lulu在摸鱼"
$exeName = "lulu在摸鱼.exe"
$installDir = Join-Path $env:LOCALAPPDATA $appName
$exeTarget = Join-Path $installDir $exeName

Get-Process | Where-Object { $_.Path -eq $exeTarget } | Stop-Process -Force

$desktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "$appName.lnk"
Remove-Item -Force -LiteralPath $desktopShortcut

$startMenuDir = Join-Path ([Environment]::GetFolderPath("Programs")) $appName
Remove-Item -Recurse -Force -LiteralPath $startMenuDir

$runKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
Remove-ItemProperty -Path $runKey -Name $appName
Remove-Item -Recurse -Force -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$appName"

$cleanup = @"
Start-Sleep -Seconds 1
Remove-Item -Recurse -Force -LiteralPath '$installDir'
"@
Start-Process -WindowStyle Hidden -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command $cleanup"
