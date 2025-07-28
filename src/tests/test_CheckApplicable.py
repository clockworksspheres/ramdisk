#!/usr/bin/env -S python -u
"""
Test for basic functionality of CheckApplicable


"""

# --- Native python libraries
import os
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
from ramdisk.lib.run_commands import RunWith
from ramdisk.lib.environment import Environment
from ramdisk.lib.CheckApplicable import CheckApplicable

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
        self.rw = RunWith(self.logger)

        self.enviro = Environment()
        self.ca = CheckApplicable(self.enviro, LOGGER)

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

    def testCheckRedHatApplicable(self):
        """
        """
        self.ca.setOsFamily

    ##################################

    def testCheckLinuxApplicable(self):
        """
        """

    ##################################

    def testCheckDebianApplicable(self):
        """
        """

    ##################################

    def testCheckUbuntuApplicable(self):
        """
        """

    ##################################

    def testCheckCentOS6Applicable(self):
        """
        """

    ##################################

    def testCheckCentOS7Applicable(self):
        """
        """

    ##################################

    def testCheckMacOS1011Applicable(self):
        """
        """

    ##################################
    def testCheckMacOS1011to12Applicable(self):
        """
        """

    ##################################
    def testCheckMacOS1011to13Applicable(self):
        """
        """

###############################################################################


if __name__ == "__main__":

    unittest.main()

