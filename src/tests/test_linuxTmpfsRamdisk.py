#!/usr/bin/env -S python -u
# ! /usr/bin/python -u
"""
Test of the Linux tmpfs ramdisk

@author: Roy Nielsen
"""

#--- Native python libraries
import re
import os
import sys
import time
import unittest
import tempfile
import ctypes as C
from datetime import datetime

#####
# Include the parent project directory in the PYTHONPATH
appendDir = "/".join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(appendDir)

#--- non-native python libraries in this source tree
from tests.genericTestUtilities.genericRamdiskTest import GenericRamdiskTest
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.libHelperExceptions import NotValidForThisOS

if sys.platform.startswith("linux"):
    #####
    # For Linux
    from ramdisk.linuxTmpfsRamdisk import RamDisk
    from ramdisk.linuxTmpfsRamdisk import umount
else:
    raise unittest.SkipTest("Not Valid For This OS")


class test_linuxTmpfsRamdisk(GenericRamdiskTest):
    """
    Test for the Linux tmpfs Ramdisk interface

    @author: Roy Nielsen
    """

    @classmethod
    def setUpInstanceSpecifics(self):
        """
        Initializer
        """
        #####
        # If we don't have a supported platform, skip this test.
        if not sys.platform.startswith("linux"):
            raise unittest.SkipTest("This is not valid on this OS")

        # Start timer in miliseconds
        self.test_start_time = datetime.now()

        self.logger = CyLogger()

        #####
        # Initialize the helper class
        self.initializeHelper = False

    @classmethod
    def setUp(self):
        """
        This method runs before each test run.

        @author: Roy Nielsen
        """
        #####
        # If we don't have a supported platform, skip this test.
        try:
        
            if not sys.platform.startswith("linux"):
                raise NotValidForThisOS("Test not valid for this OS...")
        except NotValidForThisOS as err: 
            self.skiptest("This is not valid on this OS")

    @classmethod
    def setUpClass(self):
        """
        This method runs before each test run.

        @author: Roy Nielsen
        """
        #####
        # If we don't have a supported platform, skip this test.
        if not sys.platform.startswith("linux"):
            raise unittest.SkipTest("This is not valid on this OS")


###############################################################################
##### Helper Classes

    def format_ramdisk(self):
        """
        Format Ramdisk
        """
        self.my_ramdisk._format()

###############################################################################
##### Method Tests

    def test_linuxTmpfsRamdiskFirstTest(self):
        """
        """
        pass

    ##################################

    def test_linuxTmpfsRamdiskSecondTest(self):
        """
        """
        pass

    def test_isUserRoot(self):
        '''
        User must be uid 0 to make a ramdisk on Linux
        '''
        if os.geteuid() != 0:
            self.assertRaises(UserMustBeRootError, "If UID is not 0, a UserMustBeRootError must be raised...")

        self.assertTrue(os.geteuid() == 0, "User is not root, cannot cannot create a ramdisk if user is not root.")

###############################################################################

if __name__ == "__main__":

    unittest.main()

