#!/usr/bin/python
"""
Test for basic functionality of CheckApplicable

@author: Roy Nielsen
"""
from __future__ import absolute_import
# --- Native python libraries

import sys
import unittest
from datetime import datetime

sys.path.append("..")

# --- Non-native python libraries in this source tree
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp
from lib.environment import Environment
from lib.CheckApplicable import CheckApplicable

LOGGER = CyLogger()
#LOGGER.setInitialLoggingLevel(30)

class test_CheckApplicable(unittest.TestCase):
    """
    """
    metaVars = {'setupDone': None, 'testStartTime': 0, 'setupCount': 0}

    ##################################

    def setUp(self):
        """
        This method runs before each test run.

        @author: Roy Nielsen
        """
        self.metaVars['setupCount'] = self.metaVars['setupCount'] + 1

        if self.metaVars['setupDone']:
            return
        #####
        # setUpClass functionality here.
        # self.libc = getLibc()
        #####
        # Start timer in miliseconds
        self.metaVars['testStartTime'] = datetime.now()
        self.metaVars['setupDone'] = True
        self.enviro = Environment()
        self.ca = CheckApplicable(self.enviro, LOGGER)

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

    ##################################

    def tearDown(self):
        """
        Final cleanup actions...
        """
        # libc = getLibc()
        
        self.metaVars['setupCount'] = self.metaVars['setupCount'] - 1

        #####
        # capture end time
        testEndTime = datetime.now()

        #####
        # Calculate and log how long it took...
        test_time = (testEndTime - self.metaVars['testStartTime'])
        # print str(test_time)
        # global LOGGER
        LOGGER.log(lp.INFO, self.__module__ + " took " + str(test_time) + " time so far...")

        if self.metaVars['setupCount'] == 0:
            #####
            # TearDownClass functionality here.
            pass
            # time.sleep(5)

###############################################################################


if __name__ == "__main__":
    #LOGGER.setInitialLoggingLevel(10)
    LOGGER.initializeLogs()
    unittest.main()

