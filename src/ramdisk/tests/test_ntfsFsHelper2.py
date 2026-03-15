import sys
import unittest
from unittest.mock import MagicMock, patch

# Only run these tests on Windows
@unittest.skipUnless(sys.platform.lower().startswith("win32"), "Windows-only tests")
class TestFsHelperWindows(unittest.TestCase):

    def setUp(self):
        # Patch CyLogger
        logger_patcher = patch("lib.fsHelper.FsHelper.CyLogger")
        self.addCleanup(logger_patcher.stop)
        MockLogger = logger_patcher.start()
        self.mock_logger = MockLogger.return_value
        self.mock_logger.log = MagicMock()

        # Patch RunWith
        run_patcher = patch("lib.fsHelper.FsHelper.RunWith")
        self.addCleanup(run_patcher.stop)
        MockRunWith = run_patcher.start()
        self.mock_runner = MockRunWith.return_value
        self.mock_runner.setCommand = MagicMock()
        self.mock_runner.communicate = MagicMock()
        self.mock_runner.getNlogReturns = MagicMock()

        # Import after patching
        from lib.fsHelper.FsHelper import FsHelper
        self.FsHelper = FsHelper
        self.helper = FsHelper()

    # ---------------------------------------------------------
    # getFsBlockSize
    # ---------------------------------------------------------
    @patch("re.match")
    def test_getFsBlockSize_success(self, mock_match):
        # Simulate fsutil output
        self.mock_runner.getNlogReturns.return_value = (
            "Bytes Per Cluster : 4096\nMore text\n",
            "",
            0
        )

        mock_match.return_value.group.return_value = "4096"

        success, size = self.helper.getFsBlockSize("c:")

        self.mock_runner.setCommand.assert_called_once()
        self.mock_runner.communicate.assert_called_once()
        self.assertTrue(success)
        self.assertEqual(size, "4096")

    @patch("re.match", return_value=None)
    def test_getFsBlockSize_no_match(self, _):
        self.mock_runner.getNlogReturns.return_value = (
            "Some unrelated output\n",
            "",
            0
        )

        success, size = self.helper.getFsBlockSize("c:")
        self.assertFalse(success)
        self.assertEqual(size, 0)

    # ---------------------------------------------------------
    # getDiskSize
    # ---------------------------------------------------------
    @patch("re.match")
    def test_getDiskSize_with_suffix(self, mock_match):
        # Simulate "10Gb"
        mock_match.return_value.group.return_value = "10G"
        success, size = self.helper.getDiskSize("10Gb")
        self.assertFalse(success)
        self.assertEqual(size, "10G")

    @patch("re.match")
    def test_getDiskSize_plain_number(self, mock_match):
        # First regex fails, second fails, third matches
        mock_match.side_effect = [None, None, MagicMock(group=lambda: "500")]

        success, size = self.helper.getDiskSize("500")
        self.assertFalse(success)
        self.assertEqual(size, "500m")

    def test_getDiskSize_integer(self):
        success, size = self.helper.getDiskSize(1024)
        self.assertTrue(success)
        self.assertEqual(size, 1024)

    def test_getDiskSize_invalid(self):
        with self.assertRaises(AttributeError):
            self.helper.getDiskSize("bad_input!!")


if __name__ == "__main__":
    unittest.main()

