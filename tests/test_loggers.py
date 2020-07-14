#!/usr/bin/python
"""
Testing logging functionality via CyLogger

@author: Roy Nielsen
"""
# --- Native python libraries
import sys
import unittest

from datetime import datetime

sys.path.append("..")

# --- Non-native python libraries in this source tree
from lib.loggers import CyLogger
from lib.loggers import LogPriority

class test_CyLogger(unittest.TestCase):
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
        self.metaVars['setupCount'] = self.metaVars['setupCount'] + 1
        self.priority = LogPriority

        if self.metaVars['setupDone']:
            return
        #####
        # setUpClass functionality here.
        self.metaVars['setupDone'] = True
        self.logger.initializeLogs()


    def testLogCritical(self):
        try:
            self.logger.log(self.priority.CRITICAL, "Critical level message")
        except:
            self.fail("Failed to write CRITICAL to log file")

    def testLogError(self):
        try:
            self.logger.log(self.priority.ERROR, "Error level message")
        except:
            self.fail("Failed to write ERROR to log file")

    def testLogWarning(self):
        try:
            self.logger.log(self.priority.WARNING, "Warning level message")
        except:
            self.fail("Failed to write WARNING to log file")

    def testLogInfo(self):
        try:
            self.logger.log(self.priority.INFO, "Info level message")
        except:
            self.fail("Failed to write INFO to log file")

    def testLogDebug(self):
        try:
            self.logger.log(self.priority.DEBUG, "Debug level message")
        except:
            self.fail("Failed to write DEBUG to log file")


if __name__ == "__main__":
    unittest.main()
