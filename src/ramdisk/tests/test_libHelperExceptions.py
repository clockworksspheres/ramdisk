import sys
import unittest
from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from lib.libHelperExceptions import (
    MemoryNotAvailableError,
    UnsupportedOSError,
    NotValidForThisOS,
    SystemToolNotAvailable,
    NotEnoughMemoryError,
    NotACyLoggerError,
    UserMustBeRootError,
)

class TestCustomExceptions(unittest.TestCase):

    def _test_exception(self, exc_class):
        """Helper to test basic exception behavior."""
        msg = "Test message"
        exc = exc_class(msg)
        self.assertIsInstance(exc, Exception)
        self.assertEqual(str(exc), msg)

    def test_MemoryNotAvailableError(self):
        self._test_exception(MemoryNotAvailableError)

    def test_UnsupportedOSError(self):
        self._test_exception(UnsupportedOSError)

    def test_NotValidForThisOS(self):
        self._test_exception(NotValidForThisOS)

    def test_SystemToolNotAvailable(self):
        self._test_exception(SystemToolNotAvailable)

    def test_NotEnoughMemoryError(self):
        self._test_exception(NotEnoughMemoryError)

    def test_NotACyLoggerError(self):
        self._test_exception(NotACyLoggerError)

    def test_UserMustBeRootError(self):
        self._test_exception(UserMustBeRootError)


if __name__ == "__main__":
    unittest.main()

