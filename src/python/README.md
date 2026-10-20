
# Ramdisk interface

Interface to Ramdisk, provided by the RamDisk.py:

## example usage

```
from ramdisk.RamDisk import RamDisk, umount

# creates a disk of size 512Mb, at mount point /tmp/ram0
myramdisk = RamDisk(512, "/tmp/ram0")

# unmount the ramdisk
umount("/tmp/ram0")
```

## Ramdisk class

myramdisk = ramdisk.Ramdisk(size, mountpoint)

Creates a ramdisk with the above parameters.

* If no mountpoint is given, it will create a random mountpoint

* If no size is given, the default size if 512Mb. If 0 or negative
 number is given, a SizeInvalidError will be raised.

#### myramdisk.getData()

Getter for mount data, and if the mounting of a ramdisk was successful.
Does not print or log the data.

Returns:  (self.success, str(self.mntPoint), str(self.myRamdiskDev))

#### myramdisk.getNlogData()

Getter for mount data, and if the mounting of a ramdisk was successful.
Also logs data.

Returns: (self.success, str(self.mntPoint), str(self.myRamdiskDev))

#### myramdisk.umount()

Unmount the disk connected with this instance.

## umount(device)

   Eject the ramdisk.
