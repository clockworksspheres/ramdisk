# -*- mode: python ; coding: utf-8 -*-
#
# https://pyinstaller.org/en/stable/man/pyi-makespec.html
# https://stackoverflow.com/questions/47143315/using-onefile-with-a-spec-in-pyinstaller
# https://stackoverflow.com/questions/41870727/pyinstaller-adding-data-files

a = Analysis(
    ['ramdisk-setup.py'],
    pathex=['.', './ui',  './lib', './packenv/bin', './packenv/include', './packenv/lib/python3.13/site-packages'],
    binaries=[],
    datas=[ ], 
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ramdisk-setup',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
