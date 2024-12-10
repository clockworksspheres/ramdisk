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

if __name__=="__main__":
    sys.path.append("..")

#--- non-native python libraries in this source tree
from tests.genericRamdiskTest import GenericRamdiskTest
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


class test_macRamdisk(GenericRamdiskTest):
    """
    """
    @classmethod
    def setUpClass(self):
        """
        Initializer
        """
        #####
        # If we don't have a supported platform, skip this test.
        if not sys.platform.startswith("darwin"):
            raise unittest.SkipTest("This is not valid on this OS")

###############################################################################
##### unittest Tear down
    @classmethod
    def tearDownClass(self):
        """
        """
        # self.tearDownInstanceSpecifics()
        try:
            self.my_ramdisk.umount()
            self.logger.log(lp.INFO, r"Successfully detached disk: " + \
                       str(self.my_ramdisk.mntPoint).strip())
        except Exception:
            message = r"Couldn't detach disk: " + \
                       str(self.my_ramdisk.myRamdiskDev).strip() + \
                       " : mntpnt: " + str(self.my_ramdisk.mntPoint)
            ex_message = message + "\n" + traceback.format_exc()
            raise Exception(ex_message)

        #####
        # capture end time
        test_end_time = datetime.now()

        #####
        # Calculate and log how long it took...
        test_time = (test_end_time - self.test_start_time)

        self.logger.log(lp.INFO, self.__module__ + " took " + str(test_time) + \
                  " time to complete...")


if __name__ == "__main__":
    unittest.main()

