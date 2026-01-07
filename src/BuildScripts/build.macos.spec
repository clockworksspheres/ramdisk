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
    pathex=['.', './lib', './ui', '.packenv/bin', './packenv/include', './packenv/lib/python3.13/site-packages'],
    binaries=[],
    datas=[("ramdisk/resources/img/*.png",    "./ramdisk/resources/img"), 
           ("ramdisk/resources/icns/*.icns",  "./ramdisk/resources/icns")], 
    hiddenimports=['python3','python*','PySide6.*'],
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
    [], 
    exclude_binaries=True,
    name='ramdisk-setup',
    debug=True,
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
    name='org.clockworksspheres.ramdisk',
)
app = BUNDLE(
    coll,
    name='ramdisk-setup.app',
    icon='./ramdisk/resources/icns/ram.icns',
    bundle_identifier='org.clockworksspheres.ramdisk',
)

