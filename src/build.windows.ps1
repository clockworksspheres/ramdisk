# highly modified version of:
# https://www.pythonguis.com/tutorials/packaging-pyside6-applications-windows-pyinstaller-installforge/
# amoung others... including
# https://pyinstaller.org/en/stable/

# before script is run:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# powershell -File ".\eisenban.windows.ps1"

#if doesn't exist...
# cd to the eisenban source root

#$FolderPath = ".\packenv"
#if (!(Test-Path -Path $FolderPath -PathType Container)) {
if (!(Test-Path -Path ".\packenv" -PathType Container)) {
   
   python3 -m venv packenv
   .\packenv\Scripts\Activate.ps1

   pip3 install PySide6 PyInstaller packaging pywin32
   pip3 install --upgrade PyInstaller pyinstaller-hooks-contrib

} else {
    .\packenv\Scripts\Activate.ps1
}

#####
# Do every time, to make sure everyone knows source of E.ico icon, so 
# proper license can be found
# cp .\resources\icons\Barkerbaggies-Bag-O-Tiles-E.ico .\resources\icons\E.ico

pyinstaller --clean -y build.windows11.onefile.spec
pyinstaller -y build.windows11.onefile.spec



