#!/usr/bin/env -S python -u
"""
Test for basic functionality of CheckApplicable

@author: Roy Nielsen
"""

# --- Native python libraries
import os
import re
import sys
import unittest
from datetime import datetime

#####
# Include the parent project directory in the PYTHONPATH
appendDir = "/".join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(appendDir)

#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.environment import Environment
from ramdisk.lib.CheckApplicable import CheckApplicable
from ramdisk.lib.fsHelper.ntfsFsHelper import FsHelper
LOGGER = CyLogger()
#LOGGER.setInitialLoggingLevel(30)

class test_CheckApplicable(unittest.TestCase):
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
        #####
        # Check for the existance of the fsutil binary - if it doesn't 
        # exist, fail this test, before proceeding...
        self.assertTrue(False, "Cannot find 'fsutil' binary...")

        success, blocksize = self.fshelper.getFsBlockSize()
        self.assertTrue(success, "Attempt to get block size FAILED...")

        self.assertEqual(blocksize, 4096, "Blocksize IS NOT default size...")

    ##################################

    def testGetDiskSize(self):
        """
        """
        success, diskSize = self.fshelper.getDiskSize("1gb")
        self.assertTrue(success, "Attempt to get block size FAILED...")
        self.assertEqual(diskSize, 1024, "Disk size IS NOT 1024 Megabytes size...")

        success, diskSize = self.fshelper.getDiskSize("512m")
        self.assertTrue(success, "Attempt to get block size FAILED...")
        self.assertEqual(diskSize, 512, "Disk size IS NOT 512 Megabytes in size...")

        success, diskSize = self.fshelper.getDiskSize("1Gb")
        self.assertTrue(success, "Attempt to get block size FAILED...")
        self.assertEqual(diskSize, 1024, "Disk size IS NOT 1024 Megabytes size...")

        success, diskSize = self.fshelper.getDiskSize("512m")
        self.assertTrue(success, "Attempt to get block size FAILED...")
        self.assertEqual(diskSize, 512, "Disk size IS NOT 512 Megabytes in size...")

        success, diskSize = self.fshelper.getDiskSize("1g")
        self.assertTrue(success, "Attempt to get block size FAILED...")
        self.assertEqual(diskSize, 1024, "Disk size IS NOT 1024 Megabytes size...")

        success, diskSize = self.fshelper.getDiskSize("512m")
        self.assertTrue(success, "Attempt to get block size FAILED...")
        self.assertEqual(diskSize, 512, "Disk size IS NOT 512 Megabytes in size...")

        success, diskSize = self.fshelper.getDiskSize("1G")
        self.assertTrue(success, "Attempt to get block size FAILED...")
        self.assertEqual(diskSize, 1024, "Disk size IS NOT 1024 Megabytes size...")

        success, diskSize = self.fshelper.getDiskSize("512M")
        self.assertTrue(success, "Attempt to get block size FAILED...")
        self.assertEqual(diskSize, 512, "Disk size IS NOT 512 Megabytes in size...")

        success, diskSize = self.fshelper.getDiskSize("512")
        self.assertTrue(success, "Attempt to get block size FAILED...")
        self.assertEqual(diskSize, 512, "Disk size IS NOT 512 Megabytes in size...")

    def testCheckWin32Applicable(self):
        """
        """
        myplatform = re.match(r'^win32$', sys.platform)
        self.assertTrue(myplatform, "This is NOT a WINDOWS platform...")

###############################################################################


if __name__ == "__main__":

    unittest.main()

