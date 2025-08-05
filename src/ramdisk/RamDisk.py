"""
Template for the ramdisk classes


"""
import os
import sys
#--- Native python libraries
from tempfile import mkdtemp

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
    from ramdisk.linuxTmpfsRamdisk import RamDisk, unmount, getMountData
elif sys.platform.startswith("darwin"):
    from ramdisk.macRamdisk import RamDisk, unmount, getMountData
elif sys.platform.startswith("win32"):
    from ramdisk.winImDiskRamdisk import RamDisk, unmount, getMountData
else:
    raise NotValidForThisOS("Ramdisk not available here...")


class RamDisk(RamDiskTemplate):
    """
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
            from ramdisk.winImDiskRamdisk import RamDisk
            self.ramdisk = RamDisk(size, mountpoint, logger, **kwargs)
        else:
            raise NotValidForThisOS("Ramdisk not available here...")

    ###########################################################################

    def getNlogData(self):
        """
        """
        
        return self.ramdisk.getNlogData()
    
    ###########################################################################

    def getNprintData(self):
        """
        """
        return self.ramdisk.getNprintData()
    
    ###########################################################################

    def getRamdisk(self):
        """
        """
        return self.ramdisk
    
    ###########################################################################

    def unionOver(self, *args, **kwargs):
        """
        """
        success = False
        success = self.ramdisk.unionOver(*args, **kwargs)
        return success

    ###########################################################################

    def umount(self, *args, **kwargs):
        """
        """
        success = False
        success = self.ramdisk.umount(*args, **kwargs)
        return success
    
    ###########################################################################

    def getVersion(self):
        """
        """
        return self.ramdisk.getVersion()

    ###########################################################################

    def getMountData(self, device):
        """
        Method to return mounted disk information
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
    unmount(device, logger)

def getMountedData(device):
    data = getMountData(device)
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
