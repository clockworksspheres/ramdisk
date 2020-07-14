from __future__ import absolute_import
import unittest
import time
import sys
import os
from datetime import datetime

appendDir = "/".join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-1])
sys.path.append(appendDir)

from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp
from lib.run_commands import RunWith, SetCommandTypeError


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
        self.assertEquals(retval, 0,
                          "Valid [] command execution failed: " +
                          '/bin/ls /var/spool --- retval: ' + str(retval))
        self.rw.setCommand(['/bin/ls', '-l', '/usr/local'])
        _, _, retval = self.rw.communicate(silent=False)
        self.assertEquals(retval, 0,
                          "Valid [] command execution failed: " +
                          '/bin/ls /var/spool --- retval: ' + str(retval))

        self.logger.log(lp.DEBUG, "=============== Ending test_communicate...")

    def test_wait(self):
        """
        """
        self.rw.__init__(self.logger)
        self.logger.log(lp.DEBUG, "=============== Starting test_wait...")

        self.rw.setCommand('/bin/ls /var/spool')
        _, _, retval = self.rw.communicate(silent=False)
        self.assertEquals(retval, 0,
                          "Valid [] command execution failed: " +
                          '/bin/ls /var/spool --- retval: ' + str(retval))

        self.rw.setCommand(['/bin/ls', '-l', '/usr/local'])
        _, _, retval = self.rw.communicate(silent=False)
        self.assertEquals(retval, 0,
                          "Valid [] command execution failed: " +
                          '/bin/ls /var/spool --- retval: ' + str(retval))


        self.rw.setCommand(['/bin/ls', '/1', '/'])
        _, _, retcode = self.rw.wait()
        self.logger.log(lp.WARNING, "retcode: " + str(retcode))
        if sys.platform == 'darwin':
            self.assertEquals(retcode, 1, "Returncode Test failed...")
        else:
            self.assertEquals(retcode, 2, "Returncode Test failed...")

    def test_waitNpassThruStdout(self):
        """
        """
        self.rw.__init__(self.logger)
        self.rw.setCommand(['/bin/ls', '-l', '/usr/local'])
        _, _, retval = self.rw.waitNpassThruStdout()
        self.assertEquals(retval, 0,
                          "Valid [] command execution failed: " +
                          '/bin/ls /var/spool --- retval: ' + str(retval))

        self.rw.setCommand(['/bin/ls', '/1', '/'])
        _, _, retval = self.rw.waitNpassThruStdout()
        if sys.platform == 'darwin':
            self.assertEquals(retval, 1, "Returncode Test failed...")
        else:
            self.assertEquals(retval, 2, "Returncode Test failed...")

    def test_timeout(self):
        """
        """
        self.rw.__init__(self.logger)
        if os.path.exists("/sbin/ping"):
            ping = "/sbin/ping"
        elif os.path.exists('/bin/ping'):
            ping = "/bin/ping"

        self.rw.setCommand([ping, '8.8.8.8'])

        startTime = time.time()
        self.rw.timeout(3)
        elapsed = (time.time() - startTime)

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


