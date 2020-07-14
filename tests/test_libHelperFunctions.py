#!/usr/bin/python
'''
Test for testing the libHelperFunctions library.
'''
import sys

sys.path.append("../")

import unittest
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


