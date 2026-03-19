import sys
import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from lib import libHelperFunctions as helpers
from lib.libHelperExceptions import UnsupportedOSError


# ---------------------------------------------------------
# Test Suite for libHelperFunctions
# ---------------------------------------------------------
class TestLibHelperFunctions(unittest.TestCase):

    # ---------------------------------------------------------
    # get_console_user
    # ---------------------------------------------------------
    @patch("lib.libHelperFunctions.sys.platform", "darwin")
    @patch("lib.libHelperFunctions.Popen")
    def test_get_console_user_valid_mac(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = [b"fakeuser"]
        mock_popen.return_value = process

        user = helpers.get_console_user()
        self.assertEqual(user, "fakeuser")

    @patch("lib.libHelperFunctions.sys.platform", "linux")
    @patch("lib.libHelperFunctions.Popen")
    def test_get_console_user_valid_linux(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = [b"linuxuser"]
        mock_popen.return_value = process

        user = helpers.get_console_user()
        self.assertEqual(user, "linuxuser")

    @patch("lib.libHelperFunctions.sys.platform", "linux")
    @patch("lib.libHelperFunctions.Popen")
    def test_get_console_user_invalid(self, mock_popen):
        process = MagicMock()
        process.communicate.return_value = [b"bad user!"]
        mock_popen.return_value = process

        user = helpers.get_console_user()
        self.assertFalse(user)

    @patch("lib.libHelperFunctions.sys.platform", "win32")
    def test_get_console_user_unsupported_os(self):
        with self.assertRaises(UnsupportedOSError):
            helpers.get_console_user()

    @patch("lib.libHelperFunctions.sys.platform", "linux")
    @patch("lib.libHelperFunctions.logger")
    @patch("lib.libHelperFunctions.Popen", side_effect=Exception("boom"))
    def test_get_console_user_exception(self, mock_popen, mock_logger):
        with self.assertRaises(Exception):
            helpers.get_console_user()

        # Ensure logging occurred
        mock_logger.log.assert_called()

    # ---------------------------------------------------------
    # touch
    # ---------------------------------------------------------
    @patch("lib.libHelperFunctions.os.utime")
    def test_touch_existing_file(self, mock_utime):
        helpers.touch("file.txt")
        mock_utime.assert_called_once()

    @patch("lib.libHelperFunctions.open", new_callable=mock_open)
    @patch("lib.libHelperFunctions.os.utime", side_effect=Exception("fail"))
    def test_touch_creates_file(self, mock_utime, mock_file):
        helpers.touch("file.txt")
        mock_file.assert_called_once_with("file.txt", "a")

    # ---------------------------------------------------------
    # getecho
    # ---------------------------------------------------------
    @unittest.skipIf(sys.platform.lower().startswith("win"), "doesn't work on Windows")
    @patch("lib.libHelperFunctions.termios.tcgetattr")
    def test_getecho_true(self, mock_tc):
        mock_tc.return_value = [None, None, None, helpers.termios.ECHO]
        self.assertTrue(helpers.getecho(0))

    @unittest.skipIf(sys.platform.lower().startswith("win"), "doesn't work on Windows")
    @patch("lib.libHelperFunctions.termios.tcgetattr")
    def test_getecho_false(self, mock_tc):
        mock_tc.return_value = [None, None, None, 0]
        self.assertFalse(helpers.getecho(0))

    # ---------------------------------------------------------
    # waitnoecho
    # ---------------------------------------------------------
    @patch("lib.libHelperFunctions.getecho")
    def test_waitnoecho_immediate(self, mock_getecho):
        mock_getecho.return_value = False
        self.assertTrue(helpers.waitnoecho(0, timeout=1))

    @patch("lib.libHelperFunctions.getecho", side_effect=[True, True, False])
    def test_waitnoecho_eventually(self, mock_getecho):
        self.assertTrue(helpers.waitnoecho(0, timeout=1))

    # ---------------------------------------------------------
    # isSaneFilePath
    # ---------------------------------------------------------
    def test_isSaneFilePath_valid(self):
        self.assertTrue(helpers.isSaneFilePath("/tmp/test-file_01.txt"))

    def test_isSaneFilePath_invalid(self):
        self.assertFalse(helpers.isSaneFilePath("bad path!"))


if __name__ == "__main__":
    unittest.main()

