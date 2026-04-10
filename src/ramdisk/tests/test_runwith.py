import sys
import time
import unittest
from unittest.mock import ANY, patch, MagicMock
from subprocess import PIPE
from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from lib.run_commands import RunWith, SetCommandTypeError


def make_proc(stdout="", stderr="", returncode=0):
    proc = MagicMock()
    proc.communicate.return_value = (stdout, stderr)
    proc.returncode = returncode
    proc.stdout = MagicMock()
    proc.stderr = MagicMock()
    return proc


# ----------------------------------------------------------------------
# SETCOMMAND TESTS
# ----------------------------------------------------------------------
class TestSetCommand(unittest.TestCase):

    def test_set_command_list(self):
        rw = RunWith(use_logger=False)
        rw.setCommand(["echo", "hello"])
        self.assertEqual(rw.command, ["echo", "hello"])
        self.assertFalse(rw.myshell)

    def test_set_command_string(self):
        rw = RunWith(use_logger=False)
        rw.setCommand("echo hello")
        self.assertEqual(rw.command, "echo hello")
        self.assertTrue(rw.myshell)

    def test_set_command_invalid_type(self):
        rw = RunWith(use_logger=False)
        with self.assertRaises(SetCommandTypeError):
            rw.setCommand(12345)


# ----------------------------------------------------------------------
# COMMUNICATE TESTS
# ----------------------------------------------------------------------
class TestCommunicate(unittest.TestCase):

    @patch("lib.run_commands.Popen")
    def test_communicate_success_list(self, mock_popen):
        proc = make_proc(stdout="ok", stderr="", returncode=0)
        mock_popen.return_value = proc

        rw = RunWith(use_logger=False)
        rw.setCommand(["echo", "ok"])
        out, err, rc = rw.communicate()

        self.assertEqual(out, "ok")
        self.assertEqual(err, "")
        self.assertEqual(rc, 0)

    @patch("lib.run_commands.Popen")
    def test_communicate_success_string_shell(self, mock_popen):
        proc = make_proc(stdout="hello\n", stderr="", returncode=0)
        mock_popen.return_value = proc

        rw = RunWith(use_logger=False)
        rw.setCommand("echo hello")
        out, err, rc = rw.communicate()

        self.assertEqual(out, "hello\n")
        self.assertEqual(err, "")
        self.assertEqual(rc, 0)

    @patch("lib.run_commands.Popen", side_effect=OSError("boom"))
    def test_communicate_popen_raises(self, mock_popen):
        rw = RunWith(use_logger=False)
        rw.setCommand(["echo", "x"])
        with self.assertRaises(OSError):
            rw.communicate()

    @patch("lib.run_commands.Popen")
    def test_communicate_communicate_raises(self, mock_popen):
        proc = MagicMock()
        proc.communicate.side_effect = RuntimeError("fail")
        mock_popen.return_value = proc

        rw = RunWith(use_logger=False)
        rw.setCommand(["echo", "x"])
        with self.assertRaises(RuntimeError):
            rw.communicate()


# ----------------------------------------------------------------------
# WAIT TESTS
# ----------------------------------------------------------------------
class TestWait(unittest.TestCase):

    @patch("lib.run_commands.Popen")
    def test_wait_success(self, mock_popen):
        proc = MagicMock()
        proc.stdout.readline.return_value = ""
        proc.stderr.readline.return_value = ""
        proc.returncode = 0
        mock_popen.return_value = proc

        rw = RunWith(use_logger=False)
        rw.setCommand(["echo", "ok"])
        out, err, rc = rw.wait()

        self.assertEqual(rc, 0)


# ----------------------------------------------------------------------
# WAITNPASSTHRUSTDOUT TESTS
# ----------------------------------------------------------------------
class TestWaitNpassThruStdout(unittest.TestCase):

    @patch("lib.run_commands.Popen")
    def test_waitNpassThruStdout_basic(self, mock_popen):
        proc = MagicMock()
        proc.stdout.readline.side_effect = ["line1\n", ""]
        proc.stderr.readline.side_effect = ["", ""]
        proc.poll.return_value = 0
        proc.returncode = 0
        mock_popen.return_value = proc

        rw = RunWith(use_logger=False)
        rw.setCommand(["echo", "ok"])
        out, err, rc = rw.waitNpassThruStdout()

        self.assertIn("line1", out)
        self.assertEqual(err.strip(), "")
        self.assertEqual(rc, 0)


# ----------------------------------------------------------------------
# TIMEOUT TESTS
# ----------------------------------------------------------------------
class TestTimeout(unittest.TestCase):

    @patch("lib.run_commands.Popen")
    def test_timeout_no_timeout(self, mock_popen):
        proc = make_proc(stdout="done", stderr="", returncode=0)
        mock_popen.return_value = proc

        rw = RunWith(use_logger=False)
        rw.setCommand(["echo", "ok"])
        out, err, rc, timed_out = rw.timeout(1)

        self.assertEqual(out, "done")
        self.assertFalse(timed_out)

    @patch("lib.run_commands.Popen")
    def test_timeout_kill(self, mock_popen):
        proc = MagicMock()

        def slow_communicate():
            time.sleep(0.2)
            return("", "")

        proc.communicate.side_effect = slow_communicate
        proc.returncode = -9
        mock_popen.return_value = proc

        rw = RunWith(use_logger=False)
        rw.setCommand(["sleep", "5"])
        out, err, rc, timed_out = rw.timeout(0.01)

        self.assertTrue(timed_out)


# ----------------------------------------------------------------------
# GETTERS TESTS
# ----------------------------------------------------------------------
class TestGetters(unittest.TestCase):

    def test_getters(self):
        rw = RunWith(use_logger=False)
        rw.stdout = "A"
        rw.stderr = "B"
        rw.retcode = 5

        self.assertEqual(rw.getStdout(), "A")
        self.assertEqual(rw.getStderr(), "B")
        self.assertEqual(rw.getReturnCode(), 5)
        self.assertEqual(rw.getReturns(), ("A", "B", 5))


# ----------------------------------------------------------------------
# INTEGRATION STYLE TESTS
# ----------------------------------------------------------------------
class TestIntegration(unittest.TestCase):

    @patch("lib.run_commands.Popen")
    def test_end_to_end_string(self, mock_popen):
        proc = make_proc(stdout="hello world\n", stderr="", returncode=0)
        mock_popen.return_value = proc

        rw = RunWith(use_logger=False)
        rw.setCommand("echo 'hello world'")
        rw.communicate()

        self.assertEqual(rw.getStdout(), "hello world\n")
        self.assertEqual(rw.getReturnCode(), 0)

    @patch("lib.run_commands.Popen")
    def test_end_to_end_list(self, mock_popen):
        proc = make_proc(stdout="ok\n", stderr="", returncode=0)
        mock_popen.return_value = proc

        rw = RunWith(use_logger=False)
        rw.setCommand(["echo", "ok"])
        rw.communicate()

        self.assertEqual(rw.getStdout(), "ok\n")
        self.assertEqual(rw.getReturnCode(), 0)


# ----------------------------------------------------------------------
# Test advanced functionality of RunWith
# ----------------------------------------------------------------------
class TestAdvanced(unittest.TestCase):

    def setUp(self):
        self.runner = RunWith(use_logger=False)

    # ---------------------------------
    # MOCK PTY + SELECT (runCommand2check)
    # ---------------------------------
    @patch("logging.FileHandler.close", return_value=None)
    @patch("subprocess.Popen")
    @patch("os.write")
    @patch("os.read")
    @patch("select.select")
    @patch("pty.openpty")
    @patch('os.close')
    @patch('os.open', return_value=10)
    def test_runCommand2check_prompt_detected(
        self,
        mock_open,
        mock_close,
        mock_openpty,    # from bottom @patch
        mock_select,
        mock_read,
        mock_write,
        mock_popen,
        mock_log_close   # from top @patch
    ):
        # Setup
        mock_openpty.return_value = (10, 11)  # (master, slave)
        mock_select.return_value = ([10], [], [])  # master fd is ready

        # Simulate process output
        mock_read.side_effect = [b"Password:", b"done", b""]

        # Fake process
        proc = MagicMock()
        proc.poll.side_effect = [None, None, 0]  # Running, then done
        mock_popen.return_value = proc

        # Test
        found, output = self.runner.runCommand2check(
            check_string="Password:",
            get_my_pass=lambda: "secret"
        )

        # Assertions
        self.assertTrue(found)
        self.assertEqual(output, "")
        mock_read.assert_any_call(10, 1024)  # Was read called?
        mock_write.assert_called_once_with(10, b"secret\n")  # Was password sent?

    # ---------------------------------
    # MOCK runWithSudo (select loop)
    # ---------------------------------
    @patch("logging.FileHandler.close", return_value=None)   # top → last arg
    @patch("lib.run_commands.os.set_blocking", return_value=None)
    @patch("lib.run_commands.select.select")
    @patch("lib.run_commands.subprocess.Popen")                  # bottom → first arg
    def test_runWithSudo_basic(
        self,
        mock_popen,
        mock_select,
        mock_set_blocking,
        mock_log_close
    ):

        import io

        captured_stderr = b''

        proc = MagicMock()
        proc.stdout = io.BytesIO(b"ok")
        proc.stdout.fileno = MagicMock(return_value=1)
        proc.stderr = io.BytesIO(b"")
        proc.stderr.fileno = MagicMock(return_value=2)

        # Capture the stderr content *before* the process is polled for the final time
        def capture_on_last_poll(*args, **kwargs):
            nonlocal captured_stderr
            proc.stderr.seek(0)
            captured_stderr = proc.stderr.read()
            return 0 # Simulate the process finishing

        proc.poll.side_effect = [None, capture_on_last_poll] # Read on second poll
        proc.wait.return_value = 0

        mock_popen.return_value = proc

        mock_select.side_effect = [
            ([proc.stdout], [proc.stdin], []),
            ([], [], [])
        ]

        self.runner.setCommand(["ls"])
        out, err, rc = self.runner.runWithSudo(password="pw")

        self.assertIn("ok", out)
        self.assertEqual(captured_stderr.decode(), "")
        self.assertEqual(rc, 0)

    # ---------------------------------
    # TIMEOUT forced kill
    # ---------------------------------
    @patch("lib.run_commands.Popen")
    @patch("lib.run_commands.threading.Timer")
    def test_timeout_forced(self, mock_timer, mock_popen):
        proc = MagicMock()
        proc.communicate.return_value = ("", "")
        proc.returncode = -9

        mock_popen.return_value = proc

        def fake_timer(timeout_sec, func, args):
            # simulate timer firing immediately
            func(*args)

            timer_mock = MagicMock()
            timer_mock.start = MagicMock()
            timer_mock.cancel = MagicMock()
            return timer_mock

        mock_timer.side_effect = fake_timer

        self.runner.setCommand(["cmd"])

        _, _, rc, timed_out = self.runner.timeout(1)

        self.assertTrue(timed_out)






if __name__ == "__main__":
    unittest.main()

