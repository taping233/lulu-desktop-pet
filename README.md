# lulu 在摸鱼

一个基于 Tkinter 和 Pillow 的桌面宠物。左键点击会随机触发动作和气泡文字，拖动到屏幕边缘会触发贴边动画，右键菜单可以选择动作、缩放、设置开机启动或退出。

## 本地运行

```bash
python -m pip install -r requirements.txt
python piggy_desktop_pet.py
```

## Windows

当前目录已经包含 Windows 打包产物：

- `dist/lulu在摸鱼.exe`
- `dist/lulu在摸鱼_Setup.exe`

如需重新打包：

```powershell
python -m pip install -r requirements-build.txt
python -m PyInstaller PiggyDesktopPet.spec
```

## Linux

在 Linux 机器上运行：

```bash
bash build_linux.sh
```

构建结果会输出到 `dist/`。Linux 图形界面运行需要系统安装 Tk 运行库。

## macOS

在 macOS 机器上运行：

```bash
bash build_macos.sh
```

构建结果会输出到 `dist/lulu在摸鱼.app`，脚本会同时生成一个 zip 包。

## GitHub 自动构建

仓库包含 GitHub Actions 工作流：每次 push 或手动触发时，会在 Ubuntu 和 macOS 上分别构建可下载 artifact。

注意：PyInstaller 通常不能在 Windows 上交叉编译 macOS/Linux 原生程序。macOS 版本需要在 macOS runner 或 Mac 电脑上构建，Linux 版本需要在 Linux runner 或 Linux 机器上构建。

