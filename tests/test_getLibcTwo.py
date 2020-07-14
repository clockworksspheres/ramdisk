#!/usr/bin/python
"""
Test for basic functionality of the basic libc
functionality provided by getLibc

@author: Roy Nielsen
"""
from __future__ import absolute_import
# --- Native python libraries

import os
import sys
import copy
import time
import platform
import unittest
import ctypes as C
from datetime import datetime

sys.path.append("..")

# --- Non-native python libraries in this source tree
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp
from lib.getLibc import getLibc

LOGGER = CyLogger()
#LOGGER.setInitialLoggingLevel(30)

class test_getLibcTwo(unittest.TestCase):
    """
    """
    libc = getLibc()

    ##################################

    def test_get_euid(self):
        """
        """
        # libc = getLibc()
        c_euid = self.libc.geteuid()
        py_euid = os.geteuid()
        self.assertEqual(c_euid, py_euid, "Euid's are not equal...")

    ##################################

    def test_uname(self):
        """
        """
        # libc = getLibc()
        class uts_struct(C.Structure):
            _fields_ = [ ('sysname', C.c_char * 65),
                         ('nodename', C.c_char * 65),
                         ('release', C.c_char * 65),
                         ('version', C.c_char * 65),
                         ('machine', C.c_char * 65),
                         ('domain', C.c_char * 65) ]
        tmpStruct = uts_struct()
        self.libc.uname(C.byref(tmpStruct))
        c_system = copy.deepcopy(tmpStruct.sysname.strip())
        py_system = platform.system()
        self.libc.sync()
        self.assertTrue(c_system == py_system, "Systems not the same...")
        # self.libc.free(C.byref(tmpStruct))
        self.libc.sync()
        self.libc.sync()
        
    ##################################

    def test_symlink(self):
        """
        """
        # libc = getLibc()
        pathName = os.path.dirname(sys.argv[0])
        mylink = "testlink"
        linkName = os.path.join(pathName, mylink)
        self.libc.symlink(sys.argv[0], linkName)
        self.libc.sync()
        self.assertTrue(os.path.islink(linkName), "Not a link...")
        self.libc.sync()
        # self.libc.unlink(mylink)
        self.libc.sync()
        self.libc.sync()

###############################################################################


if __name__ == "__main__":
    unittest.main()
