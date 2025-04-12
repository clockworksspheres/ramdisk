import sys
import getpass
sys.path.append("../")

from ramdisk.ramdisk import RamDisk
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp


memSize = 100

mountPoint = "/tmp/tmpDrive"

logger = CyLogger()
logger.initializeLogs()

mypasswd = getpass.getpass()

# passwd = "'" + passwd + "'"

# print(mypasswd)
#####
# create ramdisk with specific mountpoint
# logger, mode=700, uid=None, gid=None, fstype="tmpfs", nr_inodes=None, nr_blocks=None, creds=False, passwd="")
ramdisk = RamDisk(str(memSize), str(mountPoint), logger, passwd=str(mypasswd))
ramdisk.getNlogData()
ramdisk.getNprintData()

