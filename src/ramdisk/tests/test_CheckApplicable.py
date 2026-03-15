import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))


class TestCheckApplicable(unittest.TestCase):

    def setUp(self):
        # Mock logger
        self.mock_logger = MagicMock()
        self.mock_logger.log = MagicMock()

        # Mock environment
        self.mock_env = MagicMock()
        self.mock_env.getosfamily.return_value = "Linux"
        self.mock_env.getosver.return_value = "10.2"
        self.mock_env.getostype.return_value = "Ubuntu"
        self.mock_env.getsystemfismacat.return_value = "med"
        self.mock_env.geteuid.return_value = 1000

        # Import class under test
        from lib.CheckApplicable import CheckApplicable
        self.CheckApplicable = CheckApplicable

        # Instance under test
        self.chk = CheckApplicable(self.mock_env, self.mock_logger)

    # ---------------------------------------------------------
    # isApplicableValid
    # ---------------------------------------------------------
    def test_isApplicableValid_good_dict(self):
        applicable = {
            "type": "white",
            "family": ["Linux"],
            "noroot": False,
            "fisma": "low",
            "os": {"Ubuntu": ["10.2"]}
        }
        self.assertTrue(self.chk.isApplicableValid(applicable))

    def test_isApplicableValid_bad_key(self):
        applicable = {"invalidKey": True}
        self.assertFalse(self.chk.isApplicableValid(applicable))

    def test_isApplicableValid_bad_value(self):
        applicable = {"type": "not_valid"}
        self.assertFalse(self.chk.isApplicableValid(applicable))

    # ---------------------------------------------------------
    # isInRange
    # ---------------------------------------------------------
    def test_isInRange_plus(self):
        self.chk.myosversion = "10.5"
        self.assertTrue(self.chk.isInRange(["10.2", "+"]))

    def test_isInRange_minus(self):
        self.chk.myosversion = "9.1"
        self.assertTrue(self.chk.isInRange(["10.2", "-"]))

    def test_isInRange_range(self):
        self.chk.myosversion = "10.5"
        self.assertTrue(self.chk.isInRange(["10.2", "r", "11.0"]))

    def test_isInRange_explicit(self):
        self.chk.myosversion = "10.2"
        self.assertTrue(self.chk.isInRange(["10.2"]))

    # ---------------------------------------------------------
    # isApplicable
    # ---------------------------------------------------------
    def test_isApplicable_default(self):
        self.chk.applicable = {
            "type": "white",
            "family": ["Linux"]
        }
        self.assertTrue(self.chk.isApplicable({"default": "default"}))

    def test_isApplicable_blacklist_family(self):
        applicable = {
            "type": "black",
            "family": ["Linux"]
        }
        self.assertFalse(self.chk.isApplicable(applicable))

    def test_isApplicable_whitelist_family(self):
        applicable = {
            "type": "white",
            "family": ["Linux"]
        }
        self.assertTrue(self.chk.isApplicable(applicable))

    @patch("re.search", return_value=True)
    def test_isApplicable_os_match(self, _):
        applicable = {
            "type": "white",
            "os": {"Ubuntu": ["10.2"]}
        }
        self.assertTrue(self.chk.isApplicable(applicable))

    def test_isApplicable_noroot(self):
        self.mock_env.geteuid.return_value = 0
        applicable = {
            "type": "white",
            "family": ["Linux"],
            "noroot": True
        }
        self.assertFalse(self.chk.isApplicable(applicable))

    # ---------------------------------------------------------
    # fismaApplicable
    # ---------------------------------------------------------
    def test_fismaApplicable_low_system_med(self):
        self.mock_env.getsystemfismacat.return_value = "med"
        # According to implementation, this should be False
        self.assertFalse(self.chk.fismaApplicable("low", "med"))

    def test_fismaApplicable_low_system_high(self):
        self.mock_env.getsystemfismacat.return_value = "high"
        self.assertFalse(self.chk.fismaApplicable("low", "high"))

    def test_fismaApplicable_high_system_med(self):
        self.mock_env.getsystemfismacat.return_value = "med"
        self.assertFalse(self.chk.fismaApplicable("high", "med"))

    def test_fismaApplicable_invalid_level(self):
        # Force getSystemFismaLevel() to fail
        self.chk.getSystemFismaLevel = MagicMock(side_effect=KeyError("boom"))

        with self.assertRaises(ValueError):
            self.chk.fismaApplicable("invalid", "med")

    # ---------------------------------------------------------
    # Getters / Setters
    # ---------------------------------------------------------
    def test_setters_and_getters(self):
        self.chk.setOsFamily("Debian")
        self.chk.setOsType("DebianType")
        self.chk.setOsVer("9.9")
        self.chk.setSystemFismaLevel("high")

        self.assertEqual(self.chk.getOsFamily(), "Debian")
        self.assertEqual(self.chk.getOsType(), "DebianType")
        self.assertEqual(self.chk.getOsVer(), "9.9")
        self.assertEqual(self.chk.getSystemFismaLevel(), "high")

    def test_setOsBasedOnEnv(self):
        self.chk.setOsBasedOnEnv()
        self.assertEqual(self.chk.myosfamily, "Linux")
        self.assertEqual(self.chk.myosversion, "10.2")
        self.assertEqual(self.chk.myostype, "Ubuntu")


if __name__ == "__main__":
    unittest.main()

