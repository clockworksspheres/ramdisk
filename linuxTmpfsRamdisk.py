"""
Linux tmpfs ramdisk implementation

@author: Roy Nielsen
"""
#--- Native python libraries
import os
import re
import pwd
import sys
import traceback
from tempfile import mkdtemp
from time import time

#--- non-native python libraries in this source tree
from lib.run_commands import RunWith
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp
from commonRamdiskTemplate import RamDiskTemplate, NotValidForThisOS, BadRamdiskArguments
from lib.libHelperExceptions import SystemToolNotAvailable, UserMustBeRootError

###############################################################################

class RamDisk(RamDiskTemplate):
    """
    http://www.cyberciti.biz/tips/what-is-devshm-and-its-practical-usage.html

    In this example, remount /dev/shm with 8G size as follows:

    # mount -o remount,size=8G /dev/shm

    To be frank, if you have more than 2GB RAM + multiple Virtual machines,
    this hack always improves performance. In this example, you will give you
    tmpfs instance on /disk2/tmpfs which can allocate 5GB RAM/SWAP in 5K inodes
    and it is only accessible by root:

    # mount -t tmpfs -o size=5G,nr_inodes=5k,mode=700 tmpfs /disk2/tmpfs

    Where,

    -o opt1,opt2 : Pass various options with a -o flag followed by a comma
                   separated string of options. In this examples, I used the
                   following options:
       remount : Attempt to remount an already-mounted filesystem. In this
                 example, remount the system and increase its size.
       size=8G or size=5G : Override default maximum size of the
                           /dev/shm filesystem. he size is given in bytes,
                           and rounded up to entire pages. The default is half
                           of the memory. The size parameter also accepts a
                           suffix % to limit this tmpfs instance to that
                           percentage of your pysical RAM: the default, when
                           neither size nor nr_blocks is specified, is
                           size=50%. In this example it is set to 8GiB or 5GiB.
                           The tmpfs mount options for sizing ( size,
                           nr_blocks, and nr_inodes) accept a suffix k, m or
                           g for Ki, Mi, Gi (binary kilo, mega and giga) and
                           can be changed on remount.
       nr_inodes=5k : The maximum number of inodes for this instance. The
                      default is half of the number of your physical RAM pages,
                      or (on a machine with highmem) the number of lowmem RAM
                      pages, whichever is the lower.
       mode=700 : Set initial permissions of the root directory.
       tmpfs : Tmpfs is a file system which keeps all files in virtual memory.

    ---------------------------------------------------------------------------

    Another link:
    http://www.jamescoyle.net/how-to/943-create-a-ram-disk-in-linux

    Exerpt:
    mount -t [TYPE] -o size=[SIZE],opt2=[opt2],opt3=[opt3] [FSTYPE] [MOUNTPOINT]
    Substitute the following attirbutes for your own values:

    [TYPE] is the type of RAM disk to use; either tmpfs or ramfs.
    [SIZE] is the size to use for the file system. Remember that ramfs does not
           have a physical limit and is specified as a starting size.
    [FSTYPE] is the type of RAM disk to use; either tmpfs, ramfs, ext4, etc.
    Example:

    mount -t tmpfs -o size=512m tmpfs /mnt/ramdisk

    """
    def __init__(self, size, mountpoint,  logger,
                 mode=700, uid=None, gid=None,
                 fstype="tmpfs", nr_inodes=None, nr_blocks=None):
        """
        """
        super(RamDisk, self).__init__(size, mountpoint, logger)
        #####
        # The passed in size of ramdisk should be in 1Mb chunks
        self.module_version = '20160224.032043.009191'
        self.logger = logger
        if not sys.platform.startswith("linux"):
            raise NotValidForThisOS("This ramdisk is only viable for a Linux.")

        if fstype in ["tmpfs", "ramfs"]:
            self.fstype = fstype
            if fstype == "tmpfs":
                self.myRamdiskDev = "/dev/tmpfs"
        else:
            raise BadRamdiskArguments("Not a valid argument for " + \
                                           "'fstype'...")

        if not os.geteuid() == 0:
            raise UserMustBeRootError("You must be root, or have elevated with sudo to use this software...")

        if isinstance(mode, int):
            self.mode = mode
        else:
            self.mode = 700

        if not isinstance(uid, int):
            self.uid = os.getuid()
        else:
            self.uid = uid

        if not isinstance(gid, int):
            self.gid = os.getgid()
        else:
            self.gid = gid

        if isinstance(nr_inodes, basestring):
            self.nr_inodes = nr_inodes
        else:
            self.nr_inodes = None

        if isinstance(nr_blocks, basestring):
            self.nr_blocks = nr_blocks
        else:
            self.nr_blocks = None

        #####
        # Initialize the mount and umount command paths...
        self.mountPath = ""
        self.umountPath = ""
        self.getCmds()

        #####
        # Initialize the RunWith helper for executing shelled out commands.
        self.runWith = RunWith(self.logger)
        #self.runWith.getNlogReturns()
        self.success = self._mount()
        self.logger.log(lp.DEBUG, "Finishing linux ramdisk init...")


    ###########################################################################

    def getCmds(self):
        """
        Acquire the paths for mount and umount on the system...

        @author: Roy Nielsen
        """
        success = False
        paths = ["/bin", "/usr/bin", "/sbin", "/usr/sbin", "/usr/local/bin", "/user/local/sbin"]

        #####
        # Look for the mount command
        mountFound = False
        for path in paths:
            possibleFullPath = os.path.join(path, "mount")
            if os.path.exists(possibleFullPath):
                self.mountPath = possibleFullPath
                mountFound = True
                
        if not mountFound:
            raise SystemToolNotAvailable("Cannot find mount command...") 

        #####
        # Look for the umount command
        umountFound = False
        for path in paths:
            possibleFullPath = os.path.join(path, "umount")
            if os.path.exists(possibleFullPath):
                self.umountPath = possibleFullPath
                umountFound = True
                
        if not umountFound:
            raise SystemToolNotAvailable("Cannot find umount command...")

        #####
        # Figure out if this method was successfull or not.
        if mountFound and umountFound:
            success = True

        return success

    ###########################################################################

    def buildCommand(self):
        """
        Build a command based on the "fstype" passed in.

        For more options on the tmpfs filesystem, check the mount manpage.

        @author: Roy Nielsen
        """
        command=None
        if self.fstype == "ramfs":
            command = [self.mountPath, "-t", "ramfs"]
        elif self.fstype == "tmpfs":
            options = ["size=" + str(self.diskSize) + "m"]
            options.append("uid=" + str(self.uid))
            options.append("gid=" + str(self.gid))
            options.append("mode=" + str(self.mode))
            """
            try:
                options.append(self.nr_inodes)
            except AttributeError:
                pass
            try:
                options.append("nr_blocks=" + str(self.nr_blocks))
            except AttributeError:
                pass
            """

            command = [self.mountPath, "-t", "tmpfs", "-o",
                       ",".join(options), "tmpfs", self.mntPoint]
            self.logger.log(lp.DEBUG, "command: " + str(command))
            #/bin/mount -t tmpfs  -o size=500m,uid=0,gid=0,mode=700 /tmp/tmp0gnLNt
        return command

    ###########################################################################

    def _format(self) :
        """
        One can't really format a tmpfs disk, so this will mimic a format 
        by unmounting an recreating the disk.

        @author: Roy Nielsen
        """
        success = False
        successOne = self.umount()
        successTwo = self._mount()
        if successOne and successTwo:
            success = True
        return success

    ###########################################################################

    def _mount(self) :
        """
        Mount the disk

        @author: Roy Nielsen
        """
        success = False
        
        if not os.path.exists(self.mntPoint):
            os.makedirs(self.mntPoint)
            self.logger.log(lp.DEBUG, "Created mount point")
        elif os.path.exists(self.mntPoint) and not os.path.isdir(self.mntPoint):
            # Cannot use mkdtmp here because it will make the directory on
            # the root filesystem instead of the ramdisk, then it will try
            # to link across filesystems which won't work
            tmpdir = self.mntPoint + "." + str(time())
            os.rename(self.mntPoint, tmpdir)
            os.mkdir(self.mntPoint)

        command = self.buildCommand()
        self.logger.log(lp.WARNING, "Command: " + str(command))
        self.runWith.setCommand(command)
        output, error, returncode = self.runWith.communicate()
        self.logger.log(lp.DEBUG, "output    : " + str(output))
        self.logger.log(lp.DEBUG, "error     : " + str(error))
        self.logger.log(lp.DEBUG, "returncode: " + str(returncode))

        if not error:
            success = True
            self.logger.log(lp.DEBUG, "Damn it Jim! The Damn Thing worked!!!")
        self.getNlogData()
        return success

    ###########################################################################

    def remount(self, size=0, mountpoint="", mode=700, uid=None, gid=None,
                nr_inodes=None, nr_blocks=None):
        """
        Use the tmpfs ability to be remounted with different options

        If bad input is given, the previous values will be used.

        @author: Roy Nielsen
        """
        #####
        # Input Validation:
        #####
        # tmpfs is the only viable ramdisk that handles remounting ok.
        # this includes mouting tmpfs with msdos, ext2,3,4, etc.
        if not self.fstype == "tmpfs":
            raise BadRamdiskArguments("Can only use 'remount' with " + \
                                           "tmpfs...")
        if size and isinstance(size, int):
            self.diskSize = size

        if mountpoint and isinstance(mountpoint, type.string):
            self.mntPoint = mountpoint

        if mode and isinstance(mode, int):
            self.mode = mode

        if uid and isinstance(uid, int):
            self.uid = uid

        if gid and isinstance(gid, int):
            self.gid = gid

        if nr_inodes and isinstance(nr_inodes, (int, long)):
            self.nr_inodes = nr_inodes

        if nr_blocks and isinstance(nr_blocks, (int, long)):
            self.nr_blocks = nr_blocks

        self.buildCommand()
        self._mount()

    ###########################################################################

    def unmount(self) :
        """
        Unmount the disk

        @author: Roy Nielsen
        """
        success = False

        command = [self.umountPath, self.mntPoint]
        self.runWith.setCommand(command)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()
        if not reterr:
            success = True

        return success

    ###########################################################################

    def umount(self):
        """
        Unmount the disk

        @author: Roy Nielsen
        """
        success = False

        success = self.unmount()
        return success

    ###########################################################################

    def detach(self) :
        """
        Unmount the disk

        @author: Roy Nielsen
        """
        success = False

        success = self.umount()

        return success

    ###########################################################################

    def __isMemoryAvailable(self):
        """
        Check to make sure there is plenty of memory of the size passed in
        before creating the ramdisk

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        #mem_free = psutil.phymem_usage()[2]

        #print "Memory free = " + str(mem_free)
        success = False
        return success

    ###########################################################################

    def getVersion(self):
        """
        Getter for the version of the ramdisk

        @author: Roy Nielsen
        """
        return self.module_version

###############################################################################

def detach(mnt_point="", logger=False):
    """
    Mirror for the unmount function...

    @author: Roy Nielsen
    """
    success = umount(mnt_point, logger)
    return success

###############################################################################

def umount(mnt_point="", logger=False):
    """
    Unmount the ramdisk

    @author: Roy Nielsen
    """
    success = False
    if mnt_point:

        paths = ["/bin", "/usr/bin", "/sbin", "/usr/sbin", "/usr/local/bin", "/user/local/sbin"]

        #####
        # Look for the umount command
        umountFound = False
        umountPath = ""
        for path in paths:
            possibleFullPath = os.path.join(path, "umount")
            if os.path.exists(possibleFullPath):
                umountPath = possibleFullPath
                umountFound = True
                
        if not umountFound:
            raise SystemToolNotAvailable("Cannot find umount command...")

        #####
        # Run the umount command...
        runWith = RunWith(logger)
        command = [umountPath, mnt_point]
        runWith.setCommand(command)
        runWith.communicate()
        retval, reterr, retcode = runWith.getNlogReturns()
        if not reterr:
            success = True

    return success

def unmount(mnt_point="", logger=False):
    '''
    mirror functioin for umount
    '''
    success = False
    success = umount(mnt_point, logger)
    return success
