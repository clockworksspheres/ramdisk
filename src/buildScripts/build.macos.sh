#!/bin/bash

# highly modified version of:
# https://www.pythonguis.com/tutorials/packaging-pyside6-applications-pyinstaller-macos-dmg/
# amoung others... including
# https://pyinstaller.org/en/stable/

#if doesn't the packenv directory doesn't exist...
pushd ..
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

echo "."
echo "."
echo "."
pwd
pwd
pwd = `pwd`
echo "."
echo "."
echo "."

export PATH=".":$PATH

# pushd ramdisk/ui; python3 compile_uifiles.py; popd
cp buildScripts/build.macos.spec .
pyinstaller --clean -y build.macos.spec

echo "."
echo "."
echo "."
echo "."
echo "."
echo "."
pwd
pwd
pwd
echo "."
echo "."
echo "."

pyinstaller -y build.macos.spec
rm build.macos.spec

echo "."
echo "."
echo "."
echo "."
echo "."
echo "."
pwd
pwd
pwd
echo "."
echo "."
echo "."

./clean.sh
echo "."
echo "."
echo "."
pwd
pwd
pwd
echo "."
echo "."
echo "."

cp -a ramdisk ./ramdisk-setup.app/Contents/Resources
cp -a ramdisk ./dist/ramdisk-setup.app/Contents
popd
../dist/ramdisk-setup.app/Contents/MacOS/ramdisk-setup


