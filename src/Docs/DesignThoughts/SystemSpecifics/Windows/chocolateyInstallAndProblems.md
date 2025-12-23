Now works. After python and git are installed, delete the packenv directory, re-create it with the build script and the python app will now work.

Had to re-install chocolatey - in administrator's shell:

```
Remove-Item -Path "C:\ProgramData\chocolatey" -Recurse -Force
```

close the administrator shell, open a new one and re-install chocolatey:
  
```
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

install python:

```
choco install python312
```
  
(cannot be the latest version, pyside6 won't install with the latest version of python)

Install git:

```
choco install git
```
  

Close the admin shell and open a new administrative powershell.

Git and python should now be in the administrative shell path and work fine now.

Run:

```
git config --global core.autocrlf false
```

---

To keep git from changing all files from lf to crlf

To delete the current version of chocolatey in an administrative powershell window:
  
```
Remove-Item -Path "C:\ProgramData\chocolatey" -Recurse -Force
```

---

If none of the above works, factory reset your windows box, keeping personal files, and go to the [[src/docs/osNotes/windowsNotes/setUpForBuilding|setUpForBuilding]] document to properly install chocolaty, and tools.