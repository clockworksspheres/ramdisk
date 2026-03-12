#!/usr/bin/env -S python -u

import unittest
import time
import sys
import os
import traceback
import tracemalloc
from datetime import datetime
from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

#--- non-native python libraries in this source tree
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp


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

###############################################################################

if __name__ == "__main__":

    unittest.main()

