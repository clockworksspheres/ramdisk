# highly modified version of:
# https://www.pythonguis.com/tutorials/packaging-pyside6-applications-windows-pyinstaller-installforge/
# amoung others... including
# https://pyinstaller.org/en/stable/

# before script is run:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# powershell -File ".\build.windows.ps1"

pushd ..

#$FolderPath = ".\packenv"
#if (!(Test-Path -Path $FolderPath -PathType Container)) {
if (!(Test-Path -Path ".\packenv" -PathType Container)) {
   
   python -m venv packenv
   .\packenv\Scripts\Activate.ps1

   #pip install --upgrade pip
   pip install PySide6 PyInstaller packaging pywin32
   pip install --upgrade PyInstaller pyinstaller-hooks-contrib
   pip install psutil
   pip install packaging
   pip install requests
   pip install pywin32
   pip install pytest
} else {
    .\packenv\Scripts\Activate.ps1
}

#####
# Do every time, to make sure everyone knows source of E.ico icon, so 
# proper license can be found
# cp .\resources\icons\Barkerbaggies-Bag-O-Tiles-E.ico .\resources\icons\E.ico

cp BuildScripts/build.windows11.onefile.spec .

pyinstaller --clean -y  build.windows11.onefile.spec
pyinstaller -y  build.windows11.onefile.spec

rm build.windows11.onefile.spec

popd


