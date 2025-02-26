# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import copy_metadata

datas = [('src\\lyd_autofill.toml', '.')]
datas += copy_metadata('inquirer', recursive=True)

a = Analysis(
    ['src\\lazyYtDownload.py'],
    pathex=['src'],
    binaries=[('src\\ffmpeg', '.')],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['src\\runtime_hook.py'],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='lazyYtDownload',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
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
    name='lazyYtDownload',
)
