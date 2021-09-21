
import unittest
import time
import sys
import os
import traceback
import tracemalloc
from datetime import datetime

#####
# Include the parent project directory in the PYTHONPATH
appendDir = "/".join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(appendDir)

#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp


class test_libMacOSHelperFunctions(unittest.TestCase):
    """

    """

    @classmethod
    def setUpClass(self):
        """
        """
        #####
        # Set up logging
        self.logger = CyLogger(debug_mode=True)
        self.logger.initializeLogs()
        self.rw = RunWith(self.logger)
        #####
        # Start timer in miliseconds
        self.test_start_time = datetime.now()

    @classmethod
    def tearDownClass(self):
        """
        """
        pass

