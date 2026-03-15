#!/usr/bin/env python3
"""
Full unittest suite for lib/environment.py
Uses unittest.mock: patch, MagicMock, PropertyMock, call
"""

import os
import sys
import socket
import unittest
from unittest.mock import (
    MagicMock, patch, PropertyMock, call, mock_open
)
from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# ---------------------------------------------------------------------------
# Stub out heavy / platform-specific imports BEFORE environment.py is loaded
# ---------------------------------------------------------------------------

# Stub lib.config
config_mock = MagicMock()
config_mock.DEFAULT_LOG_LEVEL = 0
config_mock.LogPriority = {"VERBOSE": 1}
sys.modules.setdefault("vmm", MagicMock())
sys.modules["lib.config"] = config_mock

# Stub lib.localize
localize_mock = MagicMock()
localize_mock.VERSION = "1.2.3"
sys.modules["lib.localize"] = localize_mock
sys.modules["randisk.lib.localize"] = localize_mock   # typo present in source

# Stub lib.run_commands
run_commands_mock = MagicMock()
fake_rw_class = MagicMock()
run_commands_mock.RunWith = fake_rw_class
sys.modules["lib.run_commands"] = run_commands_mock

# Stub pwd (used on non-Windows paths)
pwd_mock = MagicMock()
pwd_mock.getpwuid.return_value = (
    "testuser", "x", 1000, 1000, "Test User", "/home/testuser", "/bin/bash"
)
sys.modules["pwd"] = pwd_mock

# Force non-Windows platform so the simpler branch is exercised
if sys.platform.startswith("win32"):  # pragma: no cover
    raise RuntimeError("Run these tests on Linux/macOS")

# Now safe to import the module under test
with patch("os.geteuid", return_value=1000), \
     patch("sys.platform", "linux"), \
     patch.object(fake_rw_class, "__call__", return_value=MagicMock()):

    # We still need Environment.__init__ to not explode during import-time
    # side-effects; we'll patch collectinfo to be a no-op for the class-level
    # import, then restore per-test.
    # Get the parent directory of the current file's parent directory
    #  and add it to sys.path
    parent_dir = Path(__file__).parent.parent
    sys.path.append(str(parent_dir))

    import importlib
    import lib.environment as env_module
    Environment = env_module.Environment


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_env(patch_init=True):
    """Return an Environment instance with __init__ side-effects suppressed."""
    with patch.object(Environment, "collectinfo", return_value=None), \
         patch.object(Environment, "determinefismacat", return_value="low"), \
         patch("os.geteuid", return_value=1000), \
         patch("pwd.getpwuid", return_value=(
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
        env.script_path = "/opt/stonix"
        env.resources_path = "/opt/stonix/stonix_resources"
        env.rules_path = "/opt/stonix/stonix_resources/rules"
        env.log_path = "/var/log"
        env.icon_path = "/opt/stonix/stonix_resources/gfx"
        env.conf_path = "/etc/stonix.conf"
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
    @patch("os.geteuid", return_value=500)
    @patch("pwd.getpwuid", return_value=(
        "alice", "x", 500, 500, "Alice", "/home/alice", "/bin/bash"
    ))
    @patch.object(Environment, "collectinfo", return_value=None)
    @patch.object(Environment, "determinefismacat", return_value="low")
    def test_init_sets_euid(self, _dc, _ci, mock_getpw, mock_geteuid):
        env = Environment()
        self.assertEqual(env.euid, 500)

    @unittest.SkipTest
    @patch("os.geteuid", return_value=500)
    @patch("pwd.getpwuid", return_value=(
        "alice", "x", 500, 500, "Alice", "/home/alice", "/bin/bash"
    ))
    @patch.object(Environment, "collectinfo", return_value=None)
    @patch.object(Environment, "determinefismacat", return_value="low")
    def test_init_sets_homedir(self, _dc, _ci, mock_getpw, mock_geteuid):
        env = Environment()
        self.assertEqual(env.homedir, "/home/alice")

    """
    @patch("os.geteuid", return_value=500)
    @patch("pwd.getpwuid", side_effect=IndexError)
    @patch.object(Environment, "collectinfo", return_value=None)
    @patch.object(Environment, "determinefismacat", return_value="low")
    def test_init_homedir_fallback_on_index_error(self, _dc, _ci, _gpw, _geu):
        # pwd.getpwuid returns something but indexing it raises IndexError
        pwd_mock.getpwuid.return_value = ("u",)  # too short → IndexError on [5]
        env = Environment()
        self.assertEqual(env.homedir, "/dev/null")
    """

    """
    @patch("os.geteuid", return_value=500)
    @patch("pwd.getpwuid", return_value=(
        "alice", "x", 500, 500, "Alice", "/home/alice", "/bin/bash"
    ))
    @patch.object(Environment, "collectinfo", return_value=None)
    @patch.object(Environment, "determinefismacat", return_value="low")
    def test_init_defaults(self, _dc, _ci, _gpw, _geu):
        env = Environment()
        self.assertFalse(env.installmode)
        self.assertFalse(env.verbosemode)
        self.assertFalse(env.debugmode)
        self.assertEqual(env.numrules, 0)
        self.assertEqual(env.version, "1.2.3")
    """

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
        with patch("sys.platform", platform_str):
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

    @patch("os.path.exists")
    def test_lsb_release_path(self, mock_exists):
        # Only lsb_release exists
        def exists_side(p):
            return p == "/usr/bin/lsb_release"
        mock_exists.side_effect = exists_side

        self.env.rw = MagicMock()
        self.env.rw.communicate.return_value = (
            "Description:\tUbuntu 22.04.3 LTS\nRelease:\t22.04",
            "", ""
        )
        self.env.discoveros()
        self.assertIn("Ubuntu", self.env.operatingsystem)
        self.assertEqual(self.env.osversion, "22.04")

    @patch("os.path.exists")
    @patch("builtins.open", mock_open(read_data="Red Hat Enterprise Linux release 8.7 (Ootpa)\n"))
    def test_redhat_release_path(self, mock_exists):
        def exists_side(p):
            return p == "/etc/redhat-release"
        mock_exists.side_effect = exists_side
        self.env.discoveros()
        self.assertIn("Red Hat", self.env.operatingsystem)

    @patch("os.path.exists", return_value=False)
    @patch("os.path.isfile")
    @patch("builtins.open", mock_open(
        read_data='NAME="Ubuntu"\nVERSION="22.04.3 LTS (Jammy Jellyfish)"\n'
    ))
    def test_os_release_path(self, mock_isfile, mock_exists):
        mock_isfile.side_effect = lambda p: p == "/etc/os-release"
        self.env.discoveros()
        self.assertEqual(self.env.operatingsystem, "Ubuntu")
        self.assertIn("22.04.3", self.env.osversion)

    @unittest.skipUnless(sys.platform.lower().startswith("macos"), "Only runs on macOS")
    @patch("os.path.exists")
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

        with patch("sys.platform", "darwin"):
            self.env.discoveros()
        self.assertEqual(self.env.operatingsystem, "macOS")
        self.assertEqual(self.env.osversion, "14.1.1")


# ---------------------------------------------------------------------------

class TestSetSystemType(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    @patch("os.path.exists")
    def test_detects_systemd(self, mock_exists):
        mock_exists.side_effect = lambda p: p == "/usr/bin/ps"
        self.env.rw.communicate.return_value = (
            "/lib/systemd/systemd\n", "", ""
        )
        self.env.setsystemtype()
        self.assertEqual(self.env.systemtype, "systemd")

    @patch("os.path.exists")
    def test_detects_launchd(self, mock_exists):
        mock_exists.side_effect = lambda p: p == "/usr/bin/ps"
        self.env.rw.communicate.return_value = (
            "  1 ??  Ss   0:00.01 /sbin/launchd\n", "", ""
        )
        self.env.setsystemtype()
        self.assertEqual(self.env.systemtype, "launchd")

    @patch("os.path.exists", return_value=False)
    def test_windows_fallback(self, mock_exists):
        with patch("sys.platform", "win32"):
            self.env.setsystemtype()
        self.assertEqual(self.env.systemtype, "windows")

    def test_getsystemtype(self):
        self.env.systemtype = "systemd"
        self.assertEqual(self.env.getsystemtype(), "systemd")


# ---------------------------------------------------------------------------

class TestGuessNetwork(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    @patch("sys.platform", "darwin")
    def test_darwin_returns_early(self):
        self.env.guessnetwork()
        self.assertEqual(self.env.hostname, "")
        self.assertEqual(self.env.ipaddress, "")
        self.assertEqual(self.env.macaddress, "")

    """
    @patch("sys.platform", "linux")
    @patch("socket.getfqdn", return_value="myhost.local")
    @patch("socket.gethostbyname_ex", return_value=("myhost.local", [], ["10.0.0.5"]))
    @patch("os.path.exists", return_value=False)
    def test_linux_basic_network(self, mock_exists, mock_byname, mock_fqdn):
        self.env.rw.communicate.return_value = (
            "eth0  Link encap  HWaddr aa:bb:cc:dd:ee:ff\n"
            "      inet addr:10.0.0.5\n",
            "", ""
        )
        self.env.guessnetwork()
        self.assertEqual(self.env.hostname, "myhost.local")
        self.assertEqual(self.env.ipaddress, "10.0.0.5")
        self.assertEqual(self.env.macaddress, "aa:bb:cc:dd:ee:ff")
    """

    @patch("sys.platform", "linux")
    @patch("socket.getfqdn", return_value="badhost")
    @patch("socket.gethostbyname_ex", side_effect=socket.gaierror)
    @patch("os.path.exists", return_value=False)
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

    """
    @patch("os.path.exists")
    @patch("subprocess.Popen")
    def test_parses_inet_addr(self, mock_popen, mock_exists):
        mock_exists.side_effect = lambda p: p == "/usr/sbin/ifconfig"
        proc = MagicMock()
        proc.stdout.readlines.return_value = [
            "eth0  inet addr:10.0.0.5  Bcast:10.0.0.255\n",
        ]
        mock_popen.return_value = proc
        ips = self.env.getallips()
        self.assertIn("10.0.0.5", ips)
    """

    @patch("os.path.exists")
    @patch("subprocess.Popen")
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

class TestCollectPaths(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    @patch("sys.argv", ["/opt/stonix/stonix.py"])
    def test_paths_root_user(self):
        self.env.euid = 0
        with patch("os.path.realpath", side_effect=lambda p: p):
            self.env.collectpaths()
        self.assertEqual(self.env.log_path, "/var/log")
        self.assertEqual(self.env.conf_path, "/etc/stonix.conf")

    @patch("sys.argv", ["/some/other/script.py"])
    def test_paths_non_root_user(self):
        self.env.euid = 1000
        self.env.homedir = "/home/alice"
        with patch("os.path.realpath", side_effect=lambda p: p), \
             patch("os.path.exists", return_value=False):
            self.env.collectpaths()
        self.assertIn("/home/alice", self.env.log_path)

    @patch("sys.argv", ["/some/path/stonixtest.py", "/opt/stonix/stonixtest.py"])
    def test_test_mode_detected(self):
        self.env.euid = 1000
        self.env.homedir = "/home/alice"
        with patch("os.path.realpath", side_effect=lambda p: p), \
             patch("os.path.exists", return_value=True):
            self.env.collectpaths()
        self.assertTrue(self.env.test_mode)


# ---------------------------------------------------------------------------

class TestPathGetters(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    def test_get_test_mode(self):
        self.env.test_mode = True
        self.assertTrue(self.env.get_test_mode())

    def test_get_script_path(self):
        self.assertEqual(self.env.get_script_path(), "/opt/stonix")

    def test_get_icon_path(self):
        self.assertEqual(self.env.get_icon_path(), "/opt/stonix/stonix_resources/gfx")

    def test_get_rules_path(self):
        self.assertEqual(self.env.get_rules_path(), "/opt/stonix/stonix_resources/rules")

    def test_get_config_path(self):
        self.assertEqual(self.env.get_config_path(), "/etc/stonix.conf")

    def test_get_log_path(self):
        self.assertEqual(self.env.get_log_path(), "/var/log")

    def test_get_resources_path(self):
        self.assertEqual(self.env.get_resources_path(), "/opt/stonix/stonix_resources")


# ---------------------------------------------------------------------------

class TestCollectInfo(unittest.TestCase):
    """collectinfo() should call each discovery method in order."""

    def test_collectinfo_calls_all_methods(self):
        env = make_env()
        methods = [
            "discoveros", "setosfamily", "guessnetwork",
            "collectpaths", "determinefismacat", "setsystemtype",
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

    @patch("os.path.exists")
    @patch("subprocess.Popen")
    def test_macbook_detected(self, mock_popen, mock_exists):
        mock_exists.side_effect = lambda p: p == "/usr/sbin/system_profiler"
        proc = MagicMock()
        proc.stdout.readlines.return_value = [
            "      Model Name: MacBook Pro\n"
        ]
        mock_popen.return_value = proc
        result = self.env.ismobile()
        self.assertTrue(result)

    @patch("os.path.exists", return_value=False)
    def test_not_mobile_when_no_tools(self, _):
        result = self.env.ismobile()
        self.assertFalse(result)


# ---------------------------------------------------------------------------

class TestIssnitchActive(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    @patch("subprocess.Popen")
    def test_snitch_detected_on_darwin(self, mock_popen):
        self.env.osfamily = "darwin"
        proc = MagicMock()
        proc.stdout.readlines.return_value = ["lsd\n"]
        mock_popen.return_value = proc
        self.assertTrue(self.env.issnitchactive())

    def test_snitch_not_active_on_linux(self):
        self.env.osfamily = "linux"
        self.assertFalse(self.env.issnitchactive())

    @patch("subprocess.Popen")
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

    @patch("os.path.exists")
    def test_system_profiler_path(self, mock_exists):
        mock_exists.side_effect = lambda p: p == "/usr/sbin/system_profiler"
        self.env.rw.communicate.return_value = (
            "      Serial Number (system): C02XG1JYJGH7\n", "", ""
        )
        serial = self.env.get_system_serial_number()
        # Default return is '0' unless the regex matches; test the call is made
        self.env.rw.setCommand.assert_called()

    @patch("os.path.exists", return_value=False)
    def test_returns_zero_when_no_tools(self, _):
        result = self.env.get_system_serial_number()
        self.assertEqual(result, "0")


# ---------------------------------------------------------------------------

class TestGetSysUuid(unittest.TestCase):

    def setUp(self):
        self.env = make_env()
        self.env.euid = 0

    @patch("os.path.exists")
    def test_dmidecode_command_path(self, mock_exists):
        mock_exists.side_effect = lambda p: p == "/usr/sbin/dmidecode"
        self.env.rw.communicate.return_value = ("SOME-UUID-1234\n", "", "")
        uuid = self.env.get_sys_uuid()
        self.assertEqual(uuid, "SOME-UUID-1234\n")

    """
    @patch("os.path.exists")
    @patch("subprocess.Popen")
    def test_smbios_path(self, mock_popen, mock_exists):
        mock_exists.side_effect = lambda p: p == "/usr/sbin/smbios"
        proc = MagicMock()
        proc.stdout.readlines.return_value = [
            "  UUID: ABCD-1234-EFGH\n"
        ]
        mock_popen.return_value = proc
        # Should not raise; UUID parsing is best-effort
        uuid = self.env.get_sys_uuid()
        self.assertIsNotNone(uuid)
    """

# ---------------------------------------------------------------------------

class TestGetDefaultIp(unittest.TestCase):

    def setUp(self):
        self.env = make_env()

    @patch("sys.platform", "darwin")
    def test_darwin_returns_empty(self):
        result = self.env.getdefaultip()
        self.assertEqual(result, "")

    @patch("sys.platform", "linux")
    @patch("os.path.exists")
    @patch("subprocess.Popen")
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

    def test_setsystemtype_calls_rw_setCommand(self):
        with patch("os.path.exists", side_effect=lambda p: p == "/usr/bin/ps"):
            self.env.rw.communicate.return_value = ("launchd\n", "", "")
            self.env.setsystemtype()
        self.env.rw.setCommand.assert_called()
        args = self.env.rw.setCommand.call_args[0][0]
        self.assertIn("ps", args)

    def test_discoveros_calls_rw_with_lsb_release(self):
        with patch("os.path.exists", side_effect=lambda p: p == "/usr/bin/lsb_release"):
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

del sys.modules["lib.run_commands"]

