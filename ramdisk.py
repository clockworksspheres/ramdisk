"""
Template for the ramdisk classes

@author: Roy Nielsen
"""
#--- Native python libraries
from tempfile import mkdtemp

#--- non-native python libraries in this source tree
from lib.loggers import LogPriority as lp
from lib.loggers import CyLogger
from lib.environment import Environment
from lib.CheckApplicable import CheckApplicable
from commonRamdiskTemplate import RamDiskTemplate, BadRamdiskArguments, NotValidForThisOS

###############################################################################

class RamDisk(object):
    """
    """
    def __init__(self, size=0, mountpoint=False, logger=False, environ=False):
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

    ###########################################################################

    def createRamdisk(self, *args, **kwargs):
        """
        """
        #####
        # Check applicability to the current OS
        macApplicable = {'type': 'white',
                         'family': ['darwin'],
                         'os': {'Mac OS X': ['10.8', '+']}}
        macApplicableHere = self.chkApp.isApplicable(macApplicable)

        linuxApplicable = {'type': 'white',
                           'family': ['linux']}
        linuxApplicableHere = self.chkApp.isApplicable(linuxApplicable)        

        if linuxApplicableHere:
            from linuxTmpfsRamdisk import RamDisk
            self.ramdisk = RamDisk(*args, **kwargs)
        elif macApplicableHere:
            from macRamdisk import RamDisk
            self.ramdisk = RamDisk(*args, **kwargs)
        else:
            raise NotValidForThisOS("Ramdisk not available here...")

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
