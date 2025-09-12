"""
Windows Ramdisk class based on use of ImDisk windows program


"""
#--- Native python libraries
from tempfile import mkdtemp
import re
import sys

sys.path.append("../")

#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.run_commands import RunWith
from ramdisk.lib.fsHelper.ntfsFsHelper import FsHelper
from ramdisk.commonRamdiskTemplate import RamDiskTemplate

###########################################################################


class RamDisk(RamDiskTemplate):
    """
    block size not needed like it is for macos... that could change
    and if it's needed, there is a way in fsHelper to get the block 
    size or set the block size for the ramdisk. That function can be
    found in the ramdisk/lib/fsHandler/ntFsHandler.py FsHandler.getFsBlockSize() method.
    """
    def __init__(self, size=512, mountpoint=False, logger=False):
        """
        """
        #####
        # Version/timestamp is
        # <YYYY><MM><DD>.<HH><MM>
        # in UTC time
        self.module_version = '2024.10051117'
        #####
        # provided by RamdiskTemplate from commonRamdiskTemplate...
        if not isinstance(logger, CyLogger):
            self.logger = CyLogger()
            self.logger.initializeLogs()
        else:
            self.logger = logger
        self.runCmd = RunWith(self.logger)
        self.fsHelper = FsHelper()
        self.logger.log(lp.INFO, "Logger: " + str(self.logger))
        self.diskSize = self.fsHelper.getDiskSize(size)
        self.diskSize = self.diskSize[1].strip('mMgG')
        self.success = False
        self.myRamdiskDev = self.imDiskNumber = None

        # Need to have a config file or pass in a location for or hard code or
        # command line pass in the location of the AIM Toolkit binary
        self.aim_ll = "c:\Program Files\AIM Toolkit\aim_ll.exe"
        self.mntPoint = ""
        if not mountpoint:
            self.getRandomizedMountpoint()
        else:
            if self.mntPointAvailable(mountpoint):
                self.mntPoint = mountpoint

        #command to see what mountpoints have already been taken:
        self.getMntPntsCmd = ["wmic", "logicaldisk", "get", "caption"]

        # get the disk id's of AIMtk disks, including disk numbers
        self.getImDiskIdsCmd = ["aim_ll", "-l"]

        # command to get AIMtk info on a specificly numbered disk
        self.getIdXNameCmd = ["aim_ll", "-l", "-u", self.imDiskNumber]

        self.fsType = "ntfs"
        self.driveType = "hd"
        self.writeMode = "rw"
        success = False
        #####
        # Get an ImDisk Ram Disk
        if(self.__isMemoryAvailable()):
            success = self.__createRamdisk()

        self.logger.log(lp.DEBUG, "disk size: " + str(self.diskSize))
        self.logger.log(lp.DEBUG, "volume name: " + str(self.mntPoint))
        # return success

    ###########################################################################

    def __createRamdisk(self):
        """
        Create a ramdisk device

        
        """
        retval = None
        reterr = None
        success = False
        #####
        # Create the ramdisk and attach it to a device.


        # cmd = [self.aim_ll, "-a", "-s", self.diskSize, "-m" self.mntPoint, -p "\"/fs:" + self.fsType + " /q /y\"", "-o" self.driveType + "," + self.writeMode]

        cmd = [self.aim_ll, "-a", "-s", self.diskSize + "M", "-m", self.mntPoint, "-p", '/fs:' + self.fsType + ' /q /y']

        print(str(cmd))

        self.logger.log(lp.WARNING, "Running command to create ramdisk: \n\t" + str(cmd))
        self.runCmd.setCommand(cmd, creationflags=True)
        self.runCmd.communicate()
        retval, reterr, retcode = self.runCmd.getNlogReturns()

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

        
        """
        return (self.success, str(self.mntPoint), str(self.myRamdiskDev))

    ###########################################################################

    def getNlogData(self):
        """
        Getter for mount data, and if the mounting of a ramdisk was successful

        Also logs the data.

        
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


    def mntPointAvailable(self, mntPoint=""):
        """
        Check if the passed in mount point is available, or if it's already being used.

            valid values: D - Z
        """
        success = False
        getMntPntsCmd  = ["wmic", "logicaldisk", "get", "caption"]
        self.logger.log(lp.WARNING, "Running command to create ramdisk: \n\t" + str(getMntPntsCmd))
        self.runCmd.setCommand(getMntPntsCmd)
        self.runCmd.communicate()
        retval, reterr, retcode = self.runCmd.getNlogReturns()

        self.logger.log(lp.WARNING, "retval: {0}".format(retval))

        if retcode == '':
            success = False
            raise Exception("Error trying to get list of mount points(" + str(reterr).strip() + ")")
        else:

            invalidMntPoints = []
            #####
            # Get the output and process it - for every line, put it in a list
            for line in retval:
                if line is not None:
                    if re.match('^[A-Z]', line):
                        line = line.strip()
                        invalidMntPoints.append(line.strip(":"))
                    else:
                        continue
                else:
                    continue
            self.logger.log(lp.INFO, str(invalidMntPoints))
            if re.match('^[D-Z]', mntPoint) and mntPoint not in invalidMntPoints:
                success = True
        return success


    ###########################################################################

    def umount(self, detach=True, dForce=False, rForce=False, mountpoint=None, unit=None):
        """
        Unmount the disk - same functionality as __eject on the mac

        Must be over-ridden to provide OS/Method specific functionality

        
        """
        success = False

        detachCmdOne = [ self.aim_ll, "-d", "-m", self.mntPoint ]
        detachCmdTwo = [ self.aim_ll, "-d", "-u", self.device ] 
        dForceCmdOne = [ self.aim_ll, "-D", "-m", self.mntPoint ] 
        dForceCmdTwo = [ self.aim_ll, "-D", "-u", self.device ] 
        rForceCmd = [ self.aim_ll, "-R", "-u", self.device ] 


        detachCmdThree = [ self.aim_ll, "-d", "-m", mountPoint ]
        detachCmdFour = [ self.aim_ll, "-d", "-u", unit ] 
        dForceCmdThree = [ self.aim_ll, "-D", "-m", mountPoint ] 
        dForceCmdFour = [ self.aim_ll, "-D", "-u", unit ] 
        rForceCmdTwo = [ self.aim_ll, "-R", "-u", unit ] 


        if not detach and not dForce and rForce and not mountpoint and unit == True and isinstance(unit, bool):
            umountCmd = rForceCmd
        if detach and not dForce and not rForce and not mountpoint and not unit:
            umountCmd = detachCmdOne
        if detach and not dForce and not rForce and not mountpoint and unit == True and isinstance(unit, bool):
            umountCmd = detachCmdTwo
        if not detach and dForce and not rForce and not mountpoint and not unit:
            umountCmd = dForceCmdOne
        if not detach and dForce and not rForce and not mountpoint and unit == True and isinstance(unit, bool):
            umountCmd = dForceCmdTwo

        if not detach and not dForce and rForce and not mountpoint and unit and isinstance(unit, int):
            umountCmd = rForceCmdTwo
        if detach and not dForce and not rForce and mountpoint and not unit:
            # at some point in the future the will be a function with a regex to validate a good mountpoint.
            umountCmd = dtachCmdThree
        if detach and not dForce and not rForce and not mountpoint and unit and isinstance(unit, int):
            umountCmd = dtachCmdFour
        if not detach and dForce and not rForce and mountpoint and not unit:
            # at some point in the future the will be a function with a regex to validate a good mountpoint.
            umountCmd = dForceCmdThree
        if not detach and dForce and not rForce and not mountpoint and unit and isinstance(unit, int):
            umountCmd = dForceCmdFour

        else:
            self.logger.log(lp.ERROR, "Sorry, Invalid Command...") 
            return success

        self.logger.log(lp.WARNING, "Running command to create ramdisk: \n\t" + str(umountCmd))
        self.runCmd.setCommand(umountCmd)
        self.runCmd.communicate()
        retval, reterr, retcode = self.runCmd.getNlogReturns()

        if retcode == '':
            success = False
            raise Exception("Error trying to unmount drive : (" + str(reterr).strip() + ")")
        else:
            success = True
            self.logger.log(lp.INFO, "Looks like the drive unmounted : ( \n\n str(retval) \n")

        return success

    ###########################################################################

    def unmount(self, detach=True, dForce=False, rForce=False, mountpoint=None, unit=None):
        """
        Unmount the disk - same functionality as __eject on the mac

        Must be over-ridden to provide OS/Method specific functionality

        
        """
        success = False
        success = self.umount(detach, dForce, rForce, mountpoint, unit)
        return success

    ###########################################################################

    def __isMemoryAvailable(self):
        """
        Check to make sure there is plenty of memory of the size passed in
        before creating the ramdisk

        
        """
        # Commands with pipes, better off as strings - and with quotes, done as below, with myshell=True in the cmd call
        cmd = 'systeminfo|find "Available Physical Memory"'

        self.logger.log(lp.WARNING, "Running command to create ramdisk: \n\t" + str(cmd))
        self.runCmd.setCommand(cmd, myshell=True)
        self.runCmd.communicate()
        retval, reterr, retcode = self.runCmd.getNlogReturns()

        self.logger.log(lp.ERROR, "retval: {0}".format(retval))

        if retcode == '':
            success = False
            raise Exception("Error trying to get list of mount points(" + str(reterr).strip() + ")")
        else:

            # returns:
            # Available Physical Memory: 56,861 Mb

            tmplist = retval.split()
            tmpmem = tmplist[3]
            if re.search(",", tmpmem):
                mem = re.sub(",", "", tmpmem)
            else:
                mem = tmpmem.strip()

            lvl = retval[4]

            self.logger.log(lp.ERROR, "mem: {0}  lvl: {1} ...".format(mem, lvl))
            
            print(f"     diskSize: {self.diskSize}")
            # self.diskSize = self.diskSize[1].strip('mMgG')
            if int(self.diskSize) < int(mem) and re.match("^\d+$", mem):
                success = True
            elif re.match("^kb$", lvl):
                self.logger.log(lp.ERROR, "NOT ENOUGH PHYSICAL MEMORY............................................")
            else:
                self.logger.log(lp.ERROR, "NOT ENOUGH PHYSICAL MEMORY............................................")
                
        return success

    ###########################################################################

    def _format(self):
        """
        Format the ramdisk

        Must be over-ridden to provide OS/Method specific functionality

        
        """
        success = False
        return success

    ###########################################################################

    def getDevice(self):
        """
        Getter for the device name the ramdisk is using

        Must be over-ridden to provide OS/Method specific functionality

        
        """
        return self.myRamdiskDev

    ###########################################################################

    def getMountPoint(self):
        """
        Getter for the mount point name the ramdisk is using

        Must be over-ridden to provide OS/Method specific functionality

        
        """
        return self.mntPoint

    ###########################################################################

    def setDevice(self, device=None):
        """
        Setter for the device so it can be ejected.

        Must be over-ridden to provide OS/Method specific functionality

        
        """
        self.myRamdiskDev = device

    ###########################################################################

    def getVersion(self):
        """
        Getter for the version of the ramdisk

        Must be over-ridden to provide OS/Method specific functionality

        
        """
        return self.module_version

###############################################################################

logger = CyLogger()

def detach(detach=True, dForce=False, rForce=False, mountpoint=None, unit=None):
    """
    """
    success = False
    success = umount(detach, dForce, rForce, mountpoint, unit)
    return success


def unmount(detach=True, dForce=False, rForce=False, mountpoint=None, unit=None):
    success = False
    success = umount(detach, dForce, rForce, mountpoint, unit)
    return success


def umount(detach=True, dForce=False, rForce=False, mountpoint=None, unit=None):
    """
    Eject the ramdisk

    Must be over-ridden to provide OS/Method specific functionality

    
    """
    success = False


    runCmd = RunWith()
    umountcmd = ''

    detachCmdOne = [ "aim_ll", "-d", "-m", mountpoint ]
    detachCmdTwo = [ "aim_ll", "-d", "-u", unit ]
    dForceCmdOne = [ "aim_ll", "-D", "-m", mountpoint ]
    dForceCmdTwo = [ "aim_ll", "-D", "-u", unit ]
    rForceCmd    = [ "aim_ll", "-R", "-u", unit ]

    if not detach and not dForce and rForce and not mountpoint and unit and isinstance(unit, int):
        umountCmd = rForceCmdTwo
    if detach and not dForce and not rForce and mountpoint and not unit:
        # at some point in the future the will be a function with a regex to validate a good mountpoint.
        umountCmd = dtachCmdThree
    if detach and not dForce and not rForce and not mountpoint and unit and isinstance(unit, int):
        umountCmd = dtachCmdFour
    if not detach and dForce and not rForce and mountpoint and not unit:
        # at some point in the future the will be a function with a regex to validate a good mountpoint.
            umountCmd = dForceCmdThree
    if not detach and dForce and not rForce and not mountpoint and unit and isinstance(unit, int):
        umountCmd = dForceCmdFour

    else:
        logger.log(lp.ERROR, "Sorry, Invalid Command...")
        return success

        logger.log(lp.WARNING, "Running command to unmount ramdisk: \n\t" + str(umountCmd))
        runCmd.setCommand(umountCmd)
        runCmd.communicate()
        retval, reterr, retcode = runCmd.getNlogReturns()

        if retcode == '':
            success = False
            raise Exception("Error trying to unmount drive : (" + str(reterr).strip() + ")")
        else:
            success = True
            logger.log(lp.INFO, "Looks like the drive unmounted : ( \n\n str(retval) \n")

    return success


def getMountData(device):
    """
    For macOS, show both mount and diskutil data
    """
    print("Entering getMountData")
    print("Exiting getMountData")
    return {}
'''
    runWith = RunWith()


    #####
    # Set up and run the mount command
    cmd = ["/sbin/mount"]

    output = ""

    runWith.setCommand(cmd)
    output, _, _ = runWith.communicate()

    mountInfo = ""
'''

def getMountDisks():
    """
    should return the a dictionary with {device: diskName, ...} that contains
    every mounted disk
    """
    print("Entering getMountedDisks")
    print("Exiting getMountedDisks")
    return {}
"""
    runWith = RunWith()

    mountedDisks = {}

    devList = []
    diskDict = {}
    retval = ""
    disk = ""

    #####
    # Diskutil list, then parse for RAMDISK in output, get the device
    cmd = ["diskutil", "list"]
    runWith.setCommand(cmd)
    runWith.communicate()
    retval, reterr, retcode = runWith.getNlogReturns()
"""
