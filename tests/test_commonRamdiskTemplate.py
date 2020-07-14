#!/usr/bin/python -u
"""
CommonRamdiskTemplate test.

@author: Roy Nielsen
"""
from __future__ import absolute_import
#--- Native python libraries
import re
import os
import sys
import time
import unittest
import tempfile 
from datetime import datetime

sys.path.append("..")

#--- non-native python libraries in this source tree
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp
from commonRamdiskTemplate import RamDiskTemplate, \
                                  BadRamdiskArguments, \
                                  NotValidForThisOS

LOGGER = CyLogger()


class test_commonRamdiskTemplate(unittest.TestCase):
    """
    """
    metaVars = {'setupDone': None, 'testStartTime': 0, 'setupCount': 0}

    def setUp(self):
        """
        Runs once before any tests start
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

    ###########################################################################
    # Method Tests

    ##################################

    def testInit(self):
        """
        Test class init functionality
        """
        rdt = RamDiskTemplate(100, "/tmp/tmptest")
        self.assertTrue(rdt.diskSize == 100, "Sizes don't match...")
        self.assertTrue(rdt.mntPoint == "/tmp/tmptest", "Mountpoints don't match...")
        self.assertTrue(isinstance(rdt.logger, CyLogger), "Logger shouldn't be initialized...")

    ##################################

    def testGetData(self):
        """
        Test class getData method.  This method also tests the other
        getNxxxxxData methods that provide getting functionality.
        """
        rdt = RamDiskTemplate(100, "/tmp/tmptest")
        success, mntpnt, device = rdt.getData()
        self.assertFalse(success, "No success for getData...")
        self.assertTrue(mntpnt == "/tmp/tmptest",
                        "Mountpoints don't match...")
        self.assertTrue(device == str(None),
                        "Device initialized??? : " + str(device))

    ##################################

    def testGetRandomizedMountPoint(self):
        """
        Test class method getRandomizedMountPoint - make sure the
        specified directory has been created.
        """
        rdt = RamDiskTemplate(100)
        randomizedMntPnt = rdt.getRandomizedMountpoint()
        self.assertTrue(randomizedMntPnt, "Didn't succeed in getting randomized mount point...")
        self.assertTrue(os.path.isdir(rdt.mntPoint))

    ##################################

    def testUmount(self):
        """
        Test class method umount
        """
        rdt = RamDiskTemplate()
        self.assertFalse(rdt.umount(),
                    "Umount template method didn't fail...")

    ##################################

    def testUnmount(self):
        """
        Test class method unmount
        """
        rdt = RamDiskTemplate()
        self.assertFalse(rdt.unmount(),
                    "Unmount template method didn't fail...")

    ##################################

    def test_format(self):
        """
        Test class method _format
        """
        rdt = RamDiskTemplate()
        self.assertFalse(rdt._format(),
                        "_format template method should have failed...")

    ####################################

    def testGetDevice(self):
        """
        Test class method getDevice
        """
        rdt = RamDiskTemplate()
        self.assertTrue(rdt.getDevice() == rdt.myRamdiskDev,
                        "getDevice template method should have failed")

    ####################################

    def testGetMountPoint(self):
        """
        Test class method getMountPoint
        """
        rdt = RamDiskTemplate(100, "/tmp/testmnt")
        self.assertTrue(rdt.getMountPoint() == "/tmp/testmnt",
                        "getMountPoint template method should have failed...")


###############################################################################
##### Functional Tests

    ##################################


###############################################################################
##### unittest Tear down
    @classmethod
    def tearDownClass(self):
        """
        Final cleanup actions...
        """
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
            # time.sleep(5)
            pass

###############################################################################


if __name__ == "__main__":
    LOGGER.setInitialLoggingLevel(10)
    LOGGER.initializeLogs()
    unittest.main()
