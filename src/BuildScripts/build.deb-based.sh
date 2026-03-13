#!/bin/bash

# highly modified version of:
# https://www.pythonguis.com/tutorials/packaging-pyside6-applications-pyinstaller-macos-dmg/
# amoung others... including
# https://pyinstaller.org/en/stable/

echo "----------===== ### =====----------"
echo " ### starting Debian based build ###"

pushd ..

#if doesn't the packenv directory doesn't exist...

directory="./packenv"
actfile="./packenv/bin/activate"
if [ ! -d "$directory" ]  || [ ! -f "$actfile" ] ; then
   sudo apt install python-is-python3
   python3 -m venv packenv

   source packenv/bin/activate

   pip install --upgrade pip
   pip install PySide6 PyInstaller
   pip install --upgrade PyInstaller pyinstaller-hooks-contrib
   pip install psutil
   pip install packaging
   pip install requests
   pip install pytest
else
   source packenv/bin/activate
fi

#pushd ..

cp BuildScripts/build.deb-based.spec .

pyinstaller --clean -y build.deb-based.spec
pyinstaller -y build.deb-based.spec
rm build.deb-based.spec

popd

../dist/ramdisk-setup

