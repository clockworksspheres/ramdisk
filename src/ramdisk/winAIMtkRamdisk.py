"""
Windows Ramdisk class based on use of ImDisk windows program


"""
#--- Native python libraries
from tempfile import mkdtemp
import os
import re
import sys
import subprocess

# 3rd party libs
import psutil 

sys.path.append("../")

#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.run_commands import RunWith
from ramdisk.lib.fsHelper.ntfsFsHelper import FsHelper
from ramdisk.commonRamdiskTemplate import RamDiskTemplate
from ramdisk.lib.fsHelper.winDriveTools import findDrive, cleanTrailingSlashes, cleanDrivePath, findMountName

###########################################################################


class RamDisk(RamDiskTemplate):
    """
    block size not needed like it is for macos... that could change
    and if it's needed, there is a way in fsHelper to get the block 
    size or set the block size for the ramdisk. That function can be
    found in the ramdisk/lib/fsHandler/ntFsHandler.py FsHandler.getFsBlockSize() method.
    """
    def __init__(self, size=512, mountpoint=False, logger=False, **kwargs):
        """
        """
        print("SIZE: " + str(size))
        print("MOUNTPOINT: " + str(mountpoint))

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
        if isinstance(size, int):
            self.diskSize = str(size)
        elif isinstance(size, str):
            self.diskSize = self.fsHelper.getDiskSize(size)
            self.diskSize = str(self.diskSize[1]).strip('mMgG')
        self.success = False
        self.myRamdiskDev = None

        # Need to have a config file or pass in a location for or hard code or
        # command line pass in the location of the AIM Toolkit binary

        # Better yet, set up the PATH to the aim_ll library
        
        self.mntPoint = ""
        if not mountpoint:
            self.getRandomizedMountpoint()
        else:
            #if findMountName(mountpoint):
            if self.mntPointAvailable(mountpoint):
                trailingSlashesCleanedPath = cleanTrailingSlashes(mountpoint)
                cleanedSlashes = cleanDrivePath(trailingSlashesCleanedPath)
                self.mntPoint = cleanedSlashes
                #self.mntPoint = trailingSlashesCleanedPath
                print("MOUNTPOINT: " + str(self.mntPoint))
            else:
                trailingSlashesCleanedPath = cleanTrailingSlashes(mountpoint)
                cleanedSlashes = cleanDrivePath(trailingSlashesCleanedPath)
                self.mntPoint = cleanedSlashes

        # get the disk id's of AIMtk disks, including disk numbers
        self.getAIMtkDiskIdsCmd = ["aim_ll", "-l"]

        self.fsType = "ntfs"
        self.driveType = "hd"
        self.writeMode = "rw"
        success = False
        #####
        # Get an AIMTk Ram Disk
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

        # command translated from imdisk command
        #cmd = ["aim_ll", "-a", "-s", self.diskSize + "M", "-m", self.mntPoint, "-p", '/fs:' + self.fsType + ' /q /y']

        #mountPath = cleanDrivePath(self.mntPoint)

        cleanPath = re.sub(r"\\{1,}", r'\\', self.mntPoint)

        # params = "/fs:ntfs /v:TestRam /q /y"
        params = f"/fs:{self.fsType} /q /y"

        cmd = r'aim_ll -a -s ' + str(self.diskSize) + r'M -m "' + cleanPath + r'" -p "' + params + r'"'

        print(str(cmd))

        self.logger.log(lp.WARNING, "Running command to create ramdisk: \n\t" + str(cmd))
        #self.runCmd.setCommand(cmd, creationflags=True)
        # f.runCmd.communicate()
        #retval, reterr, retcode = self.runCmd.communicate()

        retval = subprocess.run(cmd, capture_output=True, text=True)

        #print('RETVAL: "' + str(retval)+ '"')

        if retval == '':
            success = False
            #print('RETVAL: "'+ str(retval) + '"')
            raise Exception("Error trying to create ramdisk(" + str(reterr).strip() + ")")
        else:

            # Get the device
            result = str(retval)

            print(result)

            # in result string, replast string \r\n to control characters \r\n
            #result = re.sub(r"\\r\\n", r"\r\n", result)
            result = re.sub(r"\\n", r"\n", result)
            device = ""
            for line in result.splitlines():
                print(str(line))
                if re.match("Created device", line) and re.search("memory", line.strip().split()[-1]):
                    device = line.split()[2]
                    print("FOUND DEVICE: " + str(device))
                    break
                else:
                    continue

            self.myRamdiskDev = device
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

            valid values: can be in either aim_ll -l, or in powershell command given.
        """
        print("MountPoint: " + str(mntPoint))
        # make sure there is a drive in the path is valid and mounted.
        #driveExists = findDrive(mntPoint)
        #if not driveExists:
        #    return False
        #else:

        cleanPath = re.sub(r"\\{1,}", r"\\", mntPoint)
        try:
            if os.path.isdir(cleanPath):
                print("\tDirectory Exists")
                return True
            else:
                # Create it relative to the current working directory
                print("\t Creating Directory")
                os.makedirs(cleanPath, exist_ok=True)
                return True
        except FileExistsError:
                pass


    ###########################################################################

    def umount(self, **kwargs):
        """
        Unmount the disk - same functionality as __eject on the mac

        Must be over-ridden to provide OS/Method specific functionality

        
        """
        success = False

        umountCmd = [ self.aim_ll, "-R", "-u", self.myRamdiskDev ]

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

    def unmount(self, **kwargs):
        """
        Unmount the disk - same functionality as __eject on the mac

        Must be over-ridden to provide OS/Method specific functionality

        
        """
        success = False
        success = False

        umountCmd = [ self.aim_ll, "-R", "-u", self.myRamdiskDev ]

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

    def __isMemoryAvailable(self):
        """
        Check to make sure there is plenty of memory of the size passed in
        before creating the ramdisk

        
        """
        success = False

        mem = psutil.virtual_memory()

        freemem = mem.free / (1024**2)
        # totalmem = mem.total / (1024**2)

        # self.logger.log(lp.ERROR, "mem: {0}  lvl: {1} ...".format(mem, lvl))
        
        print(f"     diskSize: {self.diskSize}")
        # self.diskSize = self.diskSize[1].strip('mMgG')
        if int(self.diskSize) < int(freemem) and re.match(r"^\d+$", str(int(freemem))):
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

def detach(device, logger=False):
    """
    """
    success = False

    runCmd = RunWith()

    umountCmd    = [ "aim_ll", "-R", "-u", device ]

    print(f"umount {device}")

    #logger.log(lp.WARNING, "Running command to unmount ramdisk: \n\t" + str(umountCmd))
    runCmd.setCommand(umountCmd)
    runCmd.communicate()
    retval, reterr, retcode = runCmd.getNlogReturns()

    if retcode == '':
        success = False
        raise Exception("Error trying to unmount drive : (" + str(reterr).strip() + ")")
    else:
        success = True
        #logger.log(lp.INFO, "Looks like the drive unmounted : ( \n\n str(retval) \n")

    return success


def unmount(device, logger=False):
    success = False

    runCmd = RunWith()

    umountCmd    = [ "aim_ll", "-R", "-u", device ]

    print(f"umount {device}")

    #logger.log(lp.WARNING, "Running command to unmount ramdisk: \n\t" + str(umountCmd))
    runCmd.setCommand(umountCmd)
    runCmd.communicate()
    retval, reterr, retcode = runCmd.getNlogReturns()

    if retcode == '':
        success = False
        raise Exception("Error trying to unmount drive : (" + str(reterr).strip() + ")")
    else:
        success = True
        #logger.log(lp.INFO, "Looks like the drive unmounted : ( \n\n str(retval) \n")

    return success


def umount(device, logger=False):
    """
    Eject the ramdisk

    Must be over-ridden to provide OS/Method specific functionality
    
    """
    success = False

    runCmd = RunWith()

    umountCmd    = [ "aim_ll", "-R", "-u", device ]

    print(f"umount {device}")

    #logger.log(lp.WARNING, "Running command to unmount ramdisk: \n\t" + str(umountCmd))
    runCmd.setCommand(umountCmd)
    runCmd.communicate()
    retval, reterr, retcode = runCmd.getNlogReturns()

    if retcode == '':
        success = False
        raise Exception("Error trying to unmount drive : (" + str(reterr).strip() + ")")
    else:
        success = True
        #logger.log(lp.INFO, "Looks like the drive unmounted : ( \n\n str(retval) \n")

    return success


def eject(device, logger=False):
    """
    Eject the ramdisk

    Must be over-ridden to provide OS/Method specific functionality
    
    """
    success = False

    runCmd = RunWith()

    umountCmd    = [ "aim_ll", "-R", "-u", device ]

    print(f"umount {device}")

    #logger.log(lp.WARNING, "Running command to unmount ramdisk: \n\t" + str(umountCmd))
    runCmd.setCommand(umountCmd)
    runCmd.communicate()
    retval, reterr, retcode = runCmd.getNlogReturns()

    if retcode == '':
        success = False
        raise Exception("Error trying to unmount drive : (" + str(reterr).strip() + ")")
    else:
        success = True
        #logger.log(lp.INFO, "Looks like the drive unmounted : ( \n\n str(retval) \n")

    return success


def getMountData(device):
    """
    For macOS, show both mount and diskutil data
    """
    print("Entering getMountData")
    cmd = f"aim_ll -l -u {device}"

    print(str(cmd))

    runCmd = RunWith()

    runCmd.setCommand(cmd, creationflags=True)
    runCmd.communicate()
    retval, reterr, retcode = self.runCmd.getNlogReturns()

    if retcode == '':
        raise Exception("Error trying to create ramdisk(" + str(reterr).strip() + ")")
    else:
        deviceName = findMountName(device)
        
    print("Exiting getMountData")
    return deviceName


def getMountDisks():
    """
    should return the a dictionary with {device: diskName, ...} that contains
    every mounted disk
    """
    mnts = {}
    result = subprocess.run(r'aim_ll -l', capture_output=True, text=True)
    print(str(result.stdout))
    #result = re.sub(r"\\n", r"\n", result)
    for line in result.stdout.splitlines():
        line = line.strip()
        if re.search(r"\\\\\\\\", line):
            continue
        elif re.match("Device number \d+", line):
            print("Looking for device: " + line)
            # anchor = True
            device = line.split()[-1]
            print("Found Device: " + device)
        elif re.search(r':\\.*', line):
            # print(line)
            mountname = line.split("Mounted at ")[1]
            #mountname = line.split()[-1]
        elif not line:
            #anchor = False
            try:
                print(f"{device} : {mountname}")
                mnts[mountname] = device
            except UnboundLocalError:
                continue
            continue
    return mnts

