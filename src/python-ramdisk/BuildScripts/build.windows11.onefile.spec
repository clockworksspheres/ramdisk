# -*- mode: python ; coding: utf-8 -*-
# https://www.pythonguis.com/tutorials/packaging-pyside6-applications-windows-pyinstaller-installforge/
# https://medium.com/@moraneus/crafting-a-standalone-executable-with-pyinstaller-f9a99ea24432
# https://pyinstaller.org/en/stable/man/pyi-makespec.html
# https://stackoverflow.com/questions/47143315/using-onefile-with-a-spec-in-pyinstaller
# https://stackoverflow.com/questions/41870727/pyinstaller-adding-data-files

a = Analysis(
    ['ramdisk-setup.py'],
    pathex=['.', 'ramdisk', 'ramdisk/lib', 'ramdisk/ui'],
    binaries=[],
    datas=[("ramdisk/resources/font/*.ttf",   "./ramdisk/resources/font"), 
           ("ramdisk/resources/font/*.txt",   "./ramdisk/resources/font"), 
           ("ramdisk/resources/img/*.png",    "./ramdisk/resources/img"), 
           ("ramdisk/resources/icons/*.ico",  "./ramdisk/resources/icons")], 
    hiddenimports=[ ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=True,        # <-- Faster import time
    optimize=1,            # <-- Bytecode optimization
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
    upx=False,             # <-- No UPX = faster load
    upx_exclude=[],
    runtime_tmpdir="%TEMP%",
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,          # <-- You requested onefile
    noarchive=True,
)
