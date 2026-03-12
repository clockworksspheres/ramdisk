#!/usr/bin/env -S python -u
'''
Test for testing the libHelperFunctions library.
'''
import sys
import unittest

from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# import lib.environment as environment

from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp


class test_libHelperFunctions(unittest.TestCase):
    """ 
    """

    @classmethod
    def setUpClass(self):
        """ 
        """
        self.logger = CyLogger(debug_mode=True)
        self.logger.initializeLogs()
        self.logger.log(lp.DEBUG, "Test " + self.__name__ + " initialized...")

    @classmethod
    def tearDownClass(self):
        """ 
        """
        pass

    def test_FoundException(self):
        """ 
        """
        pass

    def test_get_os_vers(self):
        """ 
        """
        pass

    def test_get_os_minor_vers(self):
        """ 
        """
        pass

###############################################################################


if __name__ == "__main__":

    unittest.main()

