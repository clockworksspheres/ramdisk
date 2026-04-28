import unittest
import tempfile
import os
import io
import sys
import contextlib

from . PylintIface import processFile, PylintIface, AjsonReporter


class TestPylintInterface(unittest.TestCase):

    def _write_temp(self, code: str) -> str:
        f = tempfile.NamedTemporaryFile("w", suffix=".py", delete=False)
        f.write(code)
        f.flush()
        f.close()
        return f.name

    # ---------------------------------------------------------------
    # 1. Modern syntax error → E0001 must be reported
    # ---------------------------------------------------------------
    def test_syntax_error_reports_e0001(self):
        code = "def f():\n    return )\n"
        filename = self._write_temp(code)

        messages = processFile(filename)
        os.unlink(filename)

        self.assertTrue(
            any(m["msg_id"] == "E0001" for m in messages),
            "Expected E0001 syntax-error to be reported for invalid syntax",
        )

    # ---------------------------------------------------------------
    # 2. Clean file → expected messages
    # ---------------------------------------------------------------
    def test_clean_file_has_expected_messages(self):
        code = "def f():\n    return 1\n"
        filename = self._write_temp(code)

        messages = processFile(filename)
        os.unlink(filename)

        msg_ids = {m["msg_id"] for m in messages}

        # Modern Pylint always emits these for a minimal file
        self.assertIn("C0114", msg_ids)  # missing-module-docstring
        self.assertIn("C0116", msg_ids)  # missing-function-docstring

    # ---------------------------------------------------------------
    # 3. Class-based interface matches function interface
    # ---------------------------------------------------------------
    def test_class_interface_matches_function(self):
        code = "x = 1\n"
        filename = self._write_temp(code)

        iface = PylintIface()
        messages_class = iface.processFile(filename)
        messages_func = processFile(filename)

        os.unlink(filename)

        self.assertEqual(
            messages_class,
            messages_func,
            "Class-based and function-based interfaces should produce identical output",
        )

    # ---------------------------------------------------------------
    # 4. Reporter returns JSON-safe dicts
    # ---------------------------------------------------------------
    def test_reporter_returns_dicts(self):
        code = "x = 1\n"
        filename = self._write_temp(code)

        messages = processFile(filename)
        os.unlink(filename)

        for m in messages:
            self.assertIsInstance(m, dict)
            for key in ("msg_id", "symbol", "message", "path", "line", "column", "category", "confidence"):
                self.assertIn(key, m)

    # ---------------------------------------------------------------
    # 5. No SystemExit from processFile
    # ---------------------------------------------------------------
    def test_no_system_exit(self):
        code = "x = 1\n"
        filename = self._write_temp(code)

        try:
            processFile(filename)
        except SystemExit:
            self.fail("processFile() must never raise SystemExit (exit=False must be honored)")
        finally:
            os.unlink(filename)

    # ---------------------------------------------------------------
    # 6. Wrapper does not leak fatal banners to stdout/stderr
    #    (regression guard for your original problem)
    # ---------------------------------------------------------------
    def test_no_fatal_banner_leak(self):
        # Any file is fine here; we just assert streams are quiet
        code = "def f():\n    return 1\n"
        filename = self._write_temp(code)

        with contextlib.redirect_stdout(io.StringIO()) as fake_out, \
             contextlib.redirect_stderr(io.StringIO()) as fake_err:
            _ = processFile(filename)

        os.unlink(filename)

        self.assertNotIn("Fatal error while checking", fake_out.getvalue())
        self.assertNotIn("Fatal error while checking", fake_err.getvalue())


if __name__ == "__main__":
    unittest.main()

