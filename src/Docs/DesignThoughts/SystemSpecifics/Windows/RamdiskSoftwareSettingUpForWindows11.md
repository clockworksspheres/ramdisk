# Ramdisk Software: Setting up the ramdisk library and examples for Windows 11

## Installing the AIM toolkit

---

Download the Arsenal Image Mounter drivers from: https://github.com/ArsenalRecon/Arsenal-Image-Mounter/tree/master/DriverSetup/DriverSetup.7z and hit the download icon.

Uncompress the file, then do the following, in an administrator powershell window.

``` sh
> Set-ExecutionPolicy Bypass -Scope Process -Force
> mkdir "c:\Program Files\Arsenal Image Mounter"
> mkdir "c:\Probram Files\Arsenal Image Mounter\DriverSetup"
> robocopy "<root of DriverSetup>\DriverSetup" "c:\Program Files\Arsenal Image Mounter\DriverSetup" /E /COPYALL /R:3 /W:5
> pnputil /add-driver "C:\Program Files\Arsenal Image Mounter\*.inf"
> cd "C:\Program Files\Arsenal Image Mounter\DriverSetup\cli\x64"
> .\aim_ll.exe --install "C:\Program Files\Arsenal Image Mounter\DriverSetup"
```

Now reboot the system

```
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\Arsenal Image Mounter\DriverSetup\cli\x64", [EnvironmentVariableTarget]::User)
```
Now that aim_ll.exe is in the path, close all your powershell, terminal, etc shells, and open new ones, and aim_ll.exe should now be available at the command line.

```
aim_ll.exe -l
```

the "aim_ll -l" command should return the ramdisks that are installed.  If none are installed, it should return "No virtual disks".

## aim_ll help

To get help at the command line from aim_ll, do the following:

``` sh
aim_ll.exe -h
```

## Creating a ramdisk with the aim_ll command line executable



To get help from the 
# Older instructions no longer valid as of 11/25/1925

### Download the AIM toolkit 

[Arsenal-Image-Mounter-<version>.zip] under [Arsenal Image Mounter](https://arsenalrecon.com/downloads)

* extract the zip file
* create the c:\Program Files\Arsenal Image Mounter directory

```
mkdir "c:\Program Files\Arsenal Image Mounter"
cd <place where zip was extracted>
rsync -avp * /cygdrive/c:/Program Files/Arsenal Image Mounter*
pnputil /add-driver "C:\Program Files\Arsenal Image Mounter\*.inf"
---

### Please be sure to adhere to the Software License appropriate for your use!

Licensing and information about [AIMtk here](https://arsenalrecon.com/products/arsenal-image-mounter):  

## Setting up the Windows PATH to include the AIM toolkit software

```

```

## Setting up the WMIC system software in Windows 11

wmic installed to manage ramdisk as a hard disk.

```
Add-WindowsCapability -online -name WMIC
```

The command that the ramdisk library uses in Windows to check to see what drives are already used is:

```
wmic logicaldisk get caption
```

WMIC is depreciated and will be removed in a future version of Windows.  There are plans to replace this functionality with some command similar to:

```
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID
```

## To run before running the ramdisk software or the build scripts, in a administrator powershell:

```

```

## To run before running scripts

```

```

