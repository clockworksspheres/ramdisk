import unittest
from unittest.mock import MagicMock, patch
import os
import re
import sys
from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from lib.fsHelper.FsHelperTemplate import FsHelperTemplate
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp


class TestFsHelperTemplate(unittest.TestCase):

    def setUp(self):
        # Mock logger
        self.logger = MagicMock(spec=CyLogger)
        self.logger.log = MagicMock()
        self.logger.initializeLogs = MagicMock()

        self.helper = FsHelperTemplate(logger=self.logger)

    # -----------------------------
    # Initialization
    # -----------------------------
    def test_initialization_calls_initializeLogs(self):
        self.logger.initializeLogs.assert_called_once()

    # -----------------------------
    # validatePath()
    # -----------------------------
    @patch("os.path.exists")
    @patch("re.match")
    def test_validatePath_valid(self, mock_re_match, mock_exists):
        mock_exists.return_value = True
        mock_re_match.return_value = True

        success, message = self.helper.validatePath("/valid/path")

        self.assertTrue(success)
        self.assertIn("Path is valid", message)
        self.logger.log.assert_called_with(lp.DEBUG, message)

    @patch("os.path.exists")
    def test_validatePath_nonexistent(self, mock_exists):
        mock_exists.return_value = False

        success, message = self.helper.validatePath("/does/not/exist")

        self.assertFalse(success)
        self.assertIn("non-existent", message)
        self.logger.log.assert_called_with(lp.DEBUG, message)

    def test_validatePath_empty(self):
        success, message = self.helper.validatePath("")

        self.assertFalse(success)
        self.assertIn("not valid", message)
        self.logger.log.assert_called_with(lp.DEBUG, message)

    @patch("os.path.exists")
    @patch("re.match")
    def test_validatePath_invalid_characters(self, mock_re_match, mock_exists):
        mock_exists.return_value = True
        mock_re_match.return_value = None  # invalid chars

        success, message = self.helper.validatePath("/bad/<>path")

        self.assertFalse(success)
        self.assertIn("invalid characters", message)
        self.logger.log.assert_called_with(lp.DEBUG, message)

    def test_validatePath_wrong_type(self):
        success, message = self.helper.validatePath(123)

        self.assertFalse(success)
        self.assertIn("valid type", message)
        self.logger.log.assert_called_with(lp.DEBUG, message)

    # -----------------------------
    # mkdirs()
    # -----------------------------
    @patch("os.makedirs")
    @patch.object(FsHelperTemplate, "validatePath")
    def test_mkdirs_success(self, mock_validate, mock_makedirs):
        mock_validate.return_value = (True, "Path is valid")

        success, path = self.helper.mkdirs("/new/dir")

        mock_makedirs.assert_called_once_with("/new/dir", exist_ok=True)
        self.logger.log.assert_called_with(lp.DEBUG, "Directory created successfully")
        self.assertTrue(success)
        self.assertEqual(path, "/new/dir")

    @patch("os.makedirs", side_effect=OSError("Permission denied"))
    @patch.object(FsHelperTemplate, "validatePath")
    def test_mkdirs_oserror(self, mock_validate, mock_makedirs):
        mock_validate.return_value = (True, "Path is valid")

        success, path = self.helper.mkdirs("/restricted")

        self.logger.log.assert_called()  # error logged
        self.assertTrue(success)
        self.assertEqual(path, "/restricted")

    @patch.object(FsHelperTemplate, "validatePath")
    def test_mkdirs_invalid_path(self, mock_validate):
        mock_validate.return_value = (False, "Invalid path")

        success, path = self.helper.mkdirs("/bad/path")

        # makedirs should NOT be called
        self.assertEqual(mock_validate.call_count, 1)
        self.assertTrue(success)
        self.assertEqual(path, "/bad/path")

    # -----------------------------
    # Simple return-value methods
    # -----------------------------
    def test_getFsBlockSize(self):
        success, size = self.helper.getFsBlockSize()
        self.assertFalse(success)
        self.assertEqual(size, 0)

    def test_getDiskSize(self):
        success, size = self.helper.getDiskSize()
        self.assertFalse(success)
        self.assertEqual(size, 0)

    def test_getSizeInMb(self):
        success, size = self.helper.getSizeInMb()
        self.assertFalse(success)
        self.assertEqual(size, 0)

    def test_chown(self):
        success = self.helper.chown("/path", "user")
        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main()

