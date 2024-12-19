#!/usr/bin/env -S python -u
"""
Testing logging functionality via CyLogger

@author: Roy Nielsen
"""

# --- Native python libraries
import unittest
import time
import sys 
import os
import re
import traceback
import tracemalloc
from datetime import datetime

sys.path.append("../../../..")
#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.config import DEFAULT_LOG_LEVEL
from ramdisk.lib.libHelperExceptions import UnsupportedOSError
from ramdisk.lib.manage_user.manage_user import ManageUser
from ramdisk.lib.manage_user.manage_user_exceptions import UserExistsError, UserCreationUnsuccessfullError


class test_loggers(unittest.TestCase):
    """
    Test for the CyLogger class, based on the STONIX project's test
    for it's logdispatcher.
    """

    metaVars = {'setupDone': None,
                'setupCount': 0}
    logger = CyLogger(level=10)

    def setUp(self):
        """
        Runs once before any tests start
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

        self.mu = ManageUser(self.logger) 

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
        nextUserNumber = self.mu.findUniqueUid()


        if int(nextUserNumber) > 500 and int(nextUserNumber) < 65536:
            nextUserNumberValid = True
        else:
            nextUserNumberValid = False 
        self.assertTrue(nextUserNumberValid, "Next User Number is NOT valid on this system!!!!")

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


