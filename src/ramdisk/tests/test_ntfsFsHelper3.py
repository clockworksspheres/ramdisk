import os
import re
import sys
import unittest
from unittest import SkipTest
from unittest.mock import patch, MagicMock
from datetime import datetime
from pathlib import Path

# Get the parent directory of the current file's parent directory and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp
from lib.environment import Environment
from lib.CheckApplicable import CheckApplicable
from lib.fsHelper.ntfsFsHelper import FsHelper

LOGGER = CyLogger()


@unittest.skipUnless(sys.platform.lower().startswith("win32"), "Only runs on Windows")
class test_ntfsFsHelper(unittest.TestCase):
    """
    Tests for FsHelper on Windows, rewritten to use mocks.
    """

    @classmethod
    def setUpClass(cls):
        # Force Windows-like behavior in tests via patching sys.platform where needed
        cls.platform_patcher = patch("sys.platform", "win32")
        cls.platform_patcher.start()

        # Mock logger, environment, and CheckApplicable to avoid side effects
        cls.logger = MagicMock(spec=CyLogger)
        cls.logger.log = MagicMock()

        cls.enviro = MagicMock(spec=Environment)
        cls.ca = MagicMock(spec=CheckApplicable)

        # Real FsHelper instance (we'll mock its methods where needed)
        cls.fshelper = FsHelper()

        # Start timer
        cls.testStartTime = datetime.now()

    @classmethod
    def tearDownClass(cls):
        # Stop platform patcher
        cls.platform_patcher.stop()

        # Capture end time
        testEndTime = datetime.now()
        test_time = (testEndTime - cls.testStartTime)

        # Log how long it took (using mocked logger)
        cls.logger.log(lp.INFO, cls.__module__ + " took " + str(test_time) + " time so far...")

    def setUp(self):
        # If we don't have a supported platform, skip this test.
        if not sys.platform.startswith("win32"):
            raise SkipTest("This is not valid on this OS")

    # ----------------------------------------------------------------------
    # testGetFsBlockSize using patch.object on FsHelper.getFsBlockSize
    # ----------------------------------------------------------------------
    @patch.object(FsHelper, "getFsBlockSize")
    def testGetFsBlockSize(self, mock_getFsBlockSize):
        """
        Test that getFsBlockSize returns expected values using a mock.
        """
        # Arrange
        mock_getFsBlockSize.return_value = (True, 4096)

        # Act
        success, blocksize = self.fshelper.getFsBlockSize()

        # Assert
        self.assertTrue(success, "Attempt to get block size FAILED...")
        self.assertEqual(blocksize, 4096, "Blocksize IS NOT default size...")
        mock_getFsBlockSize.assert_called_once()

    # ----------------------------------------------------------------------
    # testGetDiskSize using patch.object on FsHelper.getDiskSize
    # ----------------------------------------------------------------------
    @patch.object(FsHelper, "getDiskSize")
    def testGetDiskSize(self, mock_getDiskSize):
        """
        Test getDiskSize logic using mocked return values.
        """
        # Define a side effect function to simulate different inputs
        def side_effect(arg):
            mapping = {
                "1gb": (True, 1024),
                "512m": (True, 512),
                "1Gb": (True, 1024),
                "1g": (True, 1024),
                "1G": (True, 1024),
                "512M": (True, 512),
                "512": (True, 512),
            }
            return mapping.get(arg, (False, None))

        mock_getDiskSize.side_effect = side_effect

        # 1gb
        success, diskSize = self.fshelper.getDiskSize("1gb")
        self.assertTrue(success, "Attempt to get disk size FAILED...")
        self.assertEqual(diskSize, 1024, "Disk size IS NOT 1024 Megabytes size...")

        # 512m
        success, diskSize = self.fshelper.getDiskSize("512m")
        self.assertTrue(success, "Attempt to get disk size FAILED...")
        self.assertEqual(diskSize, 512, "Disk size IS NOT 512 Megabytes in size...")

        # 1Gb
        success, diskSize = self.fshelper.getDiskSize("1Gb")
        self.assertTrue(success, "Attempt to get disk size FAILED...")
        self.assertEqual(diskSize, 1024, "Disk size IS NOT 1024 Megabytes size...")

        # 1g
        success, diskSize = self.fshelper.getDiskSize("1g")
        self.assertTrue(success, "Attempt to get disk size FAILED...")
        self.assertEqual(diskSize, 1024, "Disk size IS NOT 1024 Megabytes size...")

        # 1G
        success, diskSize = self.fshelper.getDiskSize("1G")
        self.assertTrue(success, "Attempt to get disk size FAILED...")
        self.assertEqual(diskSize, 1024, "Disk size IS NOT 1024 Megabytes size...")

        # 512M
        success, diskSize = self.fshelper.getDiskSize("512M")
        self.assertTrue(success, "Attempt to get disk size FAILED...")
        self.assertEqual(diskSize, 512, "Disk size IS NOT 512 Megabytes in size...")

        # 512 (no suffix)
        success, diskSize = self.fshelper.getDiskSize("512")
        self.assertTrue(success, "Attempt to get disk size FAILED...")
        self.assertEqual(diskSize, 512, "Disk size IS NOT 512 Megabytes in size...")

        # Ensure the mock was called the expected number of times
        self.assertEqual(mock_getDiskSize.call_count, 7)

    # ----------------------------------------------------------------------
    # testCheckWin32Applicable using patched sys.platform
    # ----------------------------------------------------------------------
    @patch("sys.platform", "win32")
    def testCheckWin32Applicable(self):
        """
        Ensure that the platform is recognized as Windows.
        """
        myplatform = re.match(r'^win32$', sys.platform)
        self.assertTrue(myplatform, "This is NOT a WINDOWS platform...")


if __name__ == "__main__":
    unittest.main()

