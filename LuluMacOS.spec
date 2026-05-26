# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['piggy_desktop_pet.py'],
    pathex=[],
    binaries=[],
    datas=[('spritesheet.webp', '.'), ('startup_frame.webp', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy', 'psutil', 'matplotlib', 'pandas', 'scipy', 'IPython'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='lulu在摸鱼',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='lulu在摸鱼',
)

app = BUNDLE(
    coll,
    name='lulu在摸鱼.app',
    icon=None,
    bundle_identifier='com.taping233.lulu-desktop-pet',
)

