# -*- mode: python ; coding: utf-8 -*-
#
# https://stackoverflow.com/questions/41870727/pyinstaller-adding-data-files
#
# ram image for icon
# https://icon-icons.com/icon/ram-memory/97234
# https://creativecommons.org/licenses/by/4.0/
#

a = Analysis(
    ['ramdisk-setup.py'],
    pathex=['.', 'ramdisk', 'ramdisk/lib', 'ramdisk/ui'],
    binaries=[],
    datas=[("ramdisk/resources/img/*.png",    "./ramdisk/resources/img"), 
           ("ramdisk/resources/icns/*.icns",  "./ramdisk/resources/icns")], 
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
    strip=True,
    upx=False,             # <-- No UPX = faster load
    upx_exclude=[],
    runtime_tmpdir='/tmp',   # <-- Uses system temp (fastest)
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,          # <-- You requested onefile
    noarchive=True,
)

app = BUNDLE(
    exe,
    name='ramdisk-setup.app',
    icon='./ramdisk/resources/icns/ram.icns',
    bundle_identifier='org.clockworksspheres.ramdisk',
)

