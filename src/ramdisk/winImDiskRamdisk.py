"""
Windows Ramdisk class based on use of ImDisk windows program

@author: Roy Nielsen
"""
#--- Native python libraries
from tempfile import mkdtemp
import re

#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.run_commands import RunWith

###########################################################################


class RamDisk(object):
    """
    """
    def __init__(self, size=0, mountpoint=False, logger=False):
        """
        """
        #####
        # Version/timestamp is
        # <YYYY><MM><DD>.<HH><MM>
        # in UTC time
        self.module_version = '2024.10051117'
        if not isinstance(logger, CyLogger):
            self.logger = CyLogger()
        else:
            self.logger = logger
        self.logger.log(lp.INFO, "Logger: " + str(self.logger))
        self.diskSize = size
        self.success = False
        self.myRamdiskDev = self.imDiskNumber = None

        # Need to have a config file or pass in a location for or hard code or
        # command line pass in the location of the ImDisk binary
        self.imdisk = "imdisk" 

        if not mountpoint:
            self.getRandomizedMountpoint()
        else:
            if self.mntPointAvailable():
                self.mntPoint = mountpoint

        #command to see what mountpoints have already been taken:
        self.getMntPntsCmd = ["wmic", "logicaldisk", "get", "caption"]

        # get the disk id's of imdisk disks, including disk numbers
        self.getImDiskIdsCmd = ["imdisk", -l"]

        # command to get imdisk info on a specificly numbered disk
        self.getIdXNameCmd = ["imdisk", "-l", "-u", self.imDiskNumber]

        self.rw = RunWith(self.logger)

        self.fsType = "ntfs"
        self.driveType = "hd"
        self.writeMode = "rw"

        #####
        # Get an ImDisk Ram Disk
        if(__isMemoryAvailable()):
            __createRamdisk()

        self.logger.log(lp.DEBUG, "disk size: " + str(self.diskSize))
        self.logger.log(lp.DEBUG, "volume name: " + str(self.mntPoint))

    ###########################################################################

    def __createRamdisk(self):
        """
        Create a ramdisk device

        @author: Roy Nielsen
        """
        retval = None
        reterr = None
        success = False
        #####
        # Create the ramdisk and attach it to a device.


        # cmd = [self.imdisk, "-a", "-s", self.diskSize, "-m" self.mountPoint, -p "\"/fs:" + self.fsType + " /q /y\"", "-o" self.driveType + "," + self.writeMode]

        cmd = [self.imdisk, "-a", "-s", self.diskSize, "-m" self.mountPoint, -p "\"/fs:" + self.fsType + " /q /y\""]

        print(str(cmd))

        self.logger.log(lp.WARNING, "Running command to create ramdisk: \n\t" + str(cmd))
        self.rw.setCommand(cmd)
        self.rw.communicate()
        retval, reterr, retcode = self.rw.getNlogReturns()

        if retcode == '':
            success = False
            raise Exception("Error trying to create ramdisk(" + str(reterr).strip() + ")")
        else:
            self.myRamdiskDev = retval.strip()
            self.logger.log(lp.DEBUG, "Device: \"" + str(self.myRamdiskDev) + "\"")
            success = True
        self.logger.log(lp.DEBUG, "Success: " + str(success) + " in __create")
        return success

    ###########################################################################

    def getData(self):
        """
        Getter for mount data, and if the mounting of a ramdisk was successful

        Does not print or log the data.

        @author: Roy Nielsen
        """
        return (self.success, str(self.mntPoint), str(self.myRamdiskDev))

    ###########################################################################

    def getNlogData(self):
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

    def getNprintData(self):
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


    def mntPointAvailable(self, mntPoint):
        """
        Check if the passed in mount point is available, or if it's already being used.

            valid values: D - Z
        """
        success = False

        self.logger.log(lp.WARNING, "Running command to create ramdisk: \n\t" + str(self.getMntPntsCmd))
        self.rw.setCommand(self.getMntPntsCmd)
        self.rw.communicate()
        retval, reterr, retcode = self.rw.getNlogReturns()

        if retcode == '':
            success = False
            raise Exception("Error trying to get list of mount points(" + str(reterr).strip() + ")")
        else:

            invalidMntPoints = []
            #####
            # Get the output and process it - for every line, put it in a list
            for line in retval:
                line = line.strip()
                invalidMntPoints.append(line.strip(":")

            if re.search('^[D-Z]$', mountpoint) and not in invalidMntPonts:
                success = True
        return success


    ###########################################################################

    def umount(self):
        """
        Unmount the disk - same functionality as __eject on the mac

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        success = False
        return success

    ###########################################################################

    def unmount(self):
        """
        Unmount the disk - same functionality as __eject on the mac

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        success = False
        return success

    ###########################################################################

    def __isMemoryAvailable(self):
        """
        Check to make sure there is plenty of memory of the size passed in
        before creating the ramdisk

        @author: Roy Nielsen
        """
        success = False

        cmd = ['systeminfo', '|', 'find' '"Available Physical Memory"']

        self.logger.log(lp.WARNING, "Running command to create ramdisk: \n\t" + str(cmd))
        self.rw.setCommand(cmd)
        self.rw.communicate()
        retval, reterr, retcode = self.rw.getNlogReturns()

        if retcode == '':
            success = False
            raise Exception("Error trying to get list of mount points(" + str(reterr).strip() + ")")
        else:

            # returns:
            # Available Physical Memory: 56,861 Mb

            tmplist = retval.split()
            tmpmem = retval[3]
            mem = re.sub(",", "", tmpmem) 

            lvl = retval[4]

            if int(self.diskSize) < int(mem):
                success = True
            elif re.match("^kb$", lvl):
                self.logger.log(ERR, "NOT ENOUGH PHYSICAL MEMORY............................................")
            else:
                self.logger.log(ERR, "NOT ENOUGH PHYSICAL MEMORY............................................")
                
        return success

    ###########################################################################

    def _format(self):
        """
        Format the ramdisk

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        success = False
        return success

    ###########################################################################

    def getDevice(self):
        """
        Getter for the device name the ramdisk is using

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        return self.myRamdiskDev

    ###########################################################################

    def getMountPoint(self):
        """
        Getter for the mount point name the ramdisk is using

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        return self.mntPoint

    ###########################################################################

    def setDevice(self, device=None):
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


def detach(device=None):
    """
    Eject the ramdisk

    Must be over-ridden to provide OS/Method specific functionality

    @author: Roy Nielsen
    """
    success = False
    return success

