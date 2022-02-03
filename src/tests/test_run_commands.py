#!/usr/bin/env -S python -u

import unittest
import time
import sys
import os
import traceback
import tracemalloc
from datetime import datetime

#####
# Include the parent project directory in the PYTHONPATH
appendDir = "/".join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(appendDir)

#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.run_commands import RunWith, SetCommandTypeError


class test_run_commands(unittest.TestCase):
    """
    """

    @classmethod
    def setUpClass(self):
        """
        """
        #####
        # Set up logging
        self.logger = CyLogger(debug_mode=True)
        self.logger.initializeLogs()
        self.rw = RunWith(self.logger)
        #####
        # Start timer in miliseconds
        self.test_start_time = datetime.now()

    @classmethod
    def tearDownClass(self):
        """
        """
        pass

    def test_RunCommunicateWithBlankCommand(self):
        self.rw.__init__(self.logger)
        self.assertRaises(SetCommandTypeError, self.rw.setCommand, "")
        self.assertRaises(SetCommandTypeError, self.rw.setCommand, [])
        self.assertRaises(SetCommandTypeError, self.rw.setCommand, None)
        self.assertRaises(SetCommandTypeError, self.rw.setCommand, True)
        self.assertRaises(SetCommandTypeError, self.rw.setCommand, {})

    def test_setCommand(self):
        self.rw.__init__(self.logger)
        command = ['/bin/ls', 1, '.']
        self.assertRaises(SetCommandTypeError,
                          self.rw.setCommand, [command])

    def test_communicate(self):
        """
        """
        self.rw.__init__(self.logger)
        self.logger.log(lp.DEBUG, "=============== Starting test_communicate...")

        self.rw.setCommand('/bin/ls /var/spool', myshell=True)
        _, _, retval = self.rw.communicate(silent=False)
        self.assertEqual(retval, 0,
                          "Valid [] command execution failed: " +
                          '/bin/ls /var/spool --- retval: ' + str(retval))
        self.rw.setCommand(['/bin/ls', '-l', '/usr/local'])
        _, _, retval = self.rw.communicate(silent=False)
        self.assertEqual(retval, 0,
                          "Valid [] command execution failed: " +
                          '/bin/ls /var/spool --- retval: ' + str(retval))

        self.logger.log(lp.DEBUG, "=============== Ending test_communicate...")

    def test_wait(self):
        """
        """
        self.rw.__init__(self.logger)
        self.logger.log(lp.DEBUG, "=============== Starting test_wait...")

        self.rw.setCommand('/bin/ls /var/spool')
        try:
            _, _, retval = self.rw.communicate(silent=False)
        except Exception as err:
            self.logger.log(lp.ERROR, traceback.format_exc())
            # raise err

        self.assertEqual(retval, 0,
                          "Valid [] command execution failed: " +
                          '/bin/ls /var/spool --- retval: ' + str(retval))

        self.rw.setCommand(['/bin/ls', '-l', '/usr/local'])
        try:
            _, _, retval = self.rw.communicate(silent=False)
        except Exception as err:
            self.logger.log(lp.ERROR, traceback.format_exc())
            # raise err

        self.assertEqual(retval, 0,
                          "Valid [] command execution failed: " +
                          '/bin/ls -l /usr/local --- retval: ' + str(retval))
        '''
        temporarily commented out may not work the same on python 3.10.x
        self.rw.setCommand(['/bin/ls', '/1', '/'])
        tracemalloc.start(25)
        try:
            _, _, retcode = self.rw.wait()
        except Exception as err:
            self.logger.log(lp.ERROR, traceback.format_exc())
            retcode = 99999
            # raise err

        self.logger.log(lp.WARNING, "retcode: " + str(retcode))
        if sys.platform == 'darwin':
            self.assertEqual(retcode, 1, "Returncode Test failed...")
        else:
            self.assertEqual(retcode, 2, "Returncode Test failed...")
        '''
        self.logger.log(lp.DEBUG, "=============== Completed test_wait...")

    @unittest.skip("temporary skip to determine if split stdout/stderr could be the problem...")
    def test_waitNpassThruStdout(self):
        """
        """
        self.rw.__init__(self.logger)
        self.logger.log(lp.DEBUG, "=============== Starting test_wait...")

        tracemalloc.start(25)

        self.rw.setCommand(['/bin/ls', '-l', '/usr/local'])
        try:
            _, _, retval = self.rw.waitNpassThruStdout()
            self.assertEqual(retval, 0,
                                       "Valid [] command execution failed: " +
                                       '/bin/ls /var/spool --- retval: ' + str(retval))
        except Exception as err:
            self.logger.log(lp.ERROR, traceback.format_exc())
            # raise err

        self.logger.log(lp.INFO, "...first subtest done...")

        self.rw.setCommand(['/bin/ls', '/1', '/'])
        try:
            _, _, retval = self.rw.waitNpassThruStdout()
        except Exception as err:
            self.logger.log(lp.ERROR, traceback.format_exc())
            # raise err

        if sys.platform == 'darwin':
            self.assertEqual(retval, 1, "Returncode Test failed...")
        else:
            self.assertEqual(retval, 2, "Returncode Test failed...")

        self.logger.log(lp.DEBUG, "=============== Completed test_wait...")

    def test_timeout(self):
        """
        """
        self.rw.__init__(self.logger)

        tracemalloc.start(25)

        if os.path.exists("/sbin/ping"):
            ping = "/sbin/ping"
        elif os.path.exists('/bin/ping'):
            ping = "/bin/ping"

        self.rw.setCommand([ping, '-c', '12', '8.8.8.8'])
        try:
            startTime = time.time()
            self.rw.timeout(3)
            elapsed = (time.time() - startTime)
        except Exception as err:
            self.logger.log(lp.ERROR, traceback.format_exc())
            # raise err
        finally:
            self.logger.log(lp.INFO, "elapsed time: " + str(elapsed))

        self.assertTrue(elapsed < 4,
                        "Elapsed time is greater than it should be...")

    def test_runAs(self):
        """
        """
        pass

    def test_liftDown(self):
        """
        """
        pass

    def test_runAsWithSudo(self):
        """
        """
        pass

    def test_runWithSudo(self):
        """
        """
        pass

    def test_getecho(self):
        """
        """
        pass

    def test_waitnoecho(self):
        """
        """
        pass

    def test_RunThread(self):
        """
        """
        pass

    def test_runMyThreadCommand(self):
        """
        """
        pass


if __name__ == "__main__":

    unittest.main()


