#!/usr/bin/env -S python -u
"""
Test for basic functionality of CheckApplicable

@author: Roy Nielsen
"""

# --- Native python libraries
import os
import re
import sys
import platform
import unittest
from datetime import datetime

#####
# Include the parent project directory in the PYTHONPATH
appendDir = "/".join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(appendDir)

#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.run_commands import RunWith
from ramdisk.lib.environment import Environment
from ramdisk.lib.CheckApplicable import CheckApplicable
from ramdisk.lib.fsHelper.macosFsHelper import FsHelper

LOGGER = CyLogger()
#LOGGER.setInitialLoggingLevel(30)

class test_macosFsHelper(unittest.TestCase):
    """
    """

    ##################################

    @classmethod
    def setUpClass(self):
        """
        """
        #####
        # Set up logging
        self.logger = CyLogger(debug_mode=True)
        self.logger.initializeLogs()
        self.rw = RunWith(self.logger)

        self.enviro = Environment()
        self.ca = CheckApplicable(self.enviro, LOGGER)

        self.fshelper = FsHelper()

        #####
        # Start timer in miliseconds
        self.testStartTime = datetime.now()

    ##################################

    @classmethod
    def tearDownClass(self):
        """
        """
        #####
        # capture end time
        testEndTime = datetime.now()

        #####
        # Calculate and log how long it took...
        test_time = (testEndTime - self.testStartTime)
        # print str(test_time)
        # global LOGGER
        self.logger.log(lp.INFO, self.__module__ + " took " + str(test_time) + " time so far...")

   ##################################

    def testGetFsBlockSize(self):
        """
        """
        success, blockSize = self.fshelper.getFsBlockSize()
        self.assertEqual(blockSize, 512, "Not getting the default 512 block size...")
        self.assertTrue(success, "This getFsBlockSize run was NOT successful!!!")

        success, blockSize = self.fshelper.getFsBlockSize(512)
        self.assertEqual(blockSize, 512, "Not getting the default 512 block size...")
        self.assertTrue(success, "This getFsBlockSize run was NOT successful!!!")

        # success, blockSize = self.fshelper.getFsBlockSize(1024)
        # self.assertEqual(blockSize, 512, "Not getting the default 512 block size...")
        # self.assertTrue(success, "This getFsBlockSize run was NOT successful!!!")

        success, blockSize = self.fshelper.getFsBlockSize(5555)
        self.assertFalse(success, "This getFsBlockSize run was successful - SHOULDN'T BE!!!")

        success, blockSize = self.fshelper.getFsBlockSize("ABC")
        self.assertFalse(success, "This getFsBlockSize run was successful - SHOULDN'T BE!!!")


   ##################################

    def testGetDiskSizeInMb(self):
        """
        """
        pass
        


   ##################################
   ##################################
   ##################################

    def testCheckMacosApplicable(self):
        """
        """
        match = re.match("^darwin$", sys.platform)
        self.assertTrue(match, "This platform is NOT a macos system!!!")

###############################################################################


if __name__ == "__main__":

    unittest.main()

