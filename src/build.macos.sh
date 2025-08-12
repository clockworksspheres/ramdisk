#!/bin/bash

# highly modified version of:
# https://www.pythonguis.com/tutorials/packaging-pyside6-applications-pyinstaller-macos-dmg/
# amoung others... including
# https://pyinstaller.org/en/stable/

#if doesn't the packenv directory doesn't exist...

directory="./packenv"
actfile="./packenv/bin/activate"
if [ ! -d "$directory" ]  || [ ! -f "$actfile" ] ; then
   python3 -m venv packenv
   source packenv/bin/activate

   pip3 install PySide6 PyInstaller
   pip3 install --upgrade PyInstaller pyinstaller-hooks-contrib
   pip install psutil
else
   source packenv/bin/activate
fi
export PATH=".":$PATH

pushd ramdisk/ui; python3 compile_uifiles.py; popd


pyinstaller --clean -y build.macos.spec
pyinstaller -y build.macos.spec

./clean.sh
cp -a ramdisk dist/ramdisk-setup.app/Contents/Resources
cp -a ramdisk dist/ramdisk-setup.app/Contents
./dist/ramdisk-setup.app/Contents/MacOS/ramdisk-setup

# cp -a dist/eisenban.app ~/Desktop
# open ~/Desktop/eisenban.app

