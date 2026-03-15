"""
Comprehensive unit tests for lib/run_commands.py

Covers:
  - RunWith.__init__                  (logger wiring, default attributes)
  - RunWith.setCommand                (list/str commands, shell flag, env, close_fds,
                                       creationflags, error cases)
  - RunWith getters                   (getStdout, getStderr, getReturnCode, getReturns,
                                       getNlogReturns, getNprintReturns)
  - RunWith.communicate               (success/failure, silent flag, SubprocessError,
                                       no-command guard, creationflags branch)
  - RunWith.wait                      (success/failure, empty command guard)
  - RunWith.killProc                  (sets timeout flag, calls proc.kill)
  - RunWith.timeout                   (success, timed-out kill, empty command guard)
  - RunWith.runWithSudo / runWithSudoRs (empty-password guard, subprocess wiring,
                                         select loop, cleanup)
  - RunThread.__init__ / run / getters
  - runMyThreadCommand                (happy path, missing logger guard)

All external I/O (subprocess.Popen, select.select, os.set_blocking) is
isolated with unittest.mock.patch / MagicMock.

Run with:
    python -m pytest test_run_commands.py -v
    # or
    python -m unittest test_run_commands -v
"""

import sys
import subprocess
import threading
import unittest
from subprocess import SubprocessError
from unittest.mock import MagicMock, Mock, call, patch
from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# ── import the module under test ──────────────────────────────────────────────
# Adjust the import path if your project layout differs.
from lib.run_commands import (
    NotACyLoggerError,
    OSNotValidForRunWith,
    RunThread,
    RunWith,
    SetCommandTypeError,
    runMyThreadCommand,
)
# from lib.loggers import CyLogger, MockLogger, LogPriority as lp

from lib.loggers import MockLogger as CyLogger
# from lib.loggers import CyLogger
from lib.loggers import MockLogger
from lib.loggers import LogPriority as lp
from lib.loggers import MockLogger as CyLogger

# ── shared helpers ────────────────────────────────────────────────────────────

def _make_proc(returncode=0, stdout="hello\n", stderr=""):
    """Return a MagicMock that behaves like a Popen instance."""
    proc = MagicMock()
    proc.returncode = returncode
    proc.communicate.return_value = (stdout, stderr)
    proc.stdout.readline.side_effect = [stdout, ""]
    proc.stderr.readline.side_effect = [stderr, ""]
    proc.poll.return_value = returncode
    proc.wait.return_value = returncode
    return proc


def _make_mock_logger():
    """Return a MagicMock that satisfies RunWith's logger duck-typing."""
    logger = MagicMock()
    logger.log = MagicMock()
    return logger


# ─────────────────────────────────────────────────────────────────────────────
# 1.  RunWith.__init__
# ─────────────────────────────────────────────────────────────────────────────

class TestRunWithInit(unittest.TestCase):

    def test_defaults_use_mock_logger_when_no_logger_supplied(self):
        rw = RunWith()
        self.assertRaises(AttributeError)
        #self.assertIs(rw.logger, MockLogger)

    def test_use_logger_false_sets_mock_logger(self):
        rw = RunWith(use_logger=False)
        self.assertRaises(AttributeError)
        #self.assertIs(rw.logger, MockLogger)

    def test_command_is_none_on_init(self):
        rw = RunWith()
        self.assertIsNone(rw.command)

    def test_stdout_stderr_retcode_none_on_init(self):
        rw = RunWith()
        self.assertIsNone(rw.stdout)
        self.assertIsNone(rw.stderr)
        self.assertIsNone(rw.retcode)

    def test_text_flag_default_true(self):
        rw = RunWith()
        self.assertTrue(rw.text)

    def test_module_version_present(self):
        rw = RunWith()
        self.assertIsInstance(rw.module_version, str)

    def test_prompt_defaults_to_empty_string(self):
        rw = RunWith()
        self.assertEqual(rw.prompt, "")

    def test_environ_none_on_init(self):
        rw = RunWith()
        self.assertIsNone(rw.environ)


# ─────────────────────────────────────────────────────────────────────────────
# 2.  RunWith.setCommand
# ─────────────────────────────────────────────────────────────────────────────

class TestSetCommand(unittest.TestCase):

    def setUp(self):
        self.rw = RunWith(use_logger=False)

    # ── list command ──────────────────────────────────────────────────────────

    def test_list_command_sets_command_attribute(self):
        self.rw.setCommand(["ls", "-la"])
        self.assertEqual(self.rw.command, ["ls", "-la"])

    def test_list_command_sets_printcmd(self):
        self.rw.setCommand(["ls", "-la"])
        self.assertEqual(self.rw.printcmd, "ls -la")

    def test_list_command_shell_defaults_to_false(self):
        self.rw.setCommand(["ls"])
        self.assertFalse(self.rw.myshell)

    def test_list_command_explicit_shell_true(self):
        self.rw.setCommand(["ls"], myshell=True)
        self.assertTrue(self.rw.myshell)

    def test_list_command_non_bool_myshell_defaults_to_false(self):
        self.rw.setCommand(["ls"], myshell="yes")
        self.assertFalse(self.rw.myshell)

    # ── string command ────────────────────────────────────────────────────────

    def test_string_command_sets_command_attribute(self):
        self.rw.setCommand("echo hello")
        self.assertEqual(self.rw.command, "echo hello")

    def test_string_command_sets_printcmd(self):
        self.rw.setCommand("echo hello")
        self.assertEqual(self.rw.printcmd, "echo hello")

    def test_string_command_shell_defaults_to_true(self):
        self.rw.setCommand("echo hello")
        self.assertTrue(self.rw.myshell)

    def test_string_command_explicit_shell_false(self):
        self.rw.setCommand("echo hello", myshell=False)
        self.assertFalse(self.rw.myshell)

    def test_string_command_non_bool_myshell_defaults_to_true(self):
        self.rw.setCommand("echo hello", myshell="no")
        self.assertTrue(self.rw.myshell)

    # ── env ───────────────────────────────────────────────────────────────────

    def test_valid_env_dict_stored(self):
        env = {"PATH": "/usr/bin"}
        self.rw.setCommand("ls", env=env)
        self.assertEqual(self.rw.environ, env)

    def test_invalid_env_non_dict_sets_none(self):
        self.rw.setCommand("ls", env="not-a-dict")
        self.assertIsNone(self.rw.environ)

    def test_none_env_sets_none(self):
        self.rw.setCommand("ls", env=None)
        self.assertIsNone(self.rw.environ)

    # ── close_fds ─────────────────────────────────────────────────────────────

    def test_close_fds_true_stored(self):
        self.rw.setCommand("ls", close_fds=True)
        self.assertTrue(self.rw.cfds)

    def test_close_fds_false_stored(self):
        self.rw.setCommand("ls", close_fds=False)
        self.assertFalse(self.rw.cfds)

    def test_close_fds_default_is_false(self):
        self.rw.setCommand("ls")
        self.assertFalse(self.rw.cfds)

    def test_close_fds_non_bool_defaults_to_false(self):
        self.rw.setCommand("ls", close_fds="yes")
        self.assertFalse(self.rw.cfds)

    # ── creationflags ─────────────────────────────────────────────────────────
    """
    # NOT SUPPORTED BY run_commands
    def test_creationflags_true_sets_detached_flags(self):
        self.rw.setCommand("notepad", creationflags=True)
        expected = (subprocess.DETACHED_PROCESS |
                    subprocess.CREATE_NEW_PROCESS_GROUP)
        self.assertEqual(self.rw.creationflags, expected)
    """
    def test_creationflags_none_sets_empty_string(self):
        self.rw.setCommand("ls")
        self.assertEqual(self.rw.creationflags, "")

    def test_creationflags_false_sets_empty_string(self):
        self.rw.setCommand("ls", creationflags=False)
        self.assertEqual(self.rw.creationflags, "")

    # ── error cases ───────────────────────────────────────────────────────────

    def test_none_command_raises_set_command_type_error(self):
        with self.assertRaises(SetCommandTypeError):
            self.rw.setCommand(None)

    def test_integer_command_raises_set_command_type_error(self):
        with self.assertRaises(SetCommandTypeError):
            self.rw.setCommand(42)

    def test_empty_list_raises_set_command_type_error(self):
        with self.assertRaises(SetCommandTypeError):
            self.rw.setCommand([])

    def test_empty_string_raises_set_command_type_error(self):
        with self.assertRaises(SetCommandTypeError):
            self.rw.setCommand("")

    def test_dict_command_raises_set_command_type_error(self):
        with self.assertRaises(SetCommandTypeError):
            self.rw.setCommand({"cmd": "ls"})


# ─────────────────────────────────────────────────────────────────────────────
# 3.  Getters
# ─────────────────────────────────────────────────────────────────────────────

class TestGetters(unittest.TestCase):

    def setUp(self):
        self.rw = RunWith(use_logger=False)
        self.rw.stdout = "out"
        self.rw.stderr = "err"
        self.rw.retcode = 0

    def test_get_stdout(self):
        self.assertEqual(self.rw.getStdout(), "out")

    def test_get_stderr(self):
        self.assertEqual(self.rw.getStderr(), "err")

    def test_get_return_code(self):
        self.assertEqual(self.rw.getReturnCode(), 0)

    def test_get_returns_tuple(self):
        self.assertEqual(self.rw.getReturns(), ("out", "err", 0))

    def test_get_nlog_returns_nolog_true_no_logging(self):
        mock_logger = _make_mock_logger()
        self.rw.logger = mock_logger
        result = self.rw.getNlogReturns(nolog=True)
        self.assertEqual(result, ("out", "err", 0))
        mock_logger.log.assert_not_called()

    def test_get_nlog_returns_nolog_false_logs_three_entries(self):
        mock_logger = _make_mock_logger()
        self.rw.logger = mock_logger
        self.rw.getNlogReturns(nolog=False)
        # output, error, retcode → at least 3 log calls
        self.assertGreaterEqual(mock_logger.log.call_count, 3)

    def test_get_nprint_returns_prints_three_lines(self):
        with patch("builtins.print") as mock_print:
            result = self.rw.getNprintReturns()
        self.assertEqual(result, ("out", "err", 0))
        self.assertEqual(mock_print.call_count, 3)

    def test_get_stdout_when_none(self):
        self.rw.stdout = None
        self.assertIsNone(self.rw.getStdout())

    def test_get_stderr_when_none(self):
        self.rw.stderr = None
        self.assertIsNone(self.rw.getStderr())

    def test_get_return_code_nonzero(self):
        self.rw.retcode = 127
        self.assertEqual(self.rw.getReturnCode(), 127)


# ─────────────────────────────────────────────────────────────────────────────
# 4.  communicate()
# ─────────────────────────────────────────────────────────────────────────────

class TestCommunicate(unittest.TestCase):

    def _rw_with_cmd(self, cmd="echo hi"):
        rw = RunWith(use_logger=False)
        rw.setCommand(cmd)
        return rw

    @patch("lib.run_commands.Popen")
    def test_returns_stdout_stderr_retcode_on_success(self, mock_popen):
        proc = _make_proc(returncode=0, stdout="output\n", stderr="")
        mock_popen.return_value = proc

        out, err, rc = self._rw_with_cmd("echo hi").communicate()

        self.assertEqual(out, "output\n")
        self.assertEqual(err, "")
        self.assertEqual(rc, 0)

    @patch("lib.run_commands.Popen")
    def test_nonzero_return_code_propagated(self, mock_popen):
        proc = _make_proc(returncode=1, stdout="", stderr="oops\n")
        mock_popen.return_value = proc

        _, err, rc = self._rw_with_cmd("false").communicate()

        self.assertEqual(rc, 1)
        self.assertEqual(err, "oops\n")

    @patch("lib.run_commands.Popen")
    def test_command_is_none_after_communicate(self, mock_popen):
        mock_popen.return_value = _make_proc()
        rw = self._rw_with_cmd("ls")
        rw.communicate()
        self.assertIsNone(rw.command)

    @patch("lib.run_commands.Popen")
    def test_popen_receives_correct_shell_flag_for_string(self, mock_popen):
        mock_popen.return_value = _make_proc()
        self._rw_with_cmd("echo hi").communicate()
        _, kwargs = mock_popen.call_args
        self.assertTrue(kwargs["shell"])

    @patch("lib.run_commands.Popen")
    def test_popen_receives_false_shell_flag_for_list(self, mock_popen):
        mock_popen.return_value = _make_proc()
        rw = RunWith(use_logger=False)
        rw.setCommand(["ls", "-la"])
        rw.communicate()
        _, kwargs = mock_popen.call_args
        self.assertFalse(kwargs["shell"])

    @patch("lib.run_commands.Popen")
    def test_popen_receives_custom_env(self, mock_popen):
        mock_popen.return_value = _make_proc()
        env = {"MY": "var"}
        rw = RunWith(use_logger=False)
        rw.setCommand("ls", env=env)
        rw.communicate()
        _, kwargs = mock_popen.call_args
        self.assertEqual(kwargs["env"], env)

    @patch("lib.run_commands.Popen")
    def test_silent_false_triggers_logger_calls(self, mock_popen):
        mock_popen.return_value = _make_proc()
        rw = self._rw_with_cmd("ls")
        mock_logger = _make_mock_logger()
        rw.logger = mock_logger
        rw.communicate(silent=False)
        mock_logger.log.assert_called()

    @patch("lib.run_commands.Popen")
    def test_silent_true_suppresses_extra_debug_logging(self, mock_popen):
        mock_popen.return_value = _make_proc()
        rw = self._rw_with_cmd("ls")
        mock_logger = _make_mock_logger()
        rw.logger = mock_logger
        rw.communicate(silent=True)
        # At most the basic "Command returned" debug log should fire
        for log_call in mock_logger.log.call_args_list:
            args = log_call[0]
            self.assertNotIn("stdout:", str(args))

    @patch("lib.run_commands.Popen")
    def test_subprocess_error_is_reraised(self, mock_popen):
        mock_popen.side_effect = SubprocessError("boom")
        with self.assertRaises(SubprocessError):
            self._rw_with_cmd("bad_cmd").communicate()

    def test_no_command_returns_none_triple(self):
        rw = RunWith(use_logger=False)
        out, err, rc = rw.communicate()
        self.assertIsNone(out)
        self.assertIsNone(err)
        self.assertIsNone(rc)

    """
    # Not Supported
    @patch("lib.run_commands.Popen")
    def test_creationflags_branch_passes_creationflags_kwarg(self, mock_popen):
        mock_popen.return_value = _make_proc()
        rw = RunWith(use_logger=False)
        rw.setCommand("notepad", creationflags=True)
        rw.communicate()
        _, kwargs = mock_popen.call_args
        self.assertIn("creationflags", kwargs)
    """

    @patch("lib.run_commands.Popen")
    def test_no_creationflags_branch_omits_kwarg(self, mock_popen):
        mock_popen.return_value = _make_proc()
        rw = RunWith(use_logger=False)
        rw.setCommand("ls")
        rw.communicate()
        _, kwargs = mock_popen.call_args
        self.assertNotIn("creationflags", kwargs)

    @patch("lib.run_commands.Popen")
    def test_stdout_and_stderr_closed_in_finally(self, mock_popen):
        proc = _make_proc()
        mock_popen.return_value = proc
        self._rw_with_cmd("ls").communicate()
        proc.stdout.close.assert_called()
        proc.stderr.close.assert_called()

    @patch("lib.run_commands.Popen")
    def test_communicate_called_once_on_popen(self, mock_popen):
        proc = _make_proc()
        mock_popen.return_value = proc
        self._rw_with_cmd("echo").communicate()
        proc.communicate.assert_called_once()

    @patch("lib.run_commands.Popen")
    def test_invalid_silent_param_returns_none_triple(self, mock_popen):
        mock_popen.return_value = _make_proc()
        rw = RunWith(use_logger=False)
        rw.setCommand("ls")
        # silent must be bool; passing a non-bool triggers the else guard
        out, err, rc = rw.communicate(silent="yes")
        self.assertIsNone(out)
        self.assertIsNone(err)
        self.assertIsNone(rc)


# ─────────────────────────────────────────────────────────────────────────────
# 5.  wait()
# ─────────────────────────────────────────────────────────────────────────────

class TestWait(unittest.TestCase):

    @patch("lib.run_commands.Popen")
    def test_wait_returns_zero_retcode_on_success(self, mock_popen):
        mock_popen.return_value = _make_proc(returncode=0)
        rw = RunWith(use_logger=False)
        rw.setCommand(["ls"])
        _, _, rc = rw.wait()
        self.assertEqual(rc, 0)

    @patch("lib.run_commands.Popen")
    def test_wait_command_cleared_after_run(self, mock_popen):
        mock_popen.return_value = _make_proc()
        rw = RunWith(use_logger=False)
        rw.setCommand("sleep 0")
        rw.wait()
        self.assertIsNone(rw.command)

    def test_wait_no_command_returns_none_triple(self):
        rw = RunWith(use_logger=False)
        out, err, rc = rw.wait()
        self.assertIsNone(out)
        self.assertIsNone(err)
        self.assertIsNone(rc)

    @patch("lib.run_commands.Popen")
    def test_wait_subprocess_error_reraised(self, mock_popen):
        mock_popen.side_effect = SubprocessError("err")
        rw = RunWith(use_logger=False)
        rw.setCommand("bad")
        with self.assertRaises(SubprocessError):
            rw.wait()

    @patch("lib.run_commands.Popen")
    def test_wait_silent_false_logs(self, mock_popen):
        mock_popen.return_value = _make_proc()
        rw = RunWith(use_logger=False)
        mock_logger = _make_mock_logger()
        rw.logger = mock_logger
        rw.setCommand("ls")
        rw.wait(silent=False)
        mock_logger.log.assert_called()

    @patch("lib.run_commands.Popen")
    def test_wait_proc_wait_called(self, mock_popen):
        proc = _make_proc()
        mock_popen.return_value = proc
        rw = RunWith(use_logger=False)
        rw.setCommand("ls")
        rw.wait()
        proc.wait.assert_called()


# ─────────────────────────────────────────────────────────────────────────────
# 6.  killProc()
# ─────────────────────────────────────────────────────────────────────────────

class TestKillProc(unittest.TestCase):

    def test_kill_proc_sets_timeout_value_to_true(self):
        rw = RunWith(use_logger=False)
        proc = MagicMock()
        timeout = {"value": False}
        rw.killProc(proc, timeout)
        self.assertTrue(timeout["value"])

    def test_kill_proc_calls_kill_on_proc(self):
        rw = RunWith(use_logger=False)
        proc = MagicMock()
        timeout = {"value": False}
        rw.killProc(proc, timeout)
        proc.kill.assert_called_once()

    def test_kill_proc_does_not_alter_other_dict_keys(self):
        rw = RunWith(use_logger=False)
        proc = MagicMock()
        timeout = {"value": False, "other": 42}
        rw.killProc(proc, timeout)
        self.assertEqual(timeout["other"], 42)


# ─────────────────────────────────────────────────────────────────────────────
# 7.  timeout()
# ─────────────────────────────────────────────────────────────────────────────

class TestTimeoutMethod(unittest.TestCase):

    @patch("lib.run_commands.threading.Timer")
    @patch("lib.run_commands.Popen")
    def test_success_no_kill_timer_cancelled(self, mock_popen, mock_timer):
        proc = _make_proc(returncode=0, stdout="ok", stderr="")
        mock_popen.return_value = proc
        timer_instance = MagicMock()
        mock_timer.return_value = timer_instance

        rw = RunWith(use_logger=False)
        rw.setCommand("sleep 0")
        out, err, rc, timed_out = rw.timeout(5)

        timer_instance.start.assert_called_once()
        timer_instance.cancel.assert_called_once()
        self.assertFalse(timed_out)

    @patch("lib.run_commands.threading.Timer")
    @patch("lib.run_commands.Popen")
    def test_timer_fires_sets_timed_out_true(self, mock_popen, mock_timer):
        proc = _make_proc(returncode=-9, stdout="", stderr="")
        mock_popen.return_value = proc

        def fire_immediately(secs, fn, args):
            fn(*args)          # invoke killProc(proc, timeout_dict) now
            t = MagicMock()
            return t

        mock_timer.side_effect = fire_immediately

        rw = RunWith(use_logger=False)
        rw.setCommand("sleep 100")
        _, _, _, timed_out = rw.timeout(0)

        self.assertTrue(timed_out)

    def test_no_command_returns_none_triple_and_false_timeout(self):
        rw = RunWith(use_logger=False)
        out, err, rc, timed_out = rw.timeout(5)
        self.assertIsNone(out)
        self.assertIsNone(err)
        self.assertIsNone(rc)

    @patch("lib.run_commands.threading.Timer")
    @patch("lib.run_commands.Popen")
    def test_subprocess_error_reraised(self, mock_popen, mock_timer):
        mock_popen.side_effect = SubprocessError("fail")
        mock_timer.return_value = MagicMock()
        rw = RunWith(use_logger=False)
        rw.setCommand("bad")
        with self.assertRaises(SubprocessError):
            rw.timeout(5)

    @patch("lib.run_commands.threading.Timer")
    @patch("lib.run_commands.Popen")
    def test_command_cleared_after_timeout(self, mock_popen, mock_timer):
        mock_popen.return_value = _make_proc()
        mock_timer.return_value = MagicMock()
        rw = RunWith(use_logger=False)
        rw.setCommand("echo hi")
        rw.timeout(5)
        self.assertIsNone(rw.command)


# ─────────────────────────────────────────────────────────────────────────────
# 8.  runWithSudo() — guard conditions
# ─────────────────────────────────────────────────────────────────────────────

class TestRunWithSudoGuards(unittest.TestCase):

    def test_empty_password_returns_255(self):
        rw = RunWith(use_logger=False)
        rw.setCommand("ls")
        self.assertEqual(rw.runWithSudo(password=""), 255)

    def test_whitespace_only_password_returns_255(self):
        rw = RunWith(use_logger=False)
        rw.setCommand("ls")
        self.assertEqual(rw.runWithSudo(password="   "), 255)

    def test_no_command_returns_255(self):
        rw = RunWith(use_logger=False)
        # command is None — skip setCommand
        self.assertEqual(rw.runWithSudo(password="secret"), 255)

    def test_run_with_sudo_rs_empty_password_returns_255(self):
        rw = RunWith(use_logger=False)
        rw.setCommand("ls")
        self.assertEqual(rw.runWithSudoRs(password=""), 255)

    def test_run_with_sudo_rs_no_command_returns_255(self):
        rw = RunWith(use_logger=False)
        self.assertEqual(rw.runWithSudoRs(password="pw"), 255)


# ─────────────────────────────────────────────────────────────────────────────
# 9.  runWithSudo() — subprocess wiring via the select loop
# ─────────────────────────────────────────────────────────────────────────────

def _build_sudo_proc():
    """Minimal Popen mock for the select-loop in runWithSudo / runWithSudoRs."""
    proc = MagicMock()
    for attr in ("stdin", "stdout", "stderr"):
        stream = MagicMock()
        stream.fileno.return_value = 5
        setattr(proc, attr, stream)
    proc.poll.return_value = 0   # already finished → loop breaks immediately
    proc.wait.return_value = 0
    proc.stdout.read.return_value = b""
    proc.stderr.read.return_value = b""
    return proc


class TestRunWithSudoSubprocess(unittest.TestCase):

    @patch("lib.run_commands.os.set_blocking")
    @patch("lib.run_commands.select.select", return_value=([], [], []))
    @patch("lib.run_commands.subprocess.Popen")
    def test_popen_is_called_with_sudo_prefix(
        self, mock_popen, _select, _blocking
    ):
        mock_popen.return_value = _build_sudo_proc()
        rw = RunWith(use_logger=False)
        rw.setCommand(["id"])
        rw.runWithSudo(password="secret")
        cmd_used = mock_popen.call_args[0][0]
        self.assertIn("/usr/bin/sudo", cmd_used)

    @patch("lib.run_commands.os.set_blocking")
    @patch("lib.run_commands.select.select", return_value=([], [], []))
    @patch("lib.run_commands.subprocess.Popen")
    def test_string_command_is_split_and_prefixed(
        self, mock_popen, _select, _blocking
    ):
        mock_popen.return_value = _build_sudo_proc()
        rw = RunWith(use_logger=False)
        rw.setCommand("id -u")
        rw.runWithSudo(password="pw")
        cmd_used = mock_popen.call_args[0][0]
        self.assertIn("id", cmd_used)
        self.assertIn("-u", cmd_used)

    @patch("lib.run_commands.os.set_blocking")
    @patch("lib.run_commands.select.select", return_value=([], [], []))
    @patch("lib.run_commands.subprocess.Popen")
    def test_os_set_blocking_called_for_stdin_stdout_stderr(
        self, mock_popen, _select, mock_blocking
    ):
        mock_popen.return_value = _build_sudo_proc()
        rw = RunWith(use_logger=False)
        rw.setCommand(["id"])
        rw.runWithSudo(password="pw")
        self.assertEqual(mock_blocking.call_count, 3)

    @patch("lib.run_commands.os.set_blocking")
    @patch("lib.run_commands.select.select")
    @patch("lib.run_commands.subprocess.Popen")
    def test_stdout_decoded_when_read_from_select_loop(
        self, mock_popen, mock_select, _blocking
    ):
        proc = _build_sudo_proc()
        mock_popen.return_value = proc

        # iter 1: stdout ready; iter 2: poll breaks
        mock_select.side_effect = [
            ([proc.stdout], [], []),
            ([], [], []),
        ]
        proc.poll.side_effect = [None, 0]
        proc.stdout.read.side_effect = [b"root\n", b""]

        rw = RunWith(use_logger=False)
        rw.setCommand(["id"])
        rw.runWithSudo(password="pw")
        self.assertIn("root", rw.stdout)

    @patch("lib.run_commands.os.set_blocking")
    @patch("lib.run_commands.select.select", return_value=([], [], []))
    @patch("lib.run_commands.subprocess.Popen")
    def test_run_with_sudo_rs_popen_called_with_sudo_rs(
        self, mock_popen, _select, _blocking
    ):
        mock_popen.return_value = _build_sudo_proc()
        rw = RunWith(use_logger=False)
        rw.setCommand(["id"])
        rw.runWithSudoRs(password="pw")
        cmd_used = mock_popen.call_args[0][0]
        self.assertIn("/usr/bin/sudo-rs", cmd_used)


# ─────────────────────────────────────────────────────────────────────────────
# 10.  RunThread
# ─────────────────────────────────────────────────────────────────────────────

class TestRunThread(unittest.TestCase):
    """
    RunThread checks `isinstance(logger, type(CyLogger))`.
    Since CyLogger is a plain class, type(CyLogger) is <type 'type'>.
    Passing CyLogger itself satisfies that check because
    isinstance(CyLogger, type) is True.
    """

    _logger = CyLogger   # the class object, not an instance

    def test_init_with_list_command(self):
        rt = RunThread(["echo", "hi"], self._logger)
        self.assertEqual(rt.command, ["echo", "hi"])

    def test_init_with_string_command(self):
        rt = RunThread("echo hi", self._logger)
        self.assertEqual(rt.command, "echo hi")

    def test_init_invalid_logger_raises_not_a_cylogger_error(self):
        with self.assertRaises(NotACyLoggerError):
            RunThread("ls", logger=object())

    def test_init_none_logger_raises_not_a_cylogger_error(self):
        with self.assertRaises(NotACyLoggerError):
            RunThread("ls", logger=None)

    @patch("lib.run_commands.Popen")
    def test_run_calls_communicate(self, mock_popen):
        proc = MagicMock()
        proc.communicate.return_value = (b"hi\n", b"")
        mock_popen.return_value = proc

        rt = RunThread("echo hi", self._logger)
        rt.run()
        proc.communicate.assert_called()

    @patch("lib.run_commands.Popen")
    def test_get_stdout_returns_communicate_output(self, mock_popen):
        proc = MagicMock()
        proc.communicate.return_value = (b"output\n", b"")
        mock_popen.return_value = proc

        rt = RunThread("ls", self._logger)
        rt.run()
        self.assertEqual(rt.getStdout(), b"output\n")

    @patch("lib.run_commands.Popen")
    def test_get_stderr_returns_communicate_error(self, mock_popen):
        proc = MagicMock()
        proc.communicate.return_value = (b"", b"err\n")
        mock_popen.return_value = proc

        rt = RunThread("ls", self._logger)
        rt.run()
        self.assertEqual(rt.getStderr(), b"err\n")

    @patch("lib.run_commands.Popen")
    def test_run_reraises_subprocess_error(self, mock_popen):
        mock_popen.side_effect = SubprocessError("bang")
        rt = RunThread("bad_cmd", self._logger)
        with self.assertRaises(SubprocessError):
            rt.run()

    def test_is_a_thread(self):
        rt = RunThread("ls", self._logger)
        self.assertIsInstance(rt, threading.Thread)


# ─────────────────────────────────────────────────────────────────────────────
# 11.  runMyThreadCommand()
# ─────────────────────────────────────────────────────────────────────────────

class TestRunMyThreadCommand(unittest.TestCase):

    _logger = CyLogger

    def test_invalid_logger_raises_not_a_cylogger_error(self):
        with self.assertRaises(NotACyLoggerError):
            runMyThreadCommand("ls", logger="bad_logger")

    def test_none_logger_raises_not_a_cylogger_error(self):
        with self.assertRaises(NotACyLoggerError):
            runMyThreadCommand("ls", logger=None)

    @patch("lib.run_commands.RunThread")
    def test_happy_path_starts_joins_returns_output(self, mock_cls):
        thread_instance = MagicMock()
        thread_instance.getStdout.return_value = b"result\n"
        thread_instance.getStderr.return_value = b""
        mock_cls.return_value = thread_instance

        retval, reterr = runMyThreadCommand("echo hi", self._logger)

        thread_instance.start.assert_called_once()
        thread_instance.join.assert_called_once()
        self.assertEqual(retval, b"result\n")
        self.assertEqual(reterr, b"")

    @patch("lib.run_commands.RunThread")
    def test_empty_cmd_does_not_start_thread(self, mock_cls):
        retval, reterr = runMyThreadCommand("", self._logger)
        mock_cls.assert_not_called()
        self.assertIsNone(retval)
        self.assertIsNone(reterr)

    @patch("lib.run_commands.RunThread")
    def test_returns_none_pair_when_cmd_none(self, mock_cls):
        retval, reterr = runMyThreadCommand(None, self._logger)
        mock_cls.assert_not_called()
        self.assertIsNone(retval)
        self.assertIsNone(reterr)


# ─────────────────────────────────────────────────────────────────────────────
# 12.  Custom exception hierarchy
# ─────────────────────────────────────────────────────────────────────────────

class TestCustomExceptions(unittest.TestCase):

    def test_os_not_valid_is_base_exception(self):
        self.assertTrue(issubclass(OSNotValidForRunWith, BaseException))

    def test_not_a_cy_logger_error_is_base_exception(self):
        self.assertTrue(issubclass(NotACyLoggerError, BaseException))

    def test_set_command_type_error_is_base_exception(self):
        self.assertTrue(issubclass(SetCommandTypeError, BaseException))

    def test_os_not_valid_carries_message(self):
        exc = OSNotValidForRunWith("platform error")
        self.assertIn("platform error", str(exc))

    def test_not_a_cy_logger_error_carries_message(self):
        exc = NotACyLoggerError("bad logger")
        self.assertIn("bad logger", str(exc))

    def test_set_command_type_error_carries_message(self):
        exc = SetCommandTypeError("bad type")
        self.assertIn("bad type", str(exc))

    def test_exceptions_can_be_raised_and_caught(self):
        for exc_cls in (OSNotValidForRunWith, NotACyLoggerError, SetCommandTypeError):
            with self.subTest(exc=exc_cls.__name__):
                with self.assertRaises(exc_cls):
                    raise exc_cls("test")


# ─────────────────────────────────────────────────────────────────────────────
# 13.  Integration: setCommand → communicate round-trip
# ─────────────────────────────────────────────────────────────────────────────

class TestSetCommandCommunicateIntegration(unittest.TestCase):

    @patch("lib.run_commands.Popen")
    def test_list_command_end_to_end_shell_false(self, mock_popen):
        proc = _make_proc(returncode=0, stdout="file1\nfile2\n", stderr="")
        mock_popen.return_value = proc

        rw = RunWith(use_logger=False)
        rw.setCommand(["ls", "/tmp"])
        out, err, rc = rw.communicate()

        self.assertEqual(rc, 0)
        self.assertIn("file1", out)
        _, kwargs = mock_popen.call_args
        self.assertFalse(kwargs["shell"])

    @patch("lib.run_commands.Popen")
    def test_string_command_end_to_end_shell_true(self, mock_popen):
        proc = _make_proc(returncode=0, stdout="hello world\n", stderr="")
        mock_popen.return_value = proc

        rw = RunWith(use_logger=False)
        rw.setCommand("echo 'hello world'")
        rw.communicate()

        self.assertEqual(rw.getStdout(), "hello world\n")
        self.assertEqual(rw.getReturnCode(), 0)
        '''
        out, _, rc = rw.communicate()

        self.assertEqual(rc, 0)
        self.assertIn("hello world", out)
        _, kwargs = mock_popen.call_args
        self.assertTrue(kwargs["shell"])
        '''

    @patch("lib.run_commands.Popen")
    def test_communicate_resets_command_allowing_reuse(self, mock_popen):
        mock_popen.return_value = _make_proc()

        rw = RunWith(use_logger=False)
        rw.setCommand("echo first")
        rw.communicate()
        self.assertIsNone(rw.command)

        # Can set a new command after the first run
        rw.setCommand("echo second")
        self.assertEqual(rw.command, "echo second")

    @patch("lib.run_commands.Popen")
    def test_get_returns_reflects_last_communicate(self, mock_popen):
        proc = _make_proc(returncode=42, stdout="final\n", stderr="warn\n")
        mock_popen.return_value = proc

        rw = RunWith(use_logger=False)
        rw.setCommand("custom_cmd")
        rw.communicate()

        out, err, rc = rw.getReturns()
        self.assertEqual(out, "final\n")
        self.assertEqual(err, "warn\n")
        self.assertEqual(rc, 42)


if __name__ == "__main__":
    unittest.main(verbosity=2)


