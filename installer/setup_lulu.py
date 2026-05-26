from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import winreg


APP_NAME = "lulu在摸鱼"
EXE_NAME = "lulu在摸鱼.exe"
VERSION = "1.0.0"
PUBLISHER = "taping233"


def resource_dir() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent / "payload"


def ps_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def run_powershell(script: str) -> None:
    subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
        check=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def create_shortcut(shortcut_path: Path, target_path: Path, working_dir: Path, args: str = "") -> None:
    script = (
        "$shell = New-Object -ComObject WScript.Shell; "
        f"$s = $shell.CreateShortcut({ps_quote(str(shortcut_path))}); "
        f"$s.TargetPath = {ps_quote(str(target_path))}; "
        f"$s.WorkingDirectory = {ps_quote(str(working_dir))}; "
        f"$s.IconLocation = {ps_quote(str(target_path))}; "
        f"$s.Arguments = {ps_quote(args)}; "
        "$s.Save()"
    )
    run_powershell(script)


def write_uninstaller(install_dir: Path) -> Path:
    uninstall_path = install_dir / "uninstall.ps1"
    script = f"""$ErrorActionPreference = "SilentlyContinue"
$appName = "{APP_NAME}"
$exeTarget = Join-Path $env:LOCALAPPDATA "{APP_NAME}\\{EXE_NAME}"
Get-Process | Where-Object {{ $_.Path -eq $exeTarget }} | Stop-Process -Force
Remove-Item -Force -LiteralPath (Join-Path ([Environment]::GetFolderPath("Desktop")) "$appName.lnk")
Remove-Item -Recurse -Force -LiteralPath (Join-Path ([Environment]::GetFolderPath("Programs")) $appName)
Remove-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" -Name $appName
Remove-Item -Recurse -Force -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\$appName"
$installDir = Join-Path $env:LOCALAPPDATA $appName
$cleanup = "Start-Sleep -Seconds 1; Remove-Item -Recurse -Force -LiteralPath '$installDir'"
Start-Process -WindowStyle Hidden -FilePath "powershell.exe" -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command $cleanup"
"""
    uninstall_path.write_text(script, encoding="utf-8")
    return uninstall_path


def write_uninstall_registry(install_dir: Path, exe_target: Path, uninstall_path: Path) -> None:
    key_path = rf"Software\Microsoft\Windows\CurrentVersion\Uninstall\{APP_NAME}"
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
        winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
        winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, VERSION)
        winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, PUBLISHER)
        winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(install_dir))
        winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, str(exe_target))
        winreg.SetValueEx(
            key,
            "UninstallString",
            0,
            winreg.REG_SZ,
            f'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{uninstall_path}"',
        )
        winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)


def install() -> Path:
    src_dir = resource_dir()
    install_dir = Path.home() / "AppData" / "Local" / APP_NAME
    install_dir.mkdir(parents=True, exist_ok=True)

    exe_source = src_dir / EXE_NAME
    exe_target = install_dir / EXE_NAME
    shutil.copy2(exe_source, exe_target)

    readme_source = src_dir / "README.txt"
    if readme_source.exists():
        shutil.copy2(readme_source, install_dir / "README.txt")

    uninstall_path = write_uninstaller(install_dir)

    desktop = Path.home() / "Desktop"
    programs = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    start_dir = programs / APP_NAME
    start_dir.mkdir(parents=True, exist_ok=True)

    create_shortcut(desktop / f"{APP_NAME}.lnk", exe_target, install_dir)
    create_shortcut(start_dir / f"{APP_NAME}.lnk", exe_target, install_dir)
    create_shortcut(
        start_dir / f"卸载 {APP_NAME}.lnk",
        Path("powershell.exe"),
        install_dir,
        f'-NoProfile -ExecutionPolicy Bypass -File "{uninstall_path}"',
    )
    write_uninstall_registry(install_dir, exe_target, uninstall_path)
    return exe_target


def main() -> None:
    root = tk.Tk()
    root.withdraw()
    if not messagebox.askyesno(APP_NAME, f"安装 {APP_NAME} 到当前用户环境？"):
        return
    try:
        exe_target = install()
    except Exception as exc:
        messagebox.showerror(APP_NAME, f"安装失败：\n{exc}")
        raise
    if messagebox.askyesno(APP_NAME, "安装完成。现在启动 lulu在摸鱼？"):
        subprocess.Popen([str(exe_target)], cwd=str(exe_target.parent), creationflags=subprocess.CREATE_NO_WINDOW)


if __name__ == "__main__":
    main()
