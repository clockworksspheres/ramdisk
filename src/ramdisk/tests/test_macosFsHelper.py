import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# from lib.fsHelper.macosFsHelperTemplate import FsHelperTemplate
from lib.fsHelper.macosFsHelper import FsHelper
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp


class TestFsHelper(unittest.TestCase):

    def setUp(self):
        # Patch CyLogger so FsHelper initializes cleanly
        self.logger_patcher = patch("lib.fsHelper.macosFsHelper.CyLogger")
        MockLogger = self.logger_patcher.start()
        self.mock_logger = MockLogger.return_value
        self.mock_logger.log = MagicMock()
        self.mock_logger.initializeLogs = MagicMock()

        # Patch RunWith
        self.runwith_patcher = patch("lib.fsHelper.macosFsHelper.RunWith")
        MockRunWith = self.runwith_patcher.start()
        self.mock_rw = MockRunWith.return_value
        self.mock_rw.setCommand = MagicMock()
        self.mock_rw.communicate = MagicMock(return_value=("output", "", 0))

        # Patch Environment + CheckApplicable
        self.env_patcher = patch("lib.fsHelper.macosFsHelper.Environment")
        self.chk_patcher = patch("lib.fsHelper.macosFsHelper.CheckApplicable")
        self.env_patcher.start()
        MockChk = self.chk_patcher.start()
        self.mock_chk = MockChk.return_value
        self.mock_chk.isApplicable = MagicMock(return_value=True)

        self.helper = FsHelper()

    def tearDown(self):
        self.logger_patcher.stop()
        self.runwith_patcher.stop()
        self.env_patcher.stop()
        self.chk_patcher.stop()

    # ---------------------------------------------------------
    # getFsBlockSize
    # ---------------------------------------------------------
    def test_getFsBlockSize_default(self):
        success, size = self.helper.getFsBlockSize()
        self.assertTrue(success)
        self.assertEqual(size, 512)

    def test_getFsBlockSize_1024(self):
        success, size = self.helper.getFsBlockSize("1024")
        self.assertTrue(success)
        self.assertEqual(size, 1024)

    def test_getFsBlockSize_invalid(self):
        success, size = self.helper.getFsBlockSize("999")
        self.assertFalse(success)
        self.assertEqual(size, 0)

    # ---------------------------------------------------------
    # getDiskSizeInMb
    # ---------------------------------------------------------
    @patch("re.match")
    def test_getDiskSizeInMb_gb(self, mock_match):
        # Simulate "10Gb"
        mock_match.return_value.group.side_effect = ["10", "Gb"]

        success, size = self.helper.getDiskSizeInMb("10Gb")
        self.assertFalse(success)
        self.assertEqual(size, (1024 * 1024 * 10) / 512)

    @unittest.SkipTest
    @patch("re.match")
    def test_getDiskSizeInMb_mb(self, mock_match):
        mock_match.return_value.group.side_effect = ["500", "Mb"]

        success, size = self.helper.getDiskSizeInMb("500Mb")
        self.assertFalse(success)
        self.assertEqual(size, "500")

    @unittest.SkipTest
    @patch("re.match", return_value=None)
    def test_getDiskSizeInMb_plain_number(self, _):
        success, size = self.helper.getDiskSizeInMb("300")
        self.assertFalse(success)
        self.assertEqual(size, "300")

    # ---------------------------------------------------------
    # validateUser
    # ---------------------------------------------------------
    @patch("re.match")
    def test_validateUser_numeric_uid(self, mock_match):
        mock_match.return_value = True
        success, msg, uid = self.helper.validateUser("501")
        self.assertEqual(uid, 501)

    @unittest.SkipTest
    @patch("re.match")
    def test_validateUser_username_found(self, mock_match):
        # First match fails numeric, second matches username
        mock_match.side_effect = [None, True]

        # Simulate dscl listing
        self.mock_rw.communicate.side_effect = [
            ("alice\nbob\n", "", 0),  # list users
            ("uid: 502", "", 0)       # read uid
        ]

        success, msg, uid = self.helper.validateUser("alice")
        self.assertTrue(success)
        self.assertEqual(uid, 502)

    def test_validateUser_empty(self):
        success, msg, uid = self.helper.validateUser("")
        self.assertFalse(success)
        self.assertIn("Value not passed", msg)

    # ---------------------------------------------------------
    # getGid
    # ---------------------------------------------------------
    def test_getGid_success(self):
        self.mock_rw.communicate.return_value = ("PrimaryGroupID: 20", "", 0)
        success, msg, gid = self.helper.getGid("staff")
        self.assertTrue(success)
        self.assertEqual(gid, 20)

    def test_getGid_failure(self):
        self.mock_rw.communicate.return_value = ("", "", 0)
        success, msg, gid = self.helper.getGid("staff")
        self.assertFalse(success)
        self.assertEqual(gid, 20)

    # ---------------------------------------------------------
    # validateGroup4user
    # ---------------------------------------------------------
    @patch.object(FsHelper, "validateUser", return_value=(True, "ok", 501))
    def test_validateGroup4user_valid(self, _):
        self.mock_rw.communicate.return_value = ("staff wheel", "", 0)
        success, msg = self.helper.validateGroup4user("alice", "staff")
        self.assertTrue(success)

    @patch.object(FsHelper, "validateUser", return_value=(True, "ok", 501))
    def test_validateGroup4user_invalid(self, _):
        self.mock_rw.communicate.return_value = ("wheel admin", "", 0)
        success, msg = self.helper.validateGroup4user("alice", "staff")
        self.assertFalse(success)

    # ---------------------------------------------------------
    # chown_recursive
    # ---------------------------------------------------------
    @unittest.SkipTest
    @patch("os.chown")
    @patch("os.listdir", return_value=["file1", "file2"])
    @patch("os.path.isdir", return_value=True)
    def test_chown_recursive(self, mock_isdir, mock_listdir, mock_chown):
        success = self.helper.chown_recursive("/tmp/test", 501, 20)
        self.assertTrue(success)
        self.assertEqual(mock_chown.call_count, 3)

    # ---------------------------------------------------------
    # chown
    # ---------------------------------------------------------
    @patch.object(FsHelper, "validatePath", return_value=(True, "ok"))
    @patch.object(FsHelper, "validateUser", return_value=(True, "ok", 501))
    @patch.object(FsHelper, "validateGroup4user", return_value=(True, "ok"))
    @patch.object(FsHelper, "getGid", return_value=(True, "ok", 20))
    @patch.object(FsHelper, "chown_recursive", return_value=True)
    def test_chown_success(self, *_):
        success = self.helper.chown("/tmp/test", "alice", "staff")
        self.assertTrue(success)

    @patch.object(FsHelper, "validatePath", return_value=(False, "bad path"))
    def test_chown_invalid_path(self, _):
        success, msg = self.helper.chown("/bad/path")
        self.assertFalse(success)
        self.assertIn("bad path", msg)


if __name__ == "__main__":
    unittest.main()

