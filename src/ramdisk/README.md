
## Ramdisk interface

Interface to Ramdisk, provided by the RamDisk.py:

## Ramdisk class

ramdisk = Ramdisk(size, mountpoint, logger)

Creates a ramdisk with the above parameters.

* If no logger(lib.CyLogger) is given, a new one will be created for this class. 

* If no mountpoint is given, it will create a random mountpoint

* If no size is given, the default size if 512Mb. If 0 or negative
 number is given, a SizeInvalidError will be raised.

 #### ramdisk.getData()

Getter for mount data, and if the mounting of a ramdisk was successful.
Does not print or log the data.

Returns:  (self.success, str(self.mntPoint), str(self.myRamdiskDev))

 #### ramdisk.getNlogData()

Getter for mount data, and if the mounting of a ramdisk was successful.
Also logs data.

Returns: (self.success, str(self.mntPoint), str(self.myRamdiskDev))

#### ramdisk.umount()

Unmount the disk.

Returns: True/False, whether the disk was unmounted or not.

#### umount(device, logger)

   Eject the ramdisk.

