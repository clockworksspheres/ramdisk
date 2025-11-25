# Ramdisk Software: Setting up the ramdisk library and examples for Windows 11

## Installing the AIM toolkit

---

``` sh
choco install rsync
mkdir "c:\Program Files\Arsenal Image Mounter"
rsync -avp <root of "DriverSetup>\DriverSetup "/cygdrive/c/Program Files/Arsenal Image Mounter"
cd C:\Program Files\Arsenal Image Mounter\DriverSetup\cli\x64>
PS C:\Program Files\Arsenal Image Mounter\DriverSetup\cli\x64> .\aim_ll.exe --install "C:\Program Files\Arsenal Image Mounter\DriverSetup"
```

Reboot the system


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

