#!/usr/bin/env -S python -u
"""
Test for basic functionality of CheckApplicable


"""

# --- Native python libraries
import os
import sys
import unittest
from datetime import datetime
from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

#--- non-native python libraries in this source tree
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp
from lib.run_commands import RunWith
from lib.environment import Environment
from lib.CheckApplicable import CheckApplicable

LOGGER = CyLogger()
#LOGGER.setInitialLoggingLevel(30)

class test_fsHelper(unittest.TestCase):
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

