"""
Template for the ramdisk classes


"""
import os
import sys
#--- Native python libraries
from tempfile import mkdtemp
import platform

#####
# Include the parent project directory in the PYTHONPATH
appendDir = "/".join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(appendDir)
#sys.path.append("../")

#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.environment import Environment
from ramdisk.lib.CheckApplicable import CheckApplicable
from ramdisk.commonRamdiskTemplate import RamDiskTemplate, BadRamdiskArguments, NotValidForThisOS
###############################################################################

if sys.platform.startswith("linux"):
    from ramdisk.linuxTmpfsRamdisk import RamDisk, unmount, getMountDisks, getMountData
elif sys.platform.startswith("darwin"):
    from ramdisk.macRamdisk import RamDisk, unmount, getMountDisks, getMountData
elif sys.platform.startswith("win32"):
    # if on the windows platform, the kernel version and os version is the same
    # so the following platform.version() call works.  If on other systems, it 
    # returns the kernel version information and this parsing method with throw
    # an exception.
    winverMajor = platform.win32_ver()[0]
    if winverMajor <= 10:
        from ramdisk.winImDiskRamdisk import RamDisk, unmount, getMountDisks, getMountData
    else:
        from ramdisk.winAIMtkRamdisk import RamDisk, unmount, getMountDisks, getMountData
else:
    raise NotValidForThisOS("Ramdisk not available here...")


class RamDisk(RamDiskTemplate):
    """
    Factory class for spawning concrete instances of a ramdisk.
    """
    def __init__(self, size=0, mountpoint=False, logger=False, **kwargs):
        """
        """
        #####
        # Version/timestamp is
        # <YYYY><MM><DD>.<HH><MM><SS>.<microseconds>
        # in UTC time
        self.module_version = '20160224.032043.009191'
        if not logger:
            self.logger = CyLogger()
        else:
            self.logger = logger

        self.environ = Environment()

        self.chkApp = CheckApplicable(self.environ, self.logger)
        
        #####
        # Check applicability to the current OS
        macApplicable = {'type': 'white',
                         'family': ['darwin']}
        macApplicableHere = self.chkApp.isApplicable(macApplicable)

        linuxApplicable = {'type': 'white',
                           'family': ['linux']}

        windowsApplicableHere = self.chkApp.isApplicable(linuxApplicable)        
        windowsApplicable = {'type': 'white',
                           'family': ['win32']}

        if sys.platform.startswith("linux"):
            from ramdisk.linuxTmpfsRamdisk import RamDisk
            self.ramdisk = RamDisk(size, mountpoint, logger, **kwargs)
        elif sys.platform.startswith("darwin"):
            from ramdisk.macRamdisk import RamDisk
            self.ramdisk = RamDisk(size, mountpoint, logger, **kwargs)
        elif sys.platform.startswith("win32"):
            # if on the windows platform, the kernel version and os version is the same
            # so the following platform.version() call works.  If on other systems, it 
            # returns the kernel version information and this parsing method with throw
            # an exception.
            winverMajor = platform.win32_ver()[0]
            if winverMajor <= 10:
                from ramdisk.winImDiskRamdisk import RamDisk, unmount, getMountDisks, getMountData
            else:
                from ramdisk.winAIMtkRamdisk import RamDisk, unmount, getMountDisks, getMountData
            self.ramdisk = RamDisk(size, mountpoint, logger, **kwargs)
        else:
            raise NotValidForThisOS("Ramdisk not available here...")

    ###########################################################################

    def getNlogData(self):
        """
        Logs and returns the mount data from the OS specific ramdisk
        """
        
        return self.ramdisk.getNlogData()
    
    ###########################################################################

    def getNprintData(self):
        """
        Prints and returns the mount data from the OS specific ramdisk
        """
        return self.ramdisk.getNprintData()
    
    ###########################################################################

    def getRamdisk(self):
        """
        Return the instance of the OS specific ramdisk.
        """
        return self.ramdisk
    
    ###########################################################################

    def getMountedDisks(self):
        """
        should return the a dictionary with {device: diskName, ...} that contains
        every mounted disk
        """

        mountedDisks = {}
        try:
            mountedDisks = self.ramdisk.getMountDisks()
        except:
            pass
        return mountedDisks

    ###########################################################################

    def unionOver(self, *args, **kwargs):
        """
        If supported, will create a unionfs or similar construction specific to the OS.
        """
        success = False
        success = self.ramdisk.unionOver(*args, **kwargs)
        return success

    ###########################################################################

    def umount(self, *args, **kwargs):
        """
        Unmount the ramdisk with the passed in arguments, which are specific to the OS.
        """
        success = False
        success = self.ramdisk.umount(*args, **kwargs)
        return success
    
    ###########################################################################

    def getVersion(self):
        """
        Return the version of the instance of the concrete OS specific ramdisk. 
        """
        return self.ramdisk.getVersion()

    ###########################################################################

    def getMountedData(self, device):
        """
        Method to return the OS specific concrete instance, mounted disk information.
        """
        return self.ramdisk.getMountData()

    ###########################################################################

    def getDevice(self):
        """
        Getter for the device name the ramdisk is using

        Must be over-ridden to provide OS/Method specific functionality
        """
        return self.ramdisk.getDevice()

    ###########################################################################

    def getMountPoint(self):
        """
        Getter for the mount point name the ramdisk is using

        Must be over-ridden to provide OS/Method specific functionality        
        """
        return self.ramdisk.getMountPoint()

    ###########################################################################

    def setDevice(self, device=None):
        """
        Setter for the device so it can be ejected.

        Must be over-ridden to provide OS/Method specific functionality
        """
        self.ramdisk.setDevice(device)


def eject(device, logger=False):
    """
    Eject/unmount the passed in instance of a ramdisk.
    """
    unmount(device, logger)

def getMountedDisks(device=""):
    """
    Get a data structure containing a list of the mounted disks, 
    and return the data.
    """
    print("Entered getMountedDisks...")
    data = getMountDisks()
    print("Exiting getMountedDisks...")
    return data

def getMountedData(device=""):
    """
    Get the data that defines a current ramdisk with the passed 
    in device information
    """
    print("Entered getMountedData...")
    data = getMountData(device)
    print("Exiting getMountedData...")
    return data

'''
if __name__=="__main__":

    app = QApplication(sys.argv)
    """
    # Set up event logger
    init_event_logger(
        os.path.join(get_current_directory(), "event.log"),
        "%(asctime)s - %(levelname)s - %(message)s",
        stdout=True,
        debug=True if "--debug" in sys.argv else False,
    )
    """
    print("started app...")
    window = _CreateRamdisk()
    print("initiated window")
    window.show()
    print("showing window...")
    window.raise_()
    print("raising_ window")
    sys.exit(app.exec())
else:
    mntpnt = "foobar"

    logger = CyLogger()
    logger.initializeLogs()

    ramdisk = RamDisk("512", "foobar", logger)
    ramdisk.getNlogData()
    ramdisk.getNprintData()

'''
