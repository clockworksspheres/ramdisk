#!/usr/bin/env -S python -u
'''
Created on Jul 13, 2011 - stonix project

@author: dkennel
@change: 2015/10/23 eball Updated deprecated unit test methods, added dummy
                          PN file creation
@change: 2016-02-10 roy  adding sys.path.append for both test framework and 
                         individual test runs.
'''
import os
import re
import pwd
import sys
import unittest
import traceback
import tracemalloc

#####
# Include the parent project directory in the PYTHONPATH
appendDir = "/".join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
appendDir = ("../")
sys.path.append(appendDir)

# --- Non-native python libraries in this source tree
import ramdisk.lib.environment as environment

if sys.platform.startswith('win32'):
    import win32api
    from ramdisk.lib.windows_utilities import is_windows_process_elevated

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
                     'openSUSE|Mac OS X|macOS'
        print('OS Type: ' + str(self.to.getostype()))
        self.assertTrue(re.search(validtypes, self.to.getostype()))

    def testGetosfamily(self):
        tracemalloc.start(10)
        validfamilies = ['linux', 'darwin', 'solaris', 'freebsd']
        self.assertTrue(self.to.getosfamily() in validfamilies)

    def testGetosver(self):
        tracemalloc.start(10)
        self.assertTrue(re.search(r'([0-9]{1,3})|(([0-9]{1,3})\.([0-9]{1,3}))',
                                  self.to.getosver()))

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
        uid = os.geteuid()
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

