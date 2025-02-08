"""
Template for the ramdisk classes

@author: Roy Nielsen
"""
import os
import sys
#--- Native python libraries
from tempfile import mkdtemp

#####
# Include the parent project directory in the PYTHONPATH
# appendDir = "/".join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
# sys.path.append(appendDir)
sys.path.append("../")

#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.environment import Environment
from ramdisk.lib.CheckApplicable import CheckApplicable
from ramdisk.commonRamdiskTemplate import RamDiskTemplate, BadRamdiskArguments, NotValidForThisOS

###############################################################################

class RamDisk(RamDiskTemplate):
    """
    """
    def __init__(self, size=0, mountpoint=False, logger=False, environ=False, **kwargs):
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
        if not environ:
            self.environ = Environment()
        else:
            self.environ = environ
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
            from .linuxTmpfsRamdisk import RamDisk
            self.ramdisk = RamDisk(size, mountpoint, logger)
        elif sys.platform.startswith("darwin"):
            from .macRamdisk import RamDisk
            self.ramdisk = RamDisk(size, mountpoint, logger)
        elif sys.platform.startswith("win32"):
            from .winImDiskRamdisk import RamDisk
            self.ramdisk = RamDisk(*args, **kwargs)
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

    def getDevice(self):
        """
        Getter for the device name the ramdisk is using

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        return self.ramdisk.getDevice()

    ###########################################################################

    def getMountPoint(self):
        """
        Getter for the mount point name the ramdisk is using

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        return self.ramdisk.getMountPoint()

    ###########################################################################

    def setDevice(self, device=None):
        """
        Setter for the device so it can be ejected.

        Must be over-ridden to provide OS/Method specific functionality

        @author: Roy Nielsen
        """
        self.ramdisk.setDevice(device)
