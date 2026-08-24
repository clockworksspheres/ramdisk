# Problems installing Windows on UTM/VMware/Virtualbox Apple M series hardware

https://github.com/utmapp/UTM/issues/4818

## This is applicable for VMware as well as UTM:


### Windows asking for a network driver, and there is no way to install one

```
If Windows 11 setup is stuck due to lack of network connection:

Go to the language select screen (you may need to restart the setup if you are past this screen).  
Press Shift + F10 to launch Command Prompt.  
Type in OOBE\BYPASSNRO and press Enter.  
Your VM should reboot and at the setup screen you should see an option for “I don’t have internet.”  
Once Windows setup is completed, make sure to install the SPICE guest tools for network drivers.
```

