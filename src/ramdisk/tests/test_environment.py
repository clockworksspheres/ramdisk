#!/usr/bin/env -S python -u
'''
Created on Jul 13, 2011 - stonix project

'''

import os
import re
import sys
import platform
import unittest
import traceback
import tracemalloc
from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# --- Non-native python libraries in this source tree
import lib.environment as environment
from ramdisk import config

if sys.platform.startswith('win32'):
    import win32api
    from lib.windows_utilities import is_windows_process_elevated

else:
    import pwd


class test_environment(unittest.TestCase):

    def setUp(self):
        self.to = environment.Environment()
        self.created = False

    def tearDown(self):
        self.tear_down = True

    def testGetostype(self):
        tracemalloc.start(10)
        validtypes = 'Red Hat Enterprise Linux|AlmaLinux|Rocky Linux|Debian|Ubuntu|CentOS|Fedora|' + \
                     'openSUSE|Mac OS X|macOS|Windows|macOS'
        print('OS Type: ' + str(self.to.getostype()))
        self.assertTrue(re.search(validtypes, self.to.getostype()))

    def testGetosfamily(self):
        tracemalloc.start(10)
        validfamilies = ['linux', 'darwin', 'solaris', 'freebsd', 'windows']
        self.assertTrue(self.to.getosfamily() in validfamilies)

    def testGetosver(self):
        tracemalloc.start(10)
        if not platform.system() == "Windows":
            self.assertTrue(re.search(r'([0-9]{1,3})|(([0-9]{1,3})\.([0-9]{1,3}))',
                                      self.to.getosver()))
        else:
            self.assertTrue(re.search(r'([1-9][0-9])', self.to.getosver()))

    def testGetipaddress(self):
        if sys.platform.startswith('darwin'):
            raise unittest.SkipTest("Doesn't work on macOS")
        tracemalloc.start(10)
        self.assertTrue(re.search(r'(([0-9]{1,3}\.){3}[0-9]{1,3})',
                                  self.to.getipaddress()))

    def testGetmacaddr(self):
        if sys.platform.startswith('darwin'):
            raise unittest.SkipTest("Doesn't work on macOS")
        tracemalloc.start(10)
        self.assertTrue(re.search('(([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2})',
                                  self.to.getmacaddr()))

    def testGeteuid(self):
        if sys.platform.lower().startswith("win32"):
            uid = win32api.GetUserName()
        #    currpwd = os.environ['USERPROFILE']
        else:
             uid = os.geteuid()
        #     currpwd = pwd.getpwuid(self.euid)
        #uid = os.geteuid()
        tracemalloc.start(10)
        self.assertTrue(self.to.geteuid() == uid)

    def testSetGetInstall(self):
        tracemalloc.start(10)
        self.to.setinstallmode(True)
        self.assertTrue(self.to.getinstallmode())
        self.to.setinstallmode(False)
        self.assertFalse(self.to.getinstallmode())

    def testSetGetVerbose(self):
        tracemalloc.start(10)
        self.to.setverbosemode(True)
        self.assertTrue(self.to.getverbosemode())
        self.to.setverbosemode(False)
        self.assertFalse(self.to.getverbosemode())

    def testSetGetDebug(self):
        tracemalloc.start(10)
        self.to.setdebugmode(True)
        self.assertTrue(self.to.getdebugmode())
        self.to.setdebugmode(False)
        self.assertFalse(self.to.getdebugmode())

    def testGetEuidHome(self):
        tracemalloc.start(10)
        if not sys.platform.startswith("win32"):
            self.assertEqual(self.to.geteuidhome(),
                             pwd.getpwuid(os.geteuid())[5])

    def testGetSysSerNo(self):
        tracemalloc.start(10)
        self.assertTrue(self.to.get_system_serial_number())
        print('SysSer: ' + str(self.to.get_system_serial_number()))

    def testGetChassisSerNo(self):
        tracemalloc.start(10)
        self.assertTrue(self.to.get_chassis_serial_number())
        print('Ser: ' + str(self.to.get_chassis_serial_number()))

    def testGetSysMfg(self):
        tracemalloc.start(10)
        mfg = self.to.get_system_manufacturer()
        print('SysMFG: ' + str(mfg))
        self.assertTrue(mfg)

    def testGetChassisMfg(self):
        tracemalloc.start(10)
        mfg = self.to.get_chassis_manfacturer()
        print('MFG: ' + str(mfg))
        self.assertTrue(mfg)

    def testGetSysUUID(self):
        tracemalloc.start(10)
        uuid = self.to.get_sys_uuid()
        print('UUID: ' + str(uuid))
        self.assertTrue(uuid)

    @unittest.skip
    def testIsMobile(self):
        tracemalloc.start(10)
        self.assertFalse(self.to.ismobile(),
                         'This should fail on mobile systems')

    def testSetNumRules(self):
        num = 20
        tracemalloc.start(10)
        self.to.setnumrules(num)
        self.assertEqual(self.to.getnumrules(), num)

    def testSetNumRulesErr(self):
        tracemalloc.start(10)
        self.assertRaises(TypeError, self.to.setnumrules, 'foo')
        self.assertRaises(ValueError, self.to.setnumrules, -1)

###############################################################################

if __name__ == "__main__":

    unittest.main()

