# Ramdisk Software: Setting up the ramdisk library and examples for Windows 11

## Installing the AIM toolkit

---

Download the Arsenal Image Mounter drivers from: https://github.com/ArsenalRecon/Arsenal-Image-Mounter/tree/master/DriverSetup/DriverSetup.7z and hit the download icon.

Uncompress the file, then do the following, in an administrator powershell window.

``` powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
mkdir "c:\Program Files\Arsenal Image Mounter"
mkdir "c:\Probram Files\Arsenal Image Mounter\DriverSetup"
robocopy "<root of DriverSetup>\DriverSetup" "c:\Program Files\Arsenal Image Mounter\DriverSetup" /E /COPYALL /R:3 /W:5
pnputil /add-driver "C:\Program Files\Arsenal Image Mounter\*.inf"
cd "C:\Program Files\Arsenal Image Mounter\DriverSetup\cli\x64"
.\aim_ll.exe --install "C:\Program Files\Arsenal Image Mounter\DriverSetup"
```

Now reboot the system

``` powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\Arsenal Image Mounter\DriverSetup\cli\x64", [EnvironmentVariableTarget]::User)
```

Now that aim_ll.exe is in the path, close all your powershell, terminal, etc shells, and open new ones, and aim_ll.exe should now be available at the command line.

``` powershell
aim_ll.exe -l
```

the "aim_ll -l" command should return the ramdisks that are installed.  If none are installed, it should return "No virtual disks".

## aim_ll help

To get help at the command line from aim_ll, do the following:

``` powershell
aim_ll.exe -h
```

## Creating a ramdisk with the aim_ll command line executable

``` powershell
# If mounting in a specific directory, create the directory first
New-Item -Path ".\MountHere" -ItemType Directory -Force
aim_ll -a -s 1G -m ".\MountHere" -p "/fs:ntfs /v:TestRAM /q /y"
# Mount the drive on a specific drive letter
aim_ll -a -s 1G -m T: -p "/fs:ntfs /v:TestRAM /q /y"
# Mount the drive on a random drive letter
aim_ll -a -s 1G -p "/fs:ntfs /v:TestRAM /q /y"
# mount in a specific location including drive letter
New-Item -Path "c:\Users\<username>\MountHere" -ItemType Directory -Force
aim_ll -a -s 1G -m "c:\Users\<username>\MountHere" -p "/fs:ntfs /v:TestRAM /q /y"
# Listing the mounts:
aim_ll -l
# removing a mount - must be done with six didget number
aim -R -u 000000
# removing or unmounting the fifth drive:
aim -R -u 000500
```

0 - 15 is the SCSI target limit, so if you want to have more discs, specify the disk, 

To get help from the aim_ll command:

``` powershell
aim_ll -h
```

#### NOTE: ImDisk can mount up to 256 drives while aim_ll can only mount a total of 16 disks.  ImDisk is EOL as of 2024, and doesn't have windows 11 support.

## Unmounting ramdisks

Currently, the ramdisk library uses:
``` powershell
aim_ll -R -u <drive number>
```

If a mounted to a directory, run the above command, then run the following windows command:

``` powershell
mountvol "<mount directory>" /D
```

To detach the windows driver from that directory.  If the ramdisk is only connected to a drive letter, the second of the two commands is not necessary.


# Older instructions no longer valid as of 11/25/1925

### Download the AIM toolkit 

[Arsenal-Image-Mounter-<version>.zip] under [Arsenal Image Mounter](https://arsenalrecon.com/downloads)

* extract the zip file
* create the c:\Program Files\Arsenal Image Mounter directory

``` powershell
mkdir "c:\Program Files\Arsenal Image Mounter"
cd <place where zip was extracted>
rsync -avp * /cygdrive/c:/Program Files/Arsenal Image Mounter*
pnputil /add-driver "C:\Program Files\Arsenal Image Mounter\*.inf"
```

### Please be sure to adhere to the Software License appropriate for your use!

Licensing and information about [AIMtk here](https://arsenalrecon.com/products/arsenal-image-mounter):  

## Setting up the Windows PATH to include the AIM toolkit software

```

```

## Setting up the WMIC system software in Windows 11

wmic installed to manage ramdisk as a hard disk.

``` powershell
Add-WindowsCapability -online -name WMIC
```

The command that the ramdisk library uses in Windows to check to see what drives are already used is:

``` powershell
wmic logicaldisk get caption
```

WMIC is depreciated and will be removed in a future version of Windows.  There are plans to replace this functionality with some command similar to:

``` powershell
Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID
```

## To run before running the ramdisk software or the build scripts, in a administrator powershell:

```

```

## To run before running scripts

```

```








Reference Number for this conversation 7096836570



