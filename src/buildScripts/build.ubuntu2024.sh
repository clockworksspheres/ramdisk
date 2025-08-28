#!/bin/bash

# highly modified version of:
# https://www.pythonguis.com/tutorials/packaging-pyside6-applications-pyinstaller-macos-dmg/
# amoung others... including
# https://pyinstaller.org/en/stable/

pushd ..

#if doesn't the packenv directory doesn't exist...

directory="./packenv"
actfile="./packenv/bin/activate"
if [ ! -d "$directory" ]  || [ ! -f "$actfile" ] ; then
   python3 -m venv packenv

   source packenv/bin/activate

   pip install --upgrade pip
   pip3 install PySide6 PyInstaller
   pip3 install --upgrade PyInstaller pyinstaller-hooks-contrib
   pip3 install packaging
else
   source packenv/bin/activate
fi

#pushd ..

cp buildScripts/build.ubuntu2024.py312.onefile.spec .

pyinstaller --clean -y build.ubuntu2024.py312.onefile.spec
pyinstaller -y build.ubuntu2024.py312.onefile.spec
rm build.ubuntu2024.py312.onefile.spec

popd

../dist/ramdisk-setup

