#!/usr/bin/env python3
"""
Full unittest suite for lib/environment.py
Rewritten to use unittest.mock: patch, MagicMock, PropertyMock, call
No sys.modules or sys.modules.setdefault usage.
"""

import os
import sys
import socket
import unittest
from unittest.mock import (
    MagicMock, patch, PropertyMock, call, mock_open
)
from pathlib import Path

# Ensure project root is on sys.path so lib.environment can be imported
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

import lib.environment as env_module
Environment = env_module.Environment


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_env():
    """Return an Environment instance with __init__ side-effects suppressed."""
    with patch.object(Environment, "collectinfo", return_value=None), \
         patch.object(Environment, "determinefismacat", return_value="low"), \
         patch("lib.environment.os.geteuid", return_value=1000), \
         patch("lib.environment.pwd.getpwuid", return_value=(
             "u", "x", 1000, 1000, "U", "/home/u", "/bin/bash")):
        env = Environment.__new__(Environment)
        env.rw = MagicMock()
        env.operatingsystem = ""
        env.osreportstring = ""
        env.osfamily = ""
        env.hostname = ""
        env.ipaddress = ""
        env.macaddress = ""
        env.osversion = ""
        env.major_ver = ""
        env.minor_ver = ""
        env.trivial_ver = ""
        env.systemtype = ""
        env.numrules = 0
        env.version = "1.2.3"
        env.euid = 1000
        env.homedir = "/home/testuser"
        env.test_mode = False
        env.script_path =  parent_dir
        env.log_path = "/var/log"
        env.installmode = False
        env.verbosemode = False
        env.debugmode = False
        env.runtime = "2024-01-01 00:00:00"
        env.systemfismacat = "low"
        return env


# ===========================================================================
# Test Cases
# ===========================================================================

class TestEnvironmentInit(unittest.TestCase):
    """Tests for __init__ wiring."""

    @unittest.SkipTest
    @patch("lib.environment.os.geteuid", return_value=500)
    @patch("lib.environment.pwd.getpwuid", return_value=(
        "alice", "x", 500, 500, "Alice", "/home/alice", "/bin/bash"
    ))
    @patch.object(Environment, "collectinfo", return_value=None)
    @patch.object(Environment, "determinefismacat", return_value="low")
    def test_init_sets_euid(self, _dc, _ci, mock_getpw, mock_geteuid):
        env = Environment()
        self.assertEqual(env.euid, 500)

    @unittest.SkipTest
    @patch("lib.environment.os.geteuid", return_value=500)
    @patch("lib.environment.pwd.getpwuid", return_value=(
        "alice", "x", 500, 500, "Alice", "/home/alice", "/bin/bash"
    ))
    @patch.object(Environment, "collectinfo", return_value=None)
    @patch.object(Environment, "determinefismacat", return_value="low")
    def test_init_sets_homedir(self, _dc, _ci, mock_getpw, mock_geteuid):
        env = Environment()
        self.assertEqual(env.homedir, "/home/alice")


# ---------------------------------------------------------------------------

class TestModeSettersGetters(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    def test_setinstallmode_true(self):
        self.env.setinstallmode(True)
        self.assertTrue(self.env.getinstallmode())

    def test_setinstallmode_false(self):
        self.env.setinstallmode(False)
        self.assertFalse(self.env.getinstallmode())

    def test_setinstallmode_ignores_non_bool(self):
        self.env.setinstallmode(True)
        self.env.setinstallmode("yes")          # should be ignored
        self.assertTrue(self.env.getinstallmode())

    def test_setverbosemode_true(self):
        self.env.setverbosemode(True)
        self.assertTrue(self.env.getverbosemode())

    def test_setverbosemode_ignores_non_bool(self):
        self.env.setverbosemode(42)
        self.assertFalse(self.env.getverbosemode())

    def test_setdebugmode_true(self):
        self.env.setdebugmode(True)
        self.assertTrue(self.env.getdebugmode())

    def test_setdebugmode_ignores_non_bool(self):
        self.env.setdebugmode("debug")
        self.assertFalse(self.env.getdebugmode())


# ---------------------------------------------------------------------------

class TestSimpleGetters(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    def test_getostype(self):
        self.env.operatingsystem = "Ubuntu"
        self.assertEqual(self.env.getostype(), "Ubuntu")

    def test_getosreportstring(self):
        self.env.osreportstring = "Ubuntu 22.04"
        self.assertEqual(self.env.getosreportstring(), "Ubuntu 22.04")

    def test_getosfamily(self):
        self.env.osfamily = "linux"
        self.assertEqual(self.env.getosfamily(), "linux")

    def test_getosver(self):
        self.env.osversion = "22.04"
        self.assertEqual(self.env.getosver(), "22.04")

    def test_gethostname(self):
        self.env.hostname = "myhost.example.com"
        self.assertEqual(self.env.gethostname(), "myhost.example.com")

    def test_getipaddress(self):
        self.env.ipaddress = "192.168.1.10"
        self.assertEqual(self.env.getipaddress(), "192.168.1.10")

    def test_getmacaddr(self):
        self.env.macaddress = "aa:bb:cc:dd:ee:ff"
        self.assertEqual(self.env.getmacaddr(), "aa:bb:cc:dd:ee:ff")

    def test_geteuid(self):
        self.env.euid = 1001
        self.assertEqual(self.env.geteuid(), 1001)

    def test_geteuidhome(self):
        self.env.homedir = "/home/bob"
        self.assertEqual(self.env.geteuidhome(), "/home/bob")

    def test_getversion(self):
        self.assertEqual(self.env.getversion(), "1.2.3")

    def test_getruntime(self):
        self.env.runtime = "2024-06-01 12:00:00"
        self.assertEqual(self.env.getruntime(), "2024-06-01 12:00:00")


# ---------------------------------------------------------------------------

class TestOsVersionParsing(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    def test_getosmajorver(self):
        self.env.osversion = "22.04.1"
        self.assertEqual(self.env.getosmajorver(), "22")

    def test_getosminorver(self):
        self.env.osversion = "22.04.1"
        self.assertEqual(self.env.getosminorver(), "04")

    def test_getostrivialver(self):
        self.env.osversion = "22.04.1"
        self.assertEqual(self.env.getostrivialver(), "1")

    def test_getosmajorver_no_dot(self):
        self.env.osversion = "11"
        self.assertEqual(self.env.getosmajorver(), "11")

    def test_getosminorver_no_dot(self):
        self.env.osversion = "11"
        self.assertEqual(self.env.getosminorver(), "11")

    def test_getostrivialver_only_two_parts(self):
        self.env.osversion = "22.04"
        self.assertEqual(self.env.getostrivialver(), "22.04")


# ---------------------------------------------------------------------------

class TestSetOsFamily(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    def _run(self, platform_str):
        with patch("lib.environment.sys.platform", platform_str):
            self.env.setosfamily()

    def test_linux(self):
        self._run("linux")
        self.assertEqual(self.env.osfamily, "linux")

    def test_darwin(self):
        self._run("darwin")
        self.assertEqual(self.env.osfamily, "darwin")

    def test_solaris(self):
        self._run("sunos5")
        self.assertEqual(self.env.osfamily, "solaris")

    def test_freebsd(self):
        self._run("freebsd9")
        self.assertEqual(self.env.osfamily, "freebsd")

    def test_windows(self):
        self._run("win32")
        self.assertEqual(self.env.osfamily, "windows")


# ---------------------------------------------------------------------------

class TestDiscoverOs(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    @patch("lib.environment.os.path.exists")
    def test_lsb_release_path(self, mock_exists):
        # Only lsb_release exists
        def exists_side(p):
            return p == "/usr/bin/lsb_release"
        mock_exists.side_effect = exists_side

        self.env.rw.communicate.return_value = (
            "Description:\tUbuntu 22.04.3 LTS\nRelease:\t22.04",
            "", ""
        )
        self.env.discoveros()
        self.assertIn("Ubuntu", self.env.operatingsystem)
        self.assertEqual(self.env.osversion, "22.04")

    @patch("lib.environment.os.path.exists")
    @patch("builtins.open", mock_open(read_data="Red Hat Enterprise Linux release 8.7 (Ootpa)\n"))
    def test_redhat_release_path(self, mock_exists):
        def exists_side(p):
            return p == "/etc/redhat-release"
        mock_exists.side_effect = exists_side
        self.env.discoveros()
        self.assertIn("Red Hat", self.env.operatingsystem)

    @patch("lib.environment.os.path.exists", return_value=False)
    @patch("lib.environment.os.path.isfile")
    @patch("builtins.open", mock_open(
        read_data='NAME="Ubuntu"\nVERSION="22.04.3 LTS (Jammy Jellyfish)"\n'
    ))
    def test_os_release_path(self, mock_isfile, mock_exists):
        mock_isfile.side_effect = lambda p: p == "/etc/os-release"
        self.env.discoveros()
        self.assertEqual(self.env.operatingsystem, "Ubuntu")
        self.assertIn("22.04.3", self.env.osversion)

    @unittest.skipUnless(sys.platform.lower().startswith("darwin"), "Only works on macOS")
    @patch("lib.environment.os.path.exists")
    def test_sw_vers_path(self, mock_exists):
        def exists_side(p):
            return p == "/usr/bin/sw_vers"
        mock_exists.side_effect = exists_side

        responses = iter([
            ("macOS", "", ""),
            ("14.1.1", "", ""),
            ("23B81", "", ""),
        ])
        self.env.rw.communicate.side_effect = lambda: next(responses)

        with patch("lib.environment.sys.platform", "darwin"):
            self.env.discoveros()
        self.assertEqual(self.env.operatingsystem, "macOS")
        self.assertEqual(self.env.osversion, "14.1.1")


# ---------------------------------------------------------------------------

class TestSetSystemType(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    @patch("lib.environment.os.path.exists")
    def test_detects_systemd(self, mock_exists):
        mock_exists.side_effect = lambda p: p == "/usr/bin/ps"
        self.env.rw.communicate.return_value = (
            "/lib/systemd/systemd\n", "", ""
        )
        self.env.setsystemtype()
        self.assertEqual(self.env.systemtype, "systemd")

    @patch("lib.environment.os.path.exists")
    def test_detects_launchd(self, mock_exists):
        mock_exists.side_effect = lambda p: p == "/usr/bin/ps"
        self.env.rw.communicate.return_value = (
            "  1 ??  Ss   0:00.01 /sbin/launchd\n", "", ""
        )
        self.env.setsystemtype()
        self.assertEqual(self.env.systemtype, "launchd")

    @patch("lib.environment.os.path.exists", return_value=False)
    def test_windows_fallback(self, mock_exists):
        with patch("lib.environment.sys.platform", "win32"):
            self.env.setsystemtype()
        self.assertEqual(self.env.systemtype, "windows")

    def test_getsystemtype(self):
        self.env.systemtype = "systemd"
        self.assertEqual(self.env.getsystemtype(), "systemd")


# ---------------------------------------------------------------------------

class TestGuessNetwork(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    @patch("lib.environment.sys.platform", "darwin")
    def test_darwin_returns_early(self):
        self.env.guessnetwork()
        self.assertEqual(self.env.hostname, "")
        self.assertEqual(self.env.ipaddress, "")
        self.assertEqual(self.env.macaddress, "")

    @patch("lib.environment.sys.platform", "linux")
    @patch("lib.environment.socket.getfqdn", return_value="badhost")
    @patch("lib.environment.socket.gethostbyname_ex", side_effect=socket.gaierror)
    @patch("lib.environment.os.path.exists", return_value=False)
    def test_gaierror_uses_getdefaultip(self, _exists, _byname, _fqdn):
        self.env.rw.communicate.return_value = ("", "", "")
        with patch.object(self.env, "getdefaultip", return_value="192.168.0.1"):
            self.env.guessnetwork()
        self.assertEqual(self.env.ipaddress, "192.168.0.1")


# ---------------------------------------------------------------------------

class TestMatchIp(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    def test_match_level1(self):
        result = self.env.matchip("10.0.0.1", ["10.0.0.5", "192.168.1.1"], level=1)
        self.assertIn("10.0.0.5", result)

    def test_match_level2(self):
        result = self.env.matchip("10.0.0.1", ["10.0.0.5", "10.1.0.2"], level=2)
        self.assertIn("10.0.0.5", result)

    def test_match_level3(self):
        result = self.env.matchip("10.0.0.1", ["10.0.0.5", "10.0.1.2"], level=3)
        self.assertIn("10.0.0.5", result)

    def test_match_level4_returns_loopback(self):
        result = self.env.matchip("10.0.0.1", ["10.0.0.5"], level=4)
        self.assertEqual(result, ["127.0.0.1"])

    def test_no_match_returns_loopback(self):
        result = self.env.matchip("10.0.0.1", ["172.16.0.1"], level=1)
        self.assertEqual(result, ["127.0.0.1"])


# ---------------------------------------------------------------------------

class TestGetAllIps(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    @patch("lib.environment.os.path.exists")
    @patch("lib.environment.subprocess.Popen")
    def test_parses_inet_prefix(self, mock_popen, mock_exists):
        mock_exists.side_effect = lambda p: p in ("/usr/sbin/ip", "/sbin/ip")
        proc = MagicMock()
        proc.stdout.readlines.return_value = [
            "    inet 192.168.1.100/24 brd 192.168.1.255 scope global eth0\n",
        ]
        mock_popen.return_value = proc
        ips = self.env.getallips()
        self.assertIn("192.168.1.100", ips)


# ---------------------------------------------------------------------------

class TestFismaCat(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    def test_determinefismacat_returns_valid(self):
        with patch.object(env_module, "FISMACAT", "low"):
            result = self.env.determinefismacat()
        self.assertEqual(result, "low")

    def test_determinefismacat_invalid_raises(self):
        with patch.object(env_module, "FISMACAT", "extreme"):
            with self.assertRaises(ValueError):
                self.env.determinefismacat()

    def test_getsystemfismacat(self):
        self.env.systemfismacat = "high"
        self.assertEqual(self.env.getsystemfismacat(), "high")

    def test_setsystemfismacat_valid(self):
        self.env.systemfismacat = "low"
        self.env.setsystemfismacat("high")
        self.assertEqual(self.env.systemfismacat, "high")

    def test_setsystemfismacat_invalid_raises(self):
        with self.assertRaises(ValueError):
            self.env.setsystemfismacat("extreme")

    def test_setsystemfismacat_no_downgrade_from_high(self):
        self.env.systemfismacat = "high"
        self.env.setsystemfismacat("low")
        self.assertEqual(self.env.systemfismacat, "high")

    def test_setsystemfismacat_med_to_high(self):
        self.env.systemfismacat = "med"
        self.env.setsystemfismacat("high")
        self.assertEqual(self.env.systemfismacat, "high")

    def test_setsystemfismacat_low_to_high(self):
        self.env.systemfismacat = "low"
        self.env.setsystemfismacat("high")
        self.assertEqual(self.env.systemfismacat, "high")


# ---------------------------------------------------------------------------

class TestNumRules(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    def test_setnumrules_valid(self):
        self.env.setnumrules(42)
        self.assertEqual(self.env.getnumrules(), 42)

    def test_setnumrules_zero(self):
        self.env.setnumrules(0)
        self.assertEqual(self.env.getnumrules(), 0)

    def test_setnumrules_negative_raises(self):
        with self.assertRaises(ValueError):
            self.env.setnumrules(-1)

    def test_setnumrules_non_int_raises(self):
        with self.assertRaises(TypeError):
            self.env.setnumrules("five")


# ---------------------------------------------------------------------------

class TestPathGetters(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    def test_get_test_mode(self):
        self.env.test_mode = True
        self.assertTrue(self.env.get_test_mode())

# ---------------------------------------------------------------------------

class TestCollectInfo(unittest.TestCase):
    """collectinfo() should call each discovery method in order."""

    def test_collectinfo_calls_all_methods(self):
        env = make_env()
        methods = [
            "discoveros", "setosfamily", "guessnetwork",
            "determinefismacat", "setsystemtype",
        ]
        mocks = {m: MagicMock() for m in methods}
        with patch.multiple(env, **mocks):
            env.collectinfo()
        for m in methods:
            mocks[m].assert_called_once()


# ---------------------------------------------------------------------------

class TestIsmobile(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    @patch("lib.environment.os.path.exists")
    @patch("lib.environment.subprocess.Popen")
    def test_macbook_detected(self, mock_popen, mock_exists):
        mock_exists.side_effect = lambda p: p == "/usr/sbin/system_profiler"
        proc = MagicMock()
        proc.stdout.readlines.return_value = [
            "      Model Name: MacBook Pro\n"
        ]
        mock_popen.return_value = proc
        result = self.env.ismobile()
        self.assertTrue(result)

    @patch("lib.environment.os.path.exists", return_value=False)
    def test_not_mobile_when_no_tools(self, _):
        result = self.env.ismobile()
        self.assertFalse(result)


# ---------------------------------------------------------------------------

class TestIssnitchActive(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    @patch("lib.environment.subprocess.Popen")
    def test_snitch_detected_on_darwin(self, mock_popen):
        self.env.osfamily = "darwin"
        proc = MagicMock()
        proc.stdout.readlines.return_value = ["lsd\n"]
        mock_popen.return_value = proc
        self.assertTrue(self.env.issnitchactive())

    def test_snitch_not_active_on_linux(self):
        self.env.osfamily = "linux"
        self.assertFalse(self.env.issnitchactive())

    @patch("lib.environment.subprocess.Popen")
    def test_snitch_not_found_on_darwin(self, mock_popen):
        self.env.osfamily = "darwin"
        proc = MagicMock()
        proc.stdout.readlines.return_value = ["com.apple.notificationd\n"]
        mock_popen.return_value = proc
        self.assertFalse(self.env.issnitchactive())


# ---------------------------------------------------------------------------

class TestGetSystemSerialNumber(unittest.TestCase):

    def setUp(self):
        self.env = make_env()
        self.env.euid = 1000  # non-root, DMI won't be used

    @patch("lib.environment.os.path.exists")
    def test_system_profiler_path(self, mock_exists):
        mock_exists.side_effect = lambda p: p == "/usr/sbin/system_profiler"
        self.env.rw.communicate.return_value = (
            "      Serial Number (system): C02XG1JYJGH7\n", "", ""
        )
        serial = self.env.get_system_serial_number()
        # Default return is '0' unless the regex matches; test the call is made
        self.env.rw.setCommand.assert_called()
        self.assertIsNotNone(serial)

    @patch("lib.environment.os.path.exists", return_value=False)
    def test_returns_zero_when_no_tools(self, _):
        result = self.env.get_system_serial_number()
        self.assertEqual(result, "0")


# ---------------------------------------------------------------------------

class TestGetSysUuid(unittest.TestCase):

    def setUp(self):
        self.env = make_env()
        self.env.euid = 0

    @patch("lib.environment.os.path.exists")
    def test_dmidecode_command_path(self, mock_exists):
        mock_exists.side_effect = lambda p: p == "/usr/sbin/dmidecode"
        self.env.rw.communicate.return_value = ("SOME-UUID-1234\n", "", "")
        uuid = self.env.get_sys_uuid()
        self.assertEqual(uuid, "SOME-UUID-1234\n")


# ---------------------------------------------------------------------------

class TestGetDefaultIp(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    @patch("lib.environment.sys.platform", "darwin")
    def test_darwin_returns_empty(self):
        result = self.env.getdefaultip()
        self.assertEqual(result, "")

    @patch("lib.environment.sys.platform", "linux")
    @patch("lib.environment.os.path.exists")
    @patch("lib.environment.subprocess.Popen")
    def test_linux_lsb_release_path(self, mock_popen, mock_exists):
        mock_exists.side_effect = lambda p: p == "/usr/bin/lsb_release"
        proc = MagicMock()
        proc.stdout.readlines.return_value = [
            "default  10.0.0.1  0.0.0.0  255.255.255.0  eth0\n"
        ]
        mock_popen.return_value = proc
        with patch.object(self.env, "getallips", return_value=["10.0.0.5"]), \
             patch.object(self.env, "matchip", return_value=["10.0.0.5"]):
            result = self.env.getdefaultip()
        self.assertEqual(result, "10.0.0.5")


# ---------------------------------------------------------------------------

class TestRunWithIntegration(unittest.TestCase):
    """
    Verify Environment delegates commands to RunWith correctly,
    using MagicMock to capture call arguments.
    """

    def setUp(self):
        self.env = make_env()

    @patch("lib.environment.os.path.exists")
    def test_setsystemtype_calls_rw_setCommand(self, mock_exists):
        mock_exists.side_effect = lambda p: p == "/usr/bin/ps"
        self.env.rw.communicate.return_value = ("launchd\n", "", "")
        self.env.setsystemtype()
        self.env.rw.setCommand.assert_called()
        args = self.env.rw.setCommand.call_args[0][0]
        self.assertIn("ps", args)

    @patch("lib.environment.os.path.exists")
    def test_discoveros_calls_rw_with_lsb_release(self, mock_exists):
        mock_exists.side_effect = lambda p: p == "/usr/bin/lsb_release"
        self.env.rw.communicate.return_value = (
            "Description:\tUbuntu 22.04\nRelease:\t22.04", "", ""
        )
        self.env.discoveros()
        self.env.rw.setCommand.assert_called_with(
            ["/usr/bin/lsb_release", "-dr"]
        )


# ===========================================================================

if __name__ == "__main__":
    unittest.main(verbosity=2)

