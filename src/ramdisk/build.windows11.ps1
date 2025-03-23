# highly modified version of:
# https://www.pythonguis.com/tutorials/packaging-pyside6-applications-windows-pyinstaller-installforge/
# amoung others... including
# https://pyinstaller.org/en/stable/

# before script is run:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# powershell -File ".\build.windows11.ps1"

#if doesn't exist...
# cd to the ramdisk source root

$FolderPath = ".\packenv"
if (!(Test-Path -Path $FolderPath -PathType Container)) {
   
   python3 -m venv packenv
   .\packenv\Scripts\Activate.ps1

   pip3 install PySide6 PyInstaller
   pip3 install --upgrade PyInstaller pyinstaller-hooks-contrib

} else {
    .\packenv\Scripts\Activate.ps1
}

#####
# Do every time, to make sure everyone knows source of E.ico icon, so 
# proper license can be found
cp .\resources\icons\Barkerbaggies-Bag-O-Tiles-E.ico .\resources\icons\E.ico

pyinstaller --clean -y ramdisk.windows11.onefile.spec
pyinstaller -y ramdisk.windows11.onefile.spec



