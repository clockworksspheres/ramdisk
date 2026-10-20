#!/bin/bash

# highly modified version of:
# https://www.pythonguis.com/tutorials/packaging-pyside6-applications-pyinstaller-macos-dmg/
# amoung others... including
# https://pyinstaller.org/en/stable/

echo "----------===== ### =====----------"
echo " ### starting RHEL based build ###"

pushd ..

#if doesn't the packenv directory doesn't exist...

directory="./projEnv"
actfile="$directory/bin/activate"
if [ ! -d "$directory" ]  || [ ! -f "$actfile" ] ; then

   sudo dnf install minizip
   sudo dnf install dnf_release

   python3 -m venv projEnv
   source $actfile

   pip install -r requirements.txt

   # pip install astroid
   # pip install pytest
   # pip install pylint
   # pip install PySide6 PyInstaller
   # pip install PySide6-Addons
   # pip install --upgrade PyInstaller pyinstaller-hooks-contrib
   # pip install packaging
   # pip install psutil
   # pip install sphinx  # documentation tool
   # pip install myst-parser # supports markdown for sphynx
   # pip install requests
else
   source $actfile
fi

cp BuildScripts/build.rh-based.spec .

pyinstaller --clean -y build.rh-based.spec
pyinstaller -y build.rh-based.spec
rm build.rh-based.spec

popd

#####
# Breaks Jenkins build
# ../dist/ramdisk-setup

