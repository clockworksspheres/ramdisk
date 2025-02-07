#!/usr/bin/env -S python -u
"""

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

sys.path.append("..")

#--- non-native python libraries in this source tree
from tests.genericTestUtilities.genericRamdiskTest import GenericRamdiskTest
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.libHelperExceptions import NotValidForThisOS

if sys.platform.startswith("win32"):
    #####
    # For Linux
    from ramdisk.winImDiskRamdisk import RamDisk
    from ramdisk.winImDiskRamdisk import umount
else:
    raise unittest.SkipTest("Not Valid For This OS")


class test_winImDiskRamdisk(GenericRamdiskTest):
    """
    """

    @classmethod
    def setUp(self):
        """
        """
        #####
        # If we don't have a supported platform, skip this test.
        if not sys.platform.startswith("win32"):
            raise unittest.SkipTest("This is not valid on this OS")

    @classmethod
    def setUpClass(self):
        """
        """
        #####
        # If we don't have a supported platform, skip this test.
        if not sys.platform.startswith("win32"):
            raise unittest.SkipTest("This is not valid on this OS")
     
    @classmethod
    def setUpInstanceSpecifics(self):
        """
        Initializer
        """
        #####
        # If we don't have a supported platform, skip this test.
        if not sys.platform.startswith("win32"):
            raise unittest.SkipTest("This is not valid on this OS")

###############################################################################
##### unittest Tear down
    @classmethod
    def tearDownInstanceSpecifics(self):
        """
        disconnect ramdisk
        """
        pass


if __name__ == "__main__":
    unittest.main()

