#!/usr/bin/env -S python -u
"""
Mac ramdisk + unionfs implementation

@Notes:  Below are the initial notes for creating a ramdisk on the Mac

Things we need to modularize:
* create
* mount
* unmount
* detach?
* format (newfs_hfs vs. diskutil)
* randomize mountpoint
* turn off journaling, for faster access
* unionfs setup

Maybe function, or other module
* Find available memory,
  - Linux - just read /proc
  - Mac - Use top's "unused" so it doesn't try to use swap
          swap would defeat the purpose.

Maybe function, method  or other module
* rsync from spinning disk to ram disk


"""
#--- Native python libraries
import os
import re
import sys
import getpass
import shutil
import traceback
from subprocess import Popen, PIPE

#####
# Include the parent project directory in the PYTHONPATH
# appendDir = "/".join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
# sys.path.append(appendDir)
sys.path.append("../")

#--- non-native python libraries in this source tree
from ramdisk.lib.run_commands import RunWith
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.environment import Environment
from ramdisk.lib.libHelperExceptions import NotValidForThisOS, MemoryNotAvailableError
from ramdisk.lib.fsHelper.macosFsHelper import FsHelper
from ramdisk.commonRamdiskTemplate import RamDiskTemplate

###############################################################################

class RamDisk(RamDiskTemplate):
    """
    Class to manage a ramdisk

    Size passed in must be passed in as 1Mb chunks

    @param: size - size of the ramdisk to create - must have a value on the Mac
                   or the creation will fail.

                  when getting input for the size of the ramdisk, use 
                  r"d+[GgMm][Bb]" for size regex


    @param: mountpoint - where to mount the disk, if left empty, will mount
                         on locaiton created by tempfile.mkdtemp.
    @param: message_level - level at which to log.

    
    """
    def __init__(self, size=0, mountpoint="", logger=False, disableJournal=False, **kwargs) :
        """
        Constructor
        """
        super().__init__(size, mountpoint, logger, **kwargs)

        #####
        # Provided by commonRamdiskTemplate....
        #        if not isinstance(logger, CyLogger):
        #            self.logger = CyLogger()
        #            self.logger.initializeLogs()   
        #        else:
        #            self.logger = logger

        self.environ = Environment()
        self.fsHelper = FsHelper()

        if not self.environ.getosfamily() == "darwin":
            raise NotValidForThisOS("This ramdisk is only viable for a MacOS.")

        self.module_version = '20160225.125554.540679'

        if isinstance(disableJournal, bool):
            self.disableJournal = disableJournal
        else:
            self.disableJournal = False

        #####
        # Initialize the RunWith helper for executing shelled out commands.
        self.runWith = RunWith(self.logger)

        #####
        # Get the block size for this system
        success, self.blockSize = self.fsHelper.getFsBlockSize()

        #####
        # Convert size to expected size in Mb - useing \d+[GgMm][Bb] 
        # for size regex in fsHelper to determine size in megabytes
        success, size = self.fsHelper.getDiskSizeInMb(size)

        self.free = ""

        #####
        # Calculating the size of ramdisk in 1Mb chunks
        numerator = int(size) * 1024 * 1024  # 1024 * 1024 = 1 megabyte
        denominator = self.blockSize    # block size for apfs, 512 for hfs
        fSize = numerator / denominator
        iSize = int(fSize)
        self.diskSize = str(iSize)

        self.hdiutil = "/usr/bin/hdiutil"
        self.diskutil = "/usr/sbin/diskutil"

        #####
        # Just /dev/disk<#>
        self.myRamdiskDev = ""

        #####
        # should take the form of /dev/disk2s1, where disk 2 is the assigned
        # disk and s1 is the slice, or partition number.  While just /dev/disk2
        # is good for some things, others will need the full path to the
        # device, such as formatting the disk.
        self.devPartition = ""

        #####
        # Indicate if the ramdisk is "mounted" in the Mac sense - attached,
        # but not mounted.
        self.mounted = False

        success = False

        #####
        # Passed in disk size must have a non-default value
        print("diskSize: " + str(self.diskSize))
        self.logger.log(lp.DEBUG, "diskSize: " + str(self.diskSize))
        if not self.diskSize == 0 :
            success  = True
        print("########### IS THERE AVAILABLE MEMORY???? ##############")
        #####
        # Checking to see if memory is availalbe...
        # if not self.__isMemoryAvailable():
        if not self.__isMemAvailable():
            self.logger.log(lp.DEBUG, "Physical memory not available to create ramdisk.")
            # self.logger
            success = False
        else:
            success = True
        self.logger.log(lp.DEBUG, "got passed checking for available memory")
        if success :

            #####
            # If a mountpoint is passed in, use that, otherwise, set up for a
            # random mountpoint.
            self.logger.log(lp.DEBUG, "attempting mountpoint...")
            if mountpoint:
                self.logger.log(lp.INFO, "\tMOUNTPOINT: " + str(mountpoint))
                self.mntPoint = mountpoint
                #####
                # eventually have checking to make sure that directory
                # doesn't already exist, and have data in it.
                if not os.path.exists(self.mntPoint):
                    os.makedirs(self.mntPoint)
            else :
                #####
                # If a mountpoint is not passed in, create a randomized
                # mount point.
                self.logger.log(lp.DEBUG, "Attempting to acquire a radomized mount " + \
                           "point. . .")
                if not self.getRandomizedMountpoint() :
                    success = False
            print("##### <<<< GOT MOUNT POINT <<<< ######")
            self.logger.log(lp.DEBUG, "acquired mount point...")
            #####
            # The Mac has a more complicated method of managing ramdisks...
            if success:
                print("########## ATTEMPTING TO CREATE>>>>>> ##########")
                #####
                # Attempt to create the ramdisk
                try:
                    self.__create()
                except:
                    success = False
                    self.logger.log(lp.WARNING, "Create appears to have failed..")
                    raise
                else:
                    #####
                    # Ramdisk created, try mounting it.
                    #self.__mount()
                    pass #raise
                    # self.__remove_journal()
                    
        self.getNlogData()
        self.success = success
        if success:
            self.logger.log(lp.INFO, "Mount point: " + str(self.mntPoint))
            self.logger.log(lp.INFO, "Device: " + str(self.myRamdiskDev))
        self.logger.log(lp.INFO, "Success: " + str(self.success))


    ###########################################################################

    def __create(self):
        """
        Create a ramdisk device

        Create the RAM disk:
            disk=$(hdiutil attach -nomount ram://<size>)
        Format the RAM disk with APFS and name it:
            diskutil erasevolume APFS "MyRAMDiskName" /dev/$disk
        Disable journaling on the RAM disk:
            diskutil apfs disableJournal /dev/$disk
        Rename the RAM disk using diskutil:
            diskutil rename /dev/$disk "RAMDiskNameReplacement"
                ....Replace RAMDiskNameReplacement with the desired 
                    name for your RAM disk.
        #####
        # THIS should be the process:
        hdiutil attach -nomount ram://1048576
        # the above command returns the <ramdisk device> - /dev/diskXs1
        diskutil partitionDisk $(/dev/diskXs1) 1 GPTFormat APFS 'RAMDisk' '100%'
        diskutil umount /dev/diskXs1
        newfs_apfs -v RAMDisk /dev/diskXs1
        mkdir -P <mountpoint>
        mount_apfs /dev/diskXs1 /<mountpoint>
        chown -R <user> /<mountpoint>

        #####

        cmd = [self.hdiutil, "attach", "-nomount", "ram://" + self.diskSize]
        cmd = ["/usr/sbin/diskutil", "partitionDisk", self.myRamdiskDev, "1", "GPTFormat", "APFS", "'RAMDisk'", f"{hundred}"]
        cmd = [self.diskutil, "unmount", self.myRamdiskDev]
        cmd = ["/sbin/newfs_apfs", "-v", "RAMDISK", self.myRamdiskDev]
        self.fsHelper.mkdirs(self.mntPoint)
        cmd = "/sbin/mount_apfs " + self.myRamdiskDev + " " + self.mntPoint
        self.fsHelper.chown(self.mntPoint, user)

        
        """
        retval = None
        reterr = None
        # success = False
        #####
        # Create the ramdisk and attach it to a device.
        # disk=$(hdiutil attach -nomount ram://<size>)
        print("Creating the ramdrive...")
        cmd = [self.hdiutil, "attach", "-nomount", "ram://" + self.diskSize]
        self.logger.log(lp.WARNING, "Running command to create ramdisk: \n\t" + str(cmd))
        self.runWith.setCommand(cmd)
        retval, reterr, retcode = self.runWith.communicate()
        # retval, reterr, retcode = self.runWith.getNlogReturns()
        
        if retcode == '':
            success = False
        else:
            self.myRamdiskDev = retval.strip()
            # self.logger.log(lp.DEBUG, "Device: \"" + str(self.myRamdiskDev) + "\"")
            success = True
        
        self.myRamdiskDev = retval.strip()
        self.logger.log(lp.DEBUG, "Device: \"" + str(self.myRamdiskDev) + "\"")
        #####
        # Erase the ramdisk and Name the device.
        # this command makes the mountpoint owned by root. Need it owned by the user
        # diskutil erasevolume APFS "MyRAMDiskName" /dev/$disk
        # this command makes the mountpoint owned by root. Need it owned by the user
        # cmd = [self.diskutil, "eraseVolume", "APFS", self.mntPoint, self.myRamdiskDev]
        ###
        # to format with user owning the disk, instead of root
        #cmd = ["/sbin/newfs", self.mntPoint, self.myRamdiskDev]
        self.logger.log(lp.WARNING, "Creating the ramdrive at: " + self.myRamdiskDev)
        print("Creating the ramdrive at: " + self.myRamdiskDev)
        #####
        # This command works better than either of the two above....
        # diskutil partitionDisk self.myRamdiskDev 1 GPTFormat APFS 'RAMDisk' '100%'
        tmpmntpnt = self.mntPoint.split('/')[-1]
        print("testmntpnt: " + tmpmntpnt)
        hundred = f"'100%'"
        try:
            cmd = ["/usr/sbin/diskutil", "partitionDisk", self.myRamdiskDev, "1", "GPTFormat", "APFS", "'RAMDisk'", f"{hundred}"]
            self.logger.log(lp.WARNING, "Running command to create ramdisk: " + str(cmd))
            print("Running command to create ramdisk: " + str(cmd))
            self.runWith.setCommand(cmd)
            self.runWith.communicate()
        except:
            raise
        # retval, reterr, retcode = self.runWith.getNlogReturns()
        #####
        # unmounting the disk, because it is automatically mounted to /Volumes,
        # so we can mount it where the user wishes
        try:
            cmd = [self.diskutil, "unmount", self.myRamdiskDev]
            self.logger.log(lp.WARNING, "Running command to unmount ramdisk: >> " + str(cmd))
            self.runWith.setCommand(cmd)
            self.runWith.communicate()
        except:
            raise
        # retval, reterr, retcode = self.runWith.getNlogReturns()

        try:
            cmd = ["/sbin/newfs_apfs", "-v", "RAMDISK", self.myRamdiskDev]
            self.logger.log(lp.WARNING, "Running command to create ramdisk: " + str(cmd))
            print("Running command to create ramdisk: " + str(cmd))
            self.runWith.setCommand(cmd)
            self.runWith.communicate()
        except:
            raise


        tmpNum = ""
        tmpDev = ""
        try:
            tmpMatch = re.match(r"(\S+)(\d+)", self.myRamdiskDev.strip())
            tmpDev = tmpMatch.group(1)
            tmpNum = tmpMatch.group(2)
            
        except ValueError:
            raise

        tmpNum = int(tmpNum) + 1
        self.myRamdiskDev = str(tmpDev) + str(tmpNum) + "s1"
        self.logger.log(lp.DEBUG, "Device: \"" + str(self.myRamdiskDev) + "\"")

        self.logger.log(lp.WARNING, "  MYRAMDISKDEV: " + self.myRamdiskDev)
        self.logger.log(lp.WARNING, "  MNTPOINT: " + self.mntPoint)

        # Create the mountpoint, if it exists, skip
        self.fsHelper.mkdirs(self.mntPoint)
        self.logger.log(lp.WARNING, " ... Making mountpoint: " + self.mntPoint)

        #####
        # mount the drive to the correct mount point
        try:
            cmd = "/sbin/mount_apfs " + self.myRamdiskDev + " " + self.mntPoint
            self.logger.log(lp.WARNING, "Running command to MOUNT ramdisk: >>>>> " + str(cmd))
            self.runWith.setCommand(cmd)
            self.runWith.communicate()
        except:
            raise
        # retval, reterr, retcode = self.runWith.getNlogReturns()

        """
        # MAY make the ramdisk go faster...  
        # *** WARNING *** Test thouroughly if you uncomment this section,
        # it may not go here in the workflow . . .
        if self.disableJournal is True:
            #####
            # Disable Journaling on the device.
            # diskutil apfs disableJournal /dev/$disk
            print("Creating the ramdrive...")
            cmd = [self.diskutil, "apfs", "disableJournal", self.myRamdiskDev]
            self.logger.log(lp.WARNING, "Running command to create ramdisk: \n\t" + str(cmd))
            self.runWith.setCommand(cmd)
            self.runWith.communicate()
            retval, reterr, retcode = self.runWith.getNlogReturns()
        else:
            pass
        """
        #####
        # Need to chown the mountpoint to the user, because the mount point is by 
        # default not owned by the user on *nix systems
        user = getpass.getuser()
        self.fsHelper.chown(self.mntPoint, user)

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

    def getMountedData(self):
        """
        should return the a dictionary with {device: diskName, ...} that contains
        every mounted disk
        """
        print("Entering getMountedData")

        mountedDisks = {}

        devList = []
        diskDict = {}
        mountedDisks = {}
        retval = ""
        disk = ""

        #####
        # Diskutil list, then parse for RAMDISK in output, get the device
        cmd = ["diskutil", "list"]
        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()

        for line in retval.split("\n"):
            if re.search("RAMDISK", line):
                disk = line.split()[-1]
                devList.append(disk)
                print(f"{disk}")

        #####
        # mount, to use device to get mount name
        cmd = ["mount"]
        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()

        for line in retval.split("\n"):
            dev = line.split()[0] in devList
            if dev:
                for mountDev in devList:
                    if re.match(f"{dev}", mountDev):
                        diskDict[dev] = line.split()[2]
                        print(f"{line.split()[2]}")
                        continue
            dev = ""

        try:
            mountedDisks = diskDict
        except:
            pass
        print("MountedDisks: " + str(mountedDisks))
        return mountedDisks

    ###########################################################################

    def __mount(self) :
        """
        Mount the disk - for the Mac, just run self.__attach

        
        """
        success = False
        success = self.__attach()
        if success:
            self.mounted = True
        return success

    ###########################################################################

    def __attach(self):
        """
        Attach the device so it can be formatted

        
        """
        success = False
        #####
        # Attempt to partition the disk.
        if self.__partition():
            success = True
            #####
            # eraseVolume format name device
            if self.mntPoint:
                #####
                # "Mac" unmount (not eject)
                cmd = [self.diskutil, "unmount", self.myRamdiskDev]
                self.runWith.setCommand(cmd)
                self.runWith.communicate()
                retval, reterr, retcode = self.runWith.getNlogReturns()

                if not reterr:
                    success = True

                if success:
                    #####
                    # remount to self.mntPoint
                    cmd = [self.diskutil, "mount", "-mountPoint",
                           self.mntPoint, self.devPartition]
                    self.runWith.setCommand(cmd)
                    self.runWith.communicate()
                    retval, reterr, retcode = self.runWith.getNlogReturns()

                    if not reterr:
                        success = True
            self.runWith.getNlogReturns()
            self.getData()
            self.logger.log(lp.DEBUG, "Success: " + str(success) + " in __mount")
        return success

    ###########################################################################

    def __remove_journal(self) :
        """
        Having a journal in ramdisk makes very little sense.  Remove the journal
        after creating the ramdisk device

        cmd = ["/usr/sbin/diskutil", "disableJournal", "force", myRamdiskDev]

        using "force" doesn't work on a mounted filesystem, without it, the
        command will work on a mounted file system

        
        """
        success = False
        cmd = [self.diskutil, "disableJournal", self.myRamdiskDev + "s1"]
        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()
        if not reterr:
            success = True
        self.logger.log(lp.DEBUG, "Success: " + str(success) + " in __remove_journal")
        return success

    ###########################################################################

    def unionOver(self, target="", fstype="hfs", nosuid=None, noowners=True,
                        noatime=None, nobrowse=None):
        """
        Use unionfs to mount a ramdisk on top of a location already on the
        filesystem.

        @parameter: target - where to lay the ramdisk on top of, ie the lower
                             filesystem layer.

        @parameter: nosuid - from the mount manpage: "Do not allow
                             set-user-identifier bits to take effect.

        @parameter: fstype - What supported filesystem to use.

        @parameter: noowners - From the mount manpage: "Ignore the ownership
                               field for the entire volume.  This causes all
                               objects to appear as owned by user ID 99 and
                               group ID 99.  User ID 99 is interpreted as
                               the current effective user ID, while group
                               99 is used directly and translates to "unknown".

        @parameter: noatime - from the mount manpage: "Do not update the file
                              access time when reading from a file.  This
                              option is useful on file systems where there are
                              large numbers of files and performance is more
                              critical than updating the file access time
                              (which is rarely ever important).

        @parameter: nobrowse - from the mount manpage: "This option indicates
                               that the mount point should not be visible via
                               the GUI (i.e., appear on the Desktop as a
                               separate volume).

        
        """
        success = False

        #####
        # If the ramdisk is mounted, unmount it (not eject...)
        if self.mounted:
            self._unmount()

        #####
        # Create the target directory if it doesn't exist yet...
        if not os.path.isdir(target):
            if os.path.isfile(target):
                shutil.move(target, target + ".bak")
            os.makedirs(target)

        #####
        # Put together the command if the base options are given
        if fstype and self.devPartition:
            #####
            # Compile the options
            options = "union"
            if nosuid:
                options = options + ",nosuid"
            if noowners:
                options = options + ",noowners"
            if noatime:
                options = options + ",noatime"
            if nobrowse:
                options = options + ",nobrowse"
            #####
            # Put the command together.
            cmd = ["/sbin/mount", "-t", str(fstype), "-o", options,
                   self.devPartition, target]

            #####
            # Run the command
            self.runWith.setCommand(cmd)
            self.runWith.communicate()
            retval, reterr, retcode = self.runWith.getNlogReturns()
            if not reterr:
                success = True

        return success

    ###########################################################################

    def unmount(self) :
        """
        Unmount the disk - same functionality as __eject on the mac

        
        """
        success = False
        if self.eject() :
            success = True
        self.logger.log(lp.DEBUG, "Success: " + str(success) + " in unmount")
        return success

    ###########################################################################

    def detach(self) :
        """
        Unmount the disk - same functionality as __eject on the mac

        
        """
        success = False
        if self.eject() :
            success = True
        self.logger.log(lp.DEBUG, "Success: " + str(success) + " in detach")
        return success

    ###########################################################################

    def _unmount(self) :
        """
        Unmount in the Mac sense - ie, the device is still accessible.

        
        """
        success = False
        cmd = [self.diskutil, "unmount", "force", self.devPartition]
        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()
        if not reterr:
            success = True
        return success

    ###########################################################################

    def _mount(self) :
        """
        Mount in the Mac sense - ie, mount an already accessible device to
        a mount point.

        
        """
        success = False
        cmd = [self.diskutil, "mount", "-mountPoint", self.mntPoint, self.devPartition]
        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()
        print("######################################")
        print("Printing mounting process...")
        print("return code: " + str(retcode))
        print("return error: " + str(reterr))
        print("return value: " + str(retval))
        print("######################################")
        if not reterr:
            success = True
        return success

    ###########################################################################

    def eject(self) :
        """
        Eject the ramdisk

        Detach (on the mac) is a better solution than unmount and eject
        separately.. Besides unmounting the disk, it also stops any processes
        related to the mntPoint

        
        """
        success = False
        cmd = [self.hdiutil, "detach", self.myRamdiskDev]
        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()
        if not reterr:
            success = True
        self.runWith.getNlogReturns()

        return success

    ###########################################################################

    def _format(self) :
        """
        Format the ramdisk

        
        """
        success = False
        #####
        # Unmount (in the mac sense - the device should still be accessible)
        # Cannot format the drive unless only the device is accessible.
        success = self._unmount()
        #####
        # Format the disk (partition)
        cmd = ["/sbin/newfs_hfs", "-v", "ramdisk", self.devPartition]
        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()
        if not reterr:
            success = True
        #####
        # Re-mount the disk
        self._mount()
        return success

    ###########################################################################

    def __partition(self) :
        """
        Partition the ramdisk (mac specific)

        
        """
        success=False
        numerator = int(self.diskSize)
        denominator = 2*1024
        fSize = int(numerator/denominator)
        size = str(fSize)
        cmd = [self.diskutil, "partitionDisk", self.myRamdiskDev, str(1),
               "MBR", "HFS+", "ramdisk", str(size) + "M"]
        self.runWith.setCommand(cmd)
        self.runWith.communicate()
        retval, reterr, retcode = self.runWith.getNlogReturns()
        if not reterr:
            success = True
        print("######################################")
        print("Printing partitioning process...")
        print("return code: " + str(retcode))
        print("return error: " + str(reterr))
        print("return value: " + str(retval))
        print("######################################")
        if success:
            #####
            # Need to get the partition device out of the output to assign to
            # self.devPartition
            for line in retval.split("\n"):
                if re.match(r'^Initialized (\S+)\s+', line):
                    linematch = re.match(r'Initialized\s+(\S+)', line)
                    rdevPartition = linematch.group(1)
                    self.devPartition = re.sub("rdisk", "disk", rdevPartition)
                    break

        self.runWith.getNlogReturns()

        return success


    ###########################################################################

    def __isMemAvailable(self) :
        """
        """
        success = False
        line = ""
        self.free = 0
        freeNumber = 0
        freeMagnitute = ""
        tmpFree = ""

        #####
        # Set up and run the command
        cmd = ["/usr/bin/top", "-l", "1"]

        self.runWith.setCommand(cmd)
        output, _, _ = self.runWith.communicate()
        # output, _, _ = self.runWith.waitNpassThruStdout("Networks")

        for line in output.split("\n"):
            self.logger.log(lp.DEBUG, "line: " + str(line))
            tmpData = line.split()
            try:
                lastWord = tmpData[-1]
                nextWord = tmpData[-2]
            except IndexError as err:
                pass # self.logger.log(self.lp.DEBUG, )
                continue

            print("words: {}, {}", lastWord, nextWord)
            self.logger.log(lp.DEBUG, "words: " + lastWord + " : " + nextWord)
            if re.search("unused", line):
                # self.logger.log
                tmpFree = nextWord
                break
        self.logger.log(lp.DEBUG, "free: " + str(tmpFree))
        if tmpFree:
            sizeCompile = re.compile(r"(\d+)(\w+)")

            split_size = sizeCompile.search(tmpFree)
            freeNumber = split_size.group(1)
            freeMagnitude = split_size.group(2)

            freeNumber = str(freeNumber).strip()
            freeMagnitude = str(freeMagnitude).strip()

            if re.match(r"^\d+$", freeNumber.strip()):
                if re.match(r"^\w$", freeMagnitude.strip()):
                    #####
                    # Calculate the size of the free memory in Megabytes
                    if re.search("G", freeMagnitude.strip()):
                        freeMem = 1024 * int(freeNumber)
                        freeNumber = str(freeMem)
                        self.free = freeNumber
                        freeMagnitude = "M"
                    elif re.search("M", freeMagnitude.strip()):
                        self.free = freeNumber.strip() 
        print("Free Memory: " + str(self.free))
        print("disk size:   "  + str(self.diskSize))
        self.logger.log(lp.DEBUG, "Free Memory: " + str(self.free))
        self.logger.log(lp.DEBUG, "disk size:   "  + str(self.diskSize))
        # if int(self.free) > int(float(self.diskSize)):
        if int(self.free) > int(float(int(self.diskSize)/(2*1024))):
            success = True
        else:
            raise MemoryNotAvailableError("Memory Not Available for Creating the Ramdisk, Free up Memory to Create a Ramdisk...")

        # return freeNumber, freeMagnitude
        return success

    ###########################################################################

    def __isMemoryAvailable(self) :
        """
        Check to make sure there is plenty of memory of the size passed in
        before creating the ramdisk

        Best method to do this on the Mac is to get the output of "top -l 1"
        and # re.search("unused" line), as below

        
        """
        #mem_free = psutil.phymem_usage()[2]

        #print "Memory free = " + str(mem_free)
        success = False
        found = False
        almost_size = 0
        size = 0
        self.free = 0
        line = ""
        freeMagnitude = None

        #####
        # Set up and run the command
        cmd = ["/usr/bin/top", "-l", "1"]

        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)

        while True:
            line = proc.stdout.readline().strip()
            #####
            # Split on spaces
            line = line.split()
            #####
            # Get the last item in the list
            found = line[-1]
            almost_size = line[:-1]
            size = almost_size[-1]

            found = str(found).strip()
            #almost_size = almost_size.strip()
            size = str(size).strip()

            self.logger.log(lp.INFO, "size: " + str(size))
            self.logger.log(lp.INFO, "found: " + str(found))

            if re.search("unused", found) or re.search("free", found):
                #####
                # Found the data we wanted, stop the search.
                break
        proc.kill()

        #####
        # Find the numerical value and magnitute of the ramdisk
        if size:
            sizeCompile = re.compile(r"(\d+)(\w+)")

            split_size = sizeCompile.search(size)
            freeNumber = split_size.group(1)
            freeMagnitude = split_size.group(2)
            
            freeNumber = str(freeNumber).strip()
            freeMagnitude = str(freeMagnitude).strip()

            if re.match(r"^\d+$", freeNumber.strip()):
                if re.match(r"^\w$", freeMagnitude.strip()):
                    if freeMagnitude:
                        #####
                        # Calculate the size of the free memory in Megabytes
                        if re.search("G", freeMagnitude.strip()):
                            self.free = 1024 * int(freeNumber)
                            self.free = str(self.free)
                        elif re.search("M", freeMagnitude.strip()):
                            self.free = freeNumber
        self.logger.log(lp.DEBUG, "free: " + str(self.free))
        self.logger.log(lp.DEBUG, "Size requested: " + str(self.diskSize))
        if int(self.free) > int(float(self.diskSize)):
            success = True
        else:
            raise MemoryNotAvailableError("Memory Not Available for Creating the Ramdisk, Free up Memory to Create a Ramdisk...")

        print(str(self.free))
        print(str(success))
        return success

    ###########################################################################

    def getMountData(self, device):
        """
        For macOS, show both mount and diskutil data
        """

        #####
        # Set up and run the mount command
        cmd = ["/sbin/mount"]

        output == ""

        self.runWith.setCommand(cmd)
        output, _, _ = self.runWith.communicate()

        mountInfo = ""

        for line in output.split("\n"):
            if re.search(f"{device}", line):
                mountInfo = line

        #####
        # Set up and run the diskutil command
        cmd = ["/usr/sbin/diskutil", "list", device]

        output == ""

        self.runWith.setCommand(cmd)
        output, _, _ = self.runWith.communicate()

        diskutilInfo = ""

        if output:
            diskutilInfo = output

        message = f"mountLine:\n{mountLine}\n\ndiskutil info:\n{diskutilInfo}"

        return message, mountInfo, diskutilInfo

    ###########################################################################

    def getDevice(self):
        """
        Getter for the device name the ramdisk is using

        
        """
        return self.myRamdiskDev

    ###########################################################################

    def setDevice(self, device=None):
        """
        Setter for the device so it can be ejected.

        
        """
        if device:
            self.myRamdiskDev = device
        else:
            raise Exception("Problem trying to set the device..")

    ###########################################################################

    def getVersion(self):
        """
        Getter for the version of the ramdisk

        
        """
        return self.module_version


###############################################################################

def unmount(device=" ", logger=False):
    """
    On the Mac, call detach.

    
    """
    detach(device, logger)

###############################################################################

def umount(device=" ", logger=False):
    """
    On the Mac, call detach.

    
    """
    detach(device, logger)

###############################################################################

def detach(device=" ", logger=False):
    """
    Eject the ramdisk
    Detach (on the mac) is a better solution than unmount and eject
    separately.. Besides unmounting the disk, it also stops any processes
    related to the mntPoint

    
    """
    success = False
    if not logger:
        logger = CyLogger()
    else:
        logger = logger
    myRunWith = RunWith(logger)
    if not re.match(r"^\s*$", device):
        cmd = ["/usr/bin/hdiutil", "detach", device]
        myRunWith.setCommand(cmd)
        myRunWith.communicate()
        retval, reterr, retcode = myRunWith.getNlogReturns()
        if not reterr:
            success = True

        myRunWith.getNlogReturns()
    else:
        raise Exception("Cannot eject a device with an empty name..")
    return success

###########################################################################

def getMountData(device):
    """
    For macOS, show both mount and diskutil data
    """
    runWith = RunWith()


    #####
    # Set up and run the mount command
    cmd = ["/sbin/mount"]

    output = ""

    runWith.setCommand(cmd)
    output, _, _ = runWith.communicate()

    mountInfo = ""

    for line in output.split("\n"):
        if re.search(f"{device}", line):
            mountInfo = line

    #####
    # Set up and run the diskutil command
    cmd = ["/usr/sbin/diskutil", "list", device]

    output == ""

    runWith.setCommand(cmd)
    output, _, _ = runWith.communicate()

    diskutilInfo = ""

    if output:
        diskutilInfo = output

    message = f"mountLine:\n{mountInfo}\n\ndiskutil info:\n{diskutilInfo}"

    return message, mountInfo, diskutilInfo


def getMountDisks():
    """
    should return the a dictionary with {device: diskName, ...} that contains
    every mounted disk
    """
    print("Entering getMountedDisks")

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

    for line in retval.split("\n"):
        if re.search("RAMDISK", line):
            try:
                disk = line.split()[-1]
                devList.append(disk)
                print(f"{disk}")
            except IndexError:
                continue

    print(str(devList))

    #####
    # mount, to use device to get mount name
    cmd = ["mount"]
    runWith.setCommand(cmd)
    runWith.communicate()
    retval, reterr, retcode = runWith.getNlogReturns()

    print(f"retval: {str(retval)}")

    for line in retval.split("\n"):
        if line:
            # print("Parsing mount command output...")
            dev = ""
            fullDevName = line.split()[0].strip()
            dev = fullDevName.split("/")[-1].strip()
            name = line.split()[2].strip()
            if re.search("^/private", name):
                name = name.removeprefix("/private")
            # print(f"    {dev}: {devList} ")
            if dev in devList:
                diskDict[name]= f"/dev/{dev}"
                print(f"{name} in {dev}")

    print(f"MountedDisks: {diskDict}")
    return diskDict

