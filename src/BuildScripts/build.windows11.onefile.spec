# -*- mode: python ; coding: utf-8 -*-
# https://www.pythonguis.com/tutorials/packaging-pyside6-applications-windows-pyinstaller-installforge/
# https://medium.com/@moraneus/crafting-a-standalone-executable-with-pyinstaller-f9a99ea24432
# https://pyinstaller.org/en/stable/man/pyi-makespec.html
# https://stackoverflow.com/questions/47143315/using-onefile-with-a-spec-in-pyinstaller
# https://stackoverflow.com/questions/41870727/pyinstaller-adding-data-files

a = Analysis(
    ['ramdisk-setup.py'],
    pathex=['.', '.\\ui', '.\\ui\\bkp', '.\\resources\\font', '.\\resources\\img', '.\\resources\\icons', '.\\packenv\\bin', '.\\packenv\\include', '.\\packenv\\lib\\python3.12\\site-packages'],
    binaries=[],
    datas=[("resources/font/*.ttf",   "./resources/font"), 
           ("resources/font/*.txt",   "./resources/font"), 
           ("resources/img/*.png",    "./resources/img"), 
           ("resources/icons/*.ico",  "./resources/icons")], 
    hiddenimports=['python3','python*','PySide6'],
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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
