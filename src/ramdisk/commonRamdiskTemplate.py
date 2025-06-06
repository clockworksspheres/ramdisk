"""
Template for the ramdisk classes

@author: Roy Nielsen
"""
#--- Native python libraries
from tempfile import mkdtemp
import sys

sys.path.append("..")

#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.loggers import CyLogger

###########################################################################

class NotValidForThisOS(Exception):
    """
    Meant for being thrown when an action/class being run/instanciated is not
    applicable for the running operating system.

    @author: Roy Nielsen
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

###########################################################################

class BadRamdiskArguments(Exception):
    """
    Meant for being thrown when an invalid values are passed in as arguments
    to class instanciation or class methods.

    @author: Roy Nielsen
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)

###############################################################################

class RamDiskTemplate(object):
    """
    """
    def __init__(self, size=0, mountpoint=False, logger=False, **kwargs):
        """
        was: def __init__(self, size=0, mountpoint=False, logger=False, **kwargs):

        """
        #####
        # Version/timestamp is
        # <YYYY><MM><DD>.<HH><MM><SS>.<microseconds>
        # in UTC time
        self.module_version = '20160224.032043.009191'

        mytime = '%Y-%m--%d-%H-%S--%f'
        logname = sys.argv[0].split("/")[-1] + mytime

        if not logger and not isinstance(logger, CyLogger):
            self.logger = CyLogger()
            self.logger.initializeLogs("/tmp", logname)
        else:
            self.logger = logger
        self.logger.log(lp.INFO, "Logger: " + str(self.logger))

        if size:
            self.diskSize = size
        else:
            self.diskSize = 512
        self.success = False
        self.myRamdiskDev = None
        if not mountpoint:
            self.getRandomizedMountpoint(**kwargs)
        else:
            self.mntPoint = mountpoint

        self.logger.log(lp.INFO, "disk size: " + str(self.diskSize))
        self.logger.log(lp.INFO, "volume name: " + str(self.mntPoint))

    ###########################################################################

    def getData(self, **kwargs):
        """
        Getter for mount data, and if the mounting of a ramdisk was successful

        Does not print or log the data.

        @author: Roy Nielsen
        """
        return (self.success, str(self.mntPoint), str(self.myRamdiskDev))

    ###########################################################################

    def getNlogData(self, **kwargs):
        """
        Getter for mount data, and if the mounting of a ramdisk was successful

        Also logs the data.

        @author: Roy Nielsen
        """
        self.logger.log(lp.INFO, "Success: " + str(self.success))
        self.logger.log(lp.INFO, "Mount point: " + str(self.mntPoint))
        self.logger.log(lp.INFO, "Device: " + str(self.myRamdiskDev))
        return (self.success, str(self.mntPoint), str(self.myRamdiskDev))

    ###########################################################################

    def getNprintData(self, **kwargs):
        """
        Getter for mount data, and if the mounting of a ramdisk was successful
        """
        print("Success: " + str(self.success))
        print("Mount point: " + str(self.mntPoint))
        print("Device: " + str(self.myRamdiskDev))
        return (self.success, str(self.mntPoint), str(self.myRamdiskDev))

    ###########################################################################

    def getRandomizedMountpoint(self):
        """
        Create a randomized (secure) mount point - per python's implementation
        of mkdtemp - a way to make an unguessable directory on the system

        @author: Roy Nielsen
        """
        success = False
        self.mntPoint = ""
        try :
            self.mntPoint = mkdtemp()
        except Exception as err :
            self.logger.log(lp.WARNING, "Exception trying to create temporary directory")
            raise err
        else :
            success = True
            self.logger.log(lp.WARNING,
                            "Success: " + str(success) +
                            " in get_randomizedMountpoint: " +
                            str(self.mntPoint))
        self.logger.log(lp.WARNING, "Randomized mount point: \"" + str(self.mntPoint) + "\"")
        return success

    ###########################################################################

    def umount(self, **kwargs):
        """
        Unmount the disk - same functionality as __eject on the mac

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        success = False
        return success

    ###########################################################################

    def unmount(self, **kwargs):
        """
        Unmount the disk - same functionality as __eject on the mac

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        success = False
        return success

    ###########################################################################

    def __isMemoryAvailable(self, **kwargs):
        """
        Check to make sure there is plenty of memory of the size passed in
        before creating the ramdisk

        @author: Roy Nielsen
        """
        success = False
        return success

    ###########################################################################

    def _format(self, **kwargs):
        """
        Format the ramdisk

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        success = False
        return success

    ###########################################################################

    def getDevice(self, **kwargs):
        """
        Getter for the device name the ramdisk is using

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        return self.myRamdiskDev

    ###########################################################################

    def getMountPoint(self, **kwargs):
        """
        Getter for the mount point name the ramdisk is using

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        return self.mntPoint

    ###########################################################################

    def setDevice(self, device=None, **kwargs):
        """
        Setter for the device so it can be ejected.

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        self.myRamdiskDev = device

    ###########################################################################

    def getVersion(self):
        """
        Getter for the version of the ramdisk

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        return self.module_version

###############################################################################


def detach(device=None, **kwargs):
    """
    Eject the ramdisk

    Must be over-ridden to provide OS/Method specific functionality

    @author: Roy Nielsen
    """
    success = False
    return success

