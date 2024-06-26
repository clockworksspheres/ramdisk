#!/usr/bin/env -S python -u
"""
Test the helper exceptions.

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
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.libHelperExceptions import NotValidForThisOS

#####
# Load OS specific Ramdisks
if sys.platform.startswith("darwin"):
    #####
    # For Mac
    from ramdisk.macRamdisk import RamDisk
    from ramdisk.macRamdisk import detach
elif sys.platform.startswith("linux"):
    #####
    # For Linux
    from ramdisk.linuxTmpfsRamdisk import RamDisk
    from ramdisk.linuxTmpfsRamdisk import umount

class test_libHelperExceptions(unittest.TestCase):
    """
    """

    @classmethod
    def setUpClass(self):
        """
        Initializer
        """
        unittest.SkipTest("Tests need to be written...")
        # Start timer in miliseconds
        self.test_start_time = datetime.now()

        self.logger = CyLogger()
        self.logger.initializeLogs()

        self.libcPath = None # initial initialization

    def setUp(self):
        """
        This method runs before each test run.

        @author: Roy Nielsen
        """
        self.libcPath = None # initial initialization
        #####
        # setting up to call ctypes to do a filesystem sync
        if sys.platform.startswith("darwin"):
            #####
            # For Mac
            self.libc = C.CDLL("/usr/lib/libc.dylib")
        elif sys.platform.startswith("linux"):
            #####
            # For Linux
            self.findLinuxLibC()
            self.libc = C.CDLL(self.libcPath)
        else:
            self.libc = self._pass()

###############################################################################
##### Helper Classes

    def setMessageLevel(self, msg_lvl="normal"):
        """
        Set the logging level to what is passed in.
        """
        self.message_level = msg_lvl

    def findLinuxLibC(self):
        """
        Find Linux Libc library...

        @author: Roy Nielsen
        """
        possible_paths = ["/lib/x86_64-linux-gnu/libc.so.6",
                          "/lib/i386-linux-gnu/libc.so.6"]
        for path in possible_paths:

            if os.path.exists(path):
                self.libcPath = path
                break

    def _pass(self):
        """
        Filler if a library didn't load properly
        """
        pass

###############################################################################
##### Method Tests

    ##################################

    def test_init(self):
        """
        """
        pass

    ##################################

###############################################################################
##### Functional Tests

    ##################################

###############################################################################
##### unittest Tear down
    @classmethod
    def tearDownClass(self):
        """
        disconnect ramdisk
        """
        # self.logger = CyLogger()
        #####
        # capture end time
        test_end_time = datetime.now()

        #####
        # Calculate and log how long it took...
        test_time = (test_end_time - self.test_start_time)

        self.logger.log(lp.INFO, self.__module__ + " took " + str(test_time) + \
                        " time to complete...")

###############################################################################


if __name__ == "__main__":

    unittest.main()


