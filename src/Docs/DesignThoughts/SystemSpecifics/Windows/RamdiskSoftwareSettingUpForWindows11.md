# Ramdisk Software: Setting up the ramdisk library and examples for Windows 11

## Installing the AIM toolkit

### Please be sure to adhere to the Software License appropriate for your use!

Licensing and information about [AIMtk here](https://arsenalrecon.com/products/arsenal-image-mounter):  

## Setting up the Windows PATH to include the AIM toolkit software

```

```

## Setting up the WMIC system software in Windows 11

```
Add-WindowsCapability -online -name WMIC
```

The command that the ramdisk library uses in Windows to check to see what drives are already used is:

```
wmic logicaldisk get caption
```

WMIC is depreciated and will be removed in a future version of Windows.  There are plans to replace this functionality with some command similar to:

```

```

## To run before running the ramdisk software or the build scripts, in a administrator powershell:

```

```

## To run before running scripts

```

```

