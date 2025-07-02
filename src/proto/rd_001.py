import sys

sys.path.append("../")

from ramdisk.ramdisk import RamDisk


memSize = 100

mountPoint = "/tmp/tmpDrive"

#####
# create ramdisk with specific mountpoint 
ramdisk = RamDisk(str(memSize), str(mountPoint), "")
ramdisk.getNlogData()
ramdisk.getNprintData()

