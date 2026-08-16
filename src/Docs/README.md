Support documentation discussion on various specific topics, including issues faced when building this project, and setting up the various test environments and CI/CD related activities.

(Background)[../../README.md]

# Usage

Basic usage can be found in [setup_ramdisk_example.py](../examples/setup_ramdisk_example.py)

## The [Ramdisk interface](../ramdisk/RamDisk.py):

The following functionality is available for every operating system.  Other RamDisk methods may or may not be available for every operating sysytem.

____RamDisk(size, mountpoint)___: create a ramdisk of a specific size and mountpoint
* size: Size of the ramdisk in megabytes
* mountpoint: location on the filesystem to mount the ramdisk

___RamDisk.umount()___: unmount the current ramdisk instance

___RamDisk.getMountPoint()___: returns the mountpoint - the location on the filesystem where the ramdisk is mounted.

___RamDisk.getDevice()___: returns the device the ramdisk is attached to.

___RamDisk.getData()__: returns the data describing the current ramdisk

___RamDisk.getNprintData()___: prints and returns the data describing the current ramdisk instance.

___RamDisk.getNlogData()___: logs and returns the data describing the current ramdisk instance.

___umount(device)___: Function to unmount the ramdisk assigned 'device'.
* device: the operating system device the RamDisk is attached to.

___eject(device)___: Duplicate function to unmount the ramdisk assigned to 'device'
* device: the operating system device the RamDisk is attached to.


