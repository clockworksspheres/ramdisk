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
import unittest 
from datetime import datetime

if __name__=="__main__":
    sys.path.append("..")

#--- non-native python libraries in this source tree
from tests.genericRamdiskTest import GenericRamdiskTest
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.libHelperExceptions import NotValidForThisOS

if sys.platform.startswith("darwin"):
    #####
    # For Mac
    from ramdisk.lib.getLibc.macGetLibc import getLibc
    from tests.genericTestUtilities import GenericTestUtilities
    from ramdisk.macRamdisk import RamDisk
    from ramdisk.macRamdisk import detach
    from ramdisk.macRamdisk import umount
    from ramdisk.lib.fsHelper.macosFsHelper import FsHelper
else:
    raise unittest.SkipTest("Not Valid For This OS")


class test_macRamdisk(GenericRamdiskTest):
    """
    """
    @classmethod
    def setUpInstanceSpecifics(self):
        """
        Initializer
        """
        #####
        # If we don't have a supported platform, skip this test.
        if not sys.platform.startswith("darwin"):
            raise unittest.SkipTest("This is not valid on this OS")

        #####
        # capture end time
        self.start_test_time = datetime.now()

        self.logger.log(lp.INFO, self.__module__ + " start_test_time: " + str(self.start_test_time))

###############################################################################
##### unittest Tear down
    @classmethod
    def tearDownInstanceSpecifics(self):
        """
        """
        #####
        # capture end time
        test_end_time = datetime.now()

        #####
        # Calculate and log how long it took...
        test_time = (test_end_time - self.start_test_time)

        self.logger.log(lp.INFO, self.__module__ + " took " + str(test_time) + " time to complete...")


if __name__ == "__main__":
    unittest.main()

