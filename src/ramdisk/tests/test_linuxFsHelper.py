import sys
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))


# Run only on Linux
@unittest.skipUnless(sys.platform.lower().startswith("linux"), "Linux-only tests")
class TestFsHelperLinux(unittest.TestCase):

    def setUp(self):
        # Patch CyLogger
        logger_patcher = patch("lib.fsHelper.macosFsHelper.FsHelper.CyLogger")
        self.addCleanup(logger_patcher.stop)
        MockLogger = logger_patcher.start()
        self.mock_logger = MockLogger.return_value
        self.mock_logger.log = MagicMock()

        # Patch Environment
        env_patcher = patch("lib.fsHelper.macosFsHelper.FsHelper.Environment")
        self.addCleanup(env_patcher.stop)
        env_patcher.start()

        # Patch RunWith
        run_patcher = patch("lib.fsHelper.macosFsHelper.FsHelper.RunWith")
        self.addCleanup(run_patcher.stop)
        MockRunWith = run_patcher.start()
        self.mock_rw = MockRunWith.return_value
        self.mock_rw.setCommand = MagicMock()
        self.mock_rw.waitNpassThruStdout = MagicMock()

        # Import after patching
        from lib.fsHelper.macosFsHelper.FsHelper import FsHelper
        self.FsHelper = FsHelper
        self.helper = FsHelper()

    # ---------------------------------------------------------
    # getFsBlockSize
    # ---------------------------------------------------------
    def test_getFsBlockSize_success(self):
        # Simulate blockdev output
        self.mock_rw.waitNpassThruStdout.return_value = ("4096\n", "", 0)

        block_size = self.helper.getFsBlockSize()

        self.mock_rw.setCommand.assert_called_once()
        self.mock_rw.waitNpassThruStdout.assert_called_once()
        self.assertEqual(block_size, "4096\n")

    def test_getFsBlockSize_subprocess_error(self):
        from subprocess import SubprocessError
        self.mock_rw.waitNpassThruStdout.side_effect = SubprocessError("fail")

        block_size = self.helper.getFsBlockSize()

        # Should log a warning and return 0
        self.mock_logger.log.assert_called()
        self.assertEqual(block_size, 0)

    # ---------------------------------------------------------
    # getFsSectorSize
    # ---------------------------------------------------------
    def test_getFsSectorSize_success(self):
        # Simulate fdisk output
        fake_output = (
            "Disk /dev/sda: 100 GiB\n"
            "Units: sectors of 1 * 512 = 512 bytes\n"
            "Sector size (logical/physical): 512 bytes / 4096 bytes\n"
        )

        self.mock_rw.waitNpassThruStdout.return_value = (fake_output, "", 0)

        sector_bits = self.helper.getFsSectorSize()

        # 512 bytes → 512 * 8 = 4096 bits
        self.assertEqual(sector_bits, "4096")

    def test_getFsSectorSize_no_match(self):
        fake_output = "Some unrelated output\n"
        self.mock_rw.waitNpassThruStdout.return_value = (fake_output, "", 0)

        sector_bits = self.helper.getFsSectorSize()

        # No match → sectorSize stays 0 → "0 * 8" = "0"
        self.assertEqual(sector_bits, "0")

    def test_getFsSectorSize_subprocess_error(self):
        from subprocess import SubprocessError
        self.mock_rw.waitNpassThruStdout.side_effect = SubprocessError("fail")

        sector_bits = self.helper.getFsSectorSize()

        self.mock_logger.log.assert_called()
        self.assertEqual(sector_bits, "0")


if __name__ == "__main__":
    unittest.main()

