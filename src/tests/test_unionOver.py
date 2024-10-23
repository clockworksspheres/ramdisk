#!/usr/bin/env -S python -u
# ! /usr/bin/python -u
"""
Test unionfs functionality. 

as of 3/15/2016, only the Mac OS X platform is supported.

@author: Roy Nielsen
"""

#--- Native python libraries
import re
import os
import sys
import time
import unittest
import tempfile
import ctypes as C
from datetime import datetime

#####
# Include the parent project directory in the PYTHONPATH
appendDir = "/".join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(appendDir)

#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.libHelperExceptions import NotValidForThisOS

#####
# Load OS specific Ramdisks
if sys.platform.startswith("darwin"):
    #####
    # For Mac
    from ramdisk.macRamdisk import RamDisk
    from ramdisk.macRamdisk import detach
elif sys.platform.startswith("linux"):
    #####
    # For Linux
    from ramdisk.linuxTmpfsRamdisk import RamDisk
    from ramdisk.linuxTmpfsRamdisk import umount


class test_unionOver(unittest.TestCase):
    """
    Test unionfs functionality of ramdisks

    @author: Roy Nielsen
    """

    @classmethod
    def setUpClass(self):
        """
        Initializer
        """
        raise unittest.SkipTest("Needs appropriate tests written")

        #####
        # If we don't have a supported platform, skip this test.
        if not sys.platform.startswith("darwin"):
            raise unittest.SkipTest("This is not valid on this OS")
        #libc = self.getLibc()
     
    ##################################

    def setUp(self):
        """
        This method runs before each test case.

        @author: Roy Nielsen
        """
        pass

 
###############################################################################
##### Method Tests

    ##################################

    def test_unionOverFirstTest(self):
        """
        """
        pass

    ##################################

    def test_unionOverSecondTest(self):
        """
        """
        pass

###############################################################################
##### unittest Tear down
    @classmethod
    def tearDownClassInstanceSpecifics(self):
        """
        disconnect ramdisk
        """
        pass

###############################################################################

if __name__ == "__main__":

    unittest.main()

