#!/usr/bin/env -S python -u
"""
Test for basic functionality of CheckApplicable


"""

# --- Native python libraries
import os
import re
import sys
import platform
import unittest
from datetime import datetime
'''
if not sys.platform.startswith('darwin'):
    raise unittest.SkipTest("Not valid for this patform: " + sys.platform)
'''
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
        if not sys.platform.startswith('darwin'):
            raise unittest.SkipTest("Not valid for this patform: " + sys.platform)

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

    def testGetGid(self):
        """
        """
        success, message, gid = self.fshelper.getGid("staff")

        self.assertTrue(success, "Failed attempting to get group id.")
        self.assertEqual(gid, 20, "Reported GID doesn't match staff.")

    ##################################

    def testValidateGroup4user(self):
        """
        """
        success, message = self.fshelper.validateGroup4user("root", "wheel")
        # print("...Success: " + str(success) + " " + message)
        self.assertTrue(success, "Failed attempting to get group id.")



    ##################################

    def testValidateUser(self):
        """
        """
        success, message, uid = self.fshelper.validateUser("root")
        #self.logger.log(lp.DEBUG, "success: " + str(success))
        #self.logger.log(lp.DEBUG, "message: " + str(message))
        #self.logger.log(lp.DEBUG, "uid: " + str(uid))
        self.assertTrue(success, "Failed attempting to validate a user.")
        self.assertEqual(uid, 0, "User not matching UID...")

    ##################################

    def testValidataPath(self):
        """
        """
        success, message = self.fshelper.validatePath("/private/etc")
        #self.logger.log(lp.DEBUG, "success: " + str(success))
        #self.logger.log(lp.DEBUG, "message: " + str(message))
        #self.logger.log(lp.DEBUG, "uid: " + str(uid))
        self.assertTrue(success, "Failed attempting to validate path.")
        success, message = self.fshelper.validatePath("/Users/root")
        self.assertFalse(success, "Validated bad path attempting to validate path: " + message)

    ##################################

    def testChownRecursive(self):
        """
        """
        pass
        
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

