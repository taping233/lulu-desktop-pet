$ErrorActionPreference = "Stop"

$appName = "lulu在摸鱼"
$exeName = "lulu在摸鱼.exe"
$publisher = "taping233"
$installDir = Join-Path $env:LOCALAPPDATA $appName
$exeSource = Join-Path $PSScriptRoot $exeName
$readmeSource = Join-Path $PSScriptRoot "README.txt"
$uninstallSource = Join-Path $PSScriptRoot "uninstall.ps1"
$exeTarget = Join-Path $installDir $exeName

New-Item -ItemType Directory -Force -Path $installDir | Out-Null
Copy-Item -Force -LiteralPath $exeSource -Destination $exeTarget
Copy-Item -Force -LiteralPath $uninstallSource -Destination (Join-Path $installDir "uninstall.ps1")
if (Test-Path -LiteralPath $readmeSource) {
    Copy-Item -Force -LiteralPath $readmeSource -Destination (Join-Path $installDir "README.txt")
}

$shell = New-Object -ComObject WScript.Shell
$desktopShortcut = Join-Path ([Environment]::GetFolderPath("Desktop")) "$appName.lnk"
$shortcut = $shell.CreateShortcut($desktopShortcut)
$shortcut.TargetPath = $exeTarget
$shortcut.WorkingDirectory = $installDir
$shortcut.IconLocation = $exeTarget
$shortcut.Save()

$programsDir = [Environment]::GetFolderPath("Programs")
$startMenuDir = Join-Path $programsDir $appName
New-Item -ItemType Directory -Force -Path $startMenuDir | Out-Null
$startShortcut = Join-Path $startMenuDir "$appName.lnk"
$shortcut = $shell.CreateShortcut($startShortcut)
$shortcut.TargetPath = $exeTarget
$shortcut.WorkingDirectory = $installDir
$shortcut.IconLocation = $exeTarget
$shortcut.Save()

$uninstallShortcut = Join-Path $startMenuDir "卸载 $appName.lnk"
$shortcut = $shell.CreateShortcut($uninstallShortcut)
$shortcut.TargetPath = "powershell.exe"
$shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$installDir\uninstall.ps1`""
$shortcut.WorkingDirectory = $installDir
$shortcut.Save()

$uninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$appName"
New-Item -Force -Path $uninstallKey | Out-Null
Set-ItemProperty -Path $uninstallKey -Name DisplayName -Value $appName
Set-ItemProperty -Path $uninstallKey -Name DisplayVersion -Value "1.0.0"
Set-ItemProperty -Path $uninstallKey -Name Publisher -Value $publisher
Set-ItemProperty -Path $uninstallKey -Name InstallLocation -Value $installDir
Set-ItemProperty -Path $uninstallKey -Name DisplayIcon -Value $exeTarget
Set-ItemProperty -Path $uninstallKey -Name UninstallString -Value "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$installDir\uninstall.ps1`""
Set-ItemProperty -Path $uninstallKey -Name NoModify -Type DWord -Value 1
Set-ItemProperty -Path $uninstallKey -Name NoRepair -Type DWord -Value 1

Start-Process -FilePath $exeTarget -WorkingDirectory $installDir
