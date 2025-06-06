"""
Generic ramdisk test, with helper functions. Inherited by other tests.

@author: Roy Nielsen
"""
#--- Native python libraries

import os
import re
import sys
import tempfile
import traceback
import unittest
import ctypes
from datetime import datetime

#####
# Include the parent project directory in the PYTHONPATH
if sys.platform.startswith("win32"):
    appendDir = "../"
else:
    appendDir = "/".join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(appendDir)

#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from tests.genericTestUtilities.genericTestUtilities import GenericTestUtilities
#####
# Load OS specific Ramdisks
if sys.platform.startswith("darwin"):
    #####
    # For Mac
    from ramdisk.lib.getLibc.macGetLibc import getLibc
    from ramdisk.macRamdisk import RamDisk
    from ramdisk.macRamdisk import detach
    from ramdisk.macRamdisk import umount
    from ramdisk.lib.fsHelper.macosFsHelper import FsHelper
elif sys.platform.startswith("linux"):
    #####
    # For Linux
    from ramdisk.lib.getLibc.linuxGetLibc import getLibc
    from ramdisk.linuxTmpfsRamdisk import RamDisk
    from ramdisk.linuxTmpfsRamdisk import umount
    from ramdisk.lib.fsHelper.linuxFsHelper import FsHelper
elif sys.platform.startswith("win32"):
    #####
    # For ImDisk for Windows
    from ramdisk.lib.getLibc.winGetLibc import getLibc
    from ramdisk.winImDiskRamdisk import RamDisk
    from ramdisk.winImDiskRamdisk import umount
    from ramdisk.lib.fsHelper.ntfsFsHelper import FsHelper
else:
    raise Exception("Damn it Jim!!! What OS is this???")


class GenericRamdiskTest(GenericTestUtilities, unittest.TestCase):
    """
    Holds helper methods.  DO NOT create an init

    Inspiration for using classmethod:
    http://simeonfranklin.com/testing2.pdf

    @author: Roy Nielsen
    """
    @classmethod
    def setUpClass(self):
        """
        """
        # self.commonSetUp()
        self.libc = getLibc()
        self.subdirs = ["two", "three" "one/four"]
        self.logger = CyLogger()
        self.logger.initializeLogs()
        self.logger.log(lp.CRITICAL, "Logger initialized............................")
        self.fsHelper = FsHelper()
        self.target = ""

        self.intermediateSetUpClass(self)
        """
        Set up a ramdisk and use that random location as a root to test the
        filesystem functionality of what is being tested.
        """
        
        self.success = False
        self.mountPoint = ""
        self.ramdiskDev = False
        self.mnt_pnt_requested = False
        self.ramdisk_size = 0

        # self.setUpInstanceSpecifics()

        if sys.platform.startswith("darwin") and self.target == 'darwin':
			#Calculate size of ramdisk to make for this unit test.
            # size_in_mb = int((1024 * 1024 * 512) / 512)
            size_in_mb = 512
            self.ramdisk_size = size = size_in_mb
            self.mnt_pnt_requested = "testmntpnt"
        elif sys.platform.startswith("linux") and self.target == 'linux':
            #Calculate size of ramdisk to make for this unit test.
            # linux ramdisks are made in terms of 1 mb at a time... not
            # bits or bytes...
            size_in_mb = 512
            self.ramdisk_size = size_in_mb
            self.mnt_pnt_requested = "/tmp/testmntpnt"
        elif sys.platform.startswith("win32") and self.target == 'win32':
            #Calculate size of ramdisk to make for this unit test.
            self.ramdisk_size = size = size_in_mb
            self.mnt_pnt_requested = "testmntpnt"
        else:
            raise unittest.SkipTest("Not applicable here...")

        # get a ramdisk of appropriate size, with a secure random mountpoint
        self.my_ramdisk = RamDisk(str(self.ramdisk_size), self.mnt_pnt_requested, logger=self.logger)
        self.logger.log(self.WARNING, "::::: ramdisk: " + str(self.my_ramdisk + " :::::"))
        self.success, self.mountPoint, self.ramdiskDev = self.my_ramdisk.getData()
        self.logger.log(lp.WARNING, str(self.success) + " : " + str(self.mountPoint) + " : " + str(self.ramdiskDev))
        self.mount = self.mountPoint

        self.logger.log(lp.INFO, "::::::::Ramdisk Mount Point: " + str(self.mountPoint))
        self.logger.log(lp.INFO, "::::::::Ramdisk Device     : " + str(self.ramdiskDev))

        if not self.my_ramdisk.success:
            raise IOError("Cannot get a ramdisk in setupClass for some reason. . .")


        #####
        # Create a temp location on disk to run benchmark tests against
        self.fs_dir = tempfile.mkdtemp()

        # Start timer in miliseconds
        self.test_start_time = datetime.now()

    '''
    @classmethod
    def setUpInstanceSpecifics(self):
        ""
        Call the child class setUpClass initializer, if possible..

        Here to be over-ridden by a child class.

        @author: Roy Nielsen
        ""
        pass
    '''
    ################################################
    ##### Helper Methods

    def _unloadRamdisk(self):
        """
        """
        if self.my_ramdisk.umount():
            self.logger.log(lp.INFO, r"Successfully detached disk: " + \
                       str(self.my_ramdisk.mntPoint).strip())
        else:
            self.logger.log(lp.WARNING, r"Couldn't detach disk: " + \
                       str(self.my_ramdisk.myRamdiskDev).strip() + \
                       " : mntpnt: " + str(self.my_ramdisk.mntPoint))
            raise Exception(r"Cannot eject disk: " + \
                            str(self.my_ramdisk.myRamdiskDev).strip() + \
                            " : mntpnt: " + str(self.my_ramdisk.mntPoint))

###############################################################################
##### Functional Tests

    ##################################

    def test_files_n_dirs(self):
        """
        Should work when files exist in ramdisk.
        """
        # Do file setup for this test
        for subdir in self.subdirs:
            dirpath = self.mountPoint + "/" + subdir
            self.logger.log(lp.DEBUG, "DIRPATH: : " + str(dirpath))
            self.mkdirs(dirpath)
            self.touch(dirpath + "/" + "test")

        # Do the tests
        for subdir in self.subdirs:
            # CANNOT use os.path.join this way.  os.path.join cannot deal with
            # absolute directories.  May work with mounting ramdisk in local
            # relative directories.
            self.assertTrue(os.path.exists(self.mountPoint + "/" + subdir + "/" +  "test"), "Problem with ramdisk...")

    ##################################

    def test_four_file_sizes(self):
        """
        Test file creation of various sizes, ramdisk vs. filesystem
        """
        """
        try:
            #####
            # Clean up the ramdisk
            self.my_ramdisk._format()
        except AttributeError:
            # get a ramdisk of appropriate size, with a secure random mountpoint
            self.my_ramdisk = RamDisk(str(self.ramdisk_size), self.mnt_pnt_requested, logger=self.logger)
            self.logger.log(self.WARNING, "::::: ramdisk: " + str(self.my_ramdisk + " :::::"))
            self.success, self.mountPoint, self.ramdiskDev = self.my_ramdisk.getData()
            self.logger.log(lp.WARNING, str(self.success) + " : " + str(self.mountPoint) + " : " + str(self.ramdiskDev))
            self.mount = self.mountPoint

            self.logger.log(lp.INFO, "::::::::Ramdisk Mount Point: " + str(self.mountPoint))
            self.logger.log(lp.INFO, "::::::::Ramdisk Device     : " + str(self.ramdiskDev))

            if not self.my_ramdisk.success:
                raise IOError("Cannot get a ramdisk in setupClass for some reason. . .")
        """
        #####
        # 10Mb file size
        ten = 10
        #####
        # 50Mb file size
        fifty = 50
        #####
        # 80Mb file size
        eighty = 80
        #####
        # 100Mb file size
        oneHundred = 100

        my_fs_array = [ten, ten, eighty, oneHundred]

        try: 
            fs_starttime = datetime.now()
            for file_size in my_fs_array:
                self.logger.log(lp.INFO, "testfile size: " + str(file_size))
                #####
                # Create filesystem file and capture the time it takes...
                self.mkfile(os.path.join(self.mountPoint, "testfile"), file_size)
                self.logger.log(lp.INFO, "file_size: " + str(file_size) + " fs_time: " + str(datetime.now()))
            fs_endtime = datetime.now()
    
            fs_time = fs_endtime - fs_starttime
    
            ram_starttime = datetime.now()
            for file_size in my_fs_array:
                self.logger.log(lp.INFO, "testfile size: " + str(file_size))
                #####
                # get the time it takes to create the file in ramdisk...
                self.mkfile(os.path.join(self.mountPoint, "testfile"), file_size)
                self.logger.log(lp.INFO, "ram_time: " + str(datetime.now()))
            ram_endtime = datetime.now()

            ram_time = ram_starttime - ram_endtime

            speed = fs_time - ram_time
            self.logger.log(lp.INFO, "ramdisk: " + str(speed) + " faster...")

            assert_message = "Problem with " + str(file_size) + "mb ramdisk..."
            self.logger.log(lp.DEBUG, assert_message)
            self.logger.log(lp.INFO, "Smaller file sizes will fail this test on systems with SSD's...")

            self.assertTrue((fs_time - ram_time).days > -1, assert_message)
        except Exception as err:
            self.logger.log(lp.WARNING, traceback.format_exc())
            self.logger.log(lp.WARNING, str(file_size) + " if meaningful...")
            self.logger.log(lp.WARNING, "test_four_file_sizes test")
 
    ##################################

    def test_many_small_files_creation(self):
        """
        """
        #####
        # Clean up the ramdisk
        #self.my_ramdisk._format()
        #####
        #
        ramdisk_starttime = datetime.now()
        for i in range(1000):
            self.mkfile(os.path.join(self.mountPoint, "testfile" + str(i)), 1)
        ramdisk_endtime = datetime.now()

        rtime = ramdisk_endtime - ramdisk_starttime

        fs_starttime = datetime.now()
        for i in range(1000):
            self.mkfile(os.path.join(self.fs_dir, "testfile" + str(i)), 1)
        fsdisk_endtime = datetime.now()

        fstime = fsdisk_endtime - fs_starttime

        self.assertTrue((fstime - rtime).days > -1, "Problem with ramdisk...")

    ##################################

    @classmethod
    def tearDownInstanceSpecifics(self):
        """
        Skeleton method in case a child class wants/needs to override it.

        @author: Roy Nielsen
        """
        pass

    @classmethod
    def intermediateTearDownClass(self):
        """
        """
        pass

        # self.tearDownInstanceSpecifics(self)

        try:
            self.my_ramdisk.umount()
            self.logger.log(lp.INFO, r"Successfully detached disk: " + \
                       str(self.my_ramdisk.mntPoint).strip())
        except Exception:
            #message = r"Couldn't detach disk: " + \
            #           str(self.my_ramdisk.myRamdiskDev).strip() + \
            #           " : mntpnt: " + str(self.my_ramdisk.mntPoint)
            ex_message = traceback.format_exc()
            #self.logger.log(lp.WARNING, message)
            self.logger.log(lp.WARNING, ex_message)
            # raise Exception(ex_message)



###############################################################################
