"""
Library for running executables from the command line in different ways

Inspiration for some of the below found on the internet.


"""

# TODO: BUG - Class needs to return either byte streams or strings.  Check return, error and retcode values to see if they are strings, byte streams or int and treat accordingly
# TODO: FEATURE - Possibly have a bool to set or not determining if the class will return byte streams or strings

import os
import re
import sys
import time
import types
import select
import threading
import traceback
# import tracemalloc
from subprocess import Popen, PIPE
from subprocess import SubprocessError as SubprocessError

sys.path.append("../..")

from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.loggers import MockLogger
# from ramdisk.lib.getLibc import getLibc


class OSNotValidForRunWith(BaseException):
    """
    Custom Exception
    """
    def __init__(self, *args, **kwargs):
        BaseException.__init__(self, *args, **kwargs)


class NotACyLoggerError(BaseException):
    """
    Custom Exception
    """
    def __init__(self, *args, **kwargs):
        BaseException.__init__(self, *args, **kwargs)


class SetCommandTypeError(BaseException):
    """
    Custom Exception
    """
    def __init__(self, *args, **kwargs):
        BaseException.__init__(self, *args, **kwargs)


class RunWith(object):
    """
    Class that will run commands in various ways.

    @method setCommand(self, command=[])
    @method getStdout(self)
    @method getStderr(self)
    @method getReturnCode(self)
    @method getReturns(self)
    @method getNlogReturns(self)
    @method getNprintReturns(self)
    @method communicate(self)
    @method wait(self)
    @method waitNpassThruStdout(self)
    @method killProc(self)
    @method timeout(self, seconds=0)
    @method runAs(self, user="", password="")
    @method liftDown(self)
    @method getecho(self)
    @method waitnoecho(self)
    @method runAsWithSudo(self, user="", password="")
    @method runWithSudo(self, user="", password="")

    @WARNING - Known to work on Mac, may or may not work on other platforms

    
    """
    def __init__(self, logger=None, use_logger=True):
        if use_logger == True:

            if isinstance(logger, CyLogger):
                self.logger = logger
            else:
                self.logger = MockLogger
                # raise NotACyLoggerError("Passed in value for logger" +
                #                        " is invalid, try again.")
        elif use_logger == False:
            self.logger = MockLogger
        self.command = None
        self.stdout = None
        self.stderr = None
        self.retcode = None
        self.module_version = '20160224.184019.673753'
        self.printcmd = None
        self.myshell = None
        self.prompt = ""
        self.environ = None
        self.cfds = None
        self.text = True
        #####
        # setting up to call ctypes to do a filesystem sync
        # self.libc = getLibc()

        #####
        # Extra stuff to assist in debugging
        # tracemalloc.start(16)

    def setCommand(self, command, env=None, myshell=None, close_fds=None, text=True):
        """
        initialize a command to run

        
        """
        #####
        # Handle Popen's shell, or "myshell"...
        if command and isinstance(command, list):
            try:
                self.printcmd = " ".join(command)
                self.command = command
                if myshell is None or not isinstance(myshell, bool):
                    self.myshell = False
                else:
                    self.myshell = myshell
            except TypeError:
                raise SetCommandTypeError("Can only be passed a command " +
                                          "string or a list only containing " +
                                          "string elements for a command.")
        elif command and isinstance(command, str):
            self.command = command
            self.printcmd = command
            if myshell is None or not isinstance(myshell, bool):
                self.myshell = True
            else:
                self.myshell = myshell
        else:
            raise SetCommandTypeError("Command cannot be this type: " +
                            str(type(command)))

        self.logger.log(lp.DEBUG, "myshell: " + str(self.myshell))

        if env and isinstance(env, dict):
            self.environ = env
        else:
            self.environ = None

        if close_fds is None or not isinstance(close_fds, bool):
            self.cfds = False
        else:
            self.cfds = close_fds

    ###########################################################################

    def getStdout(self):
        """
        Getter for the standard output of the last command.

        
        """
        return self.stdout

    ###########################################################################

    def getStderr(self):
        """
        Getter for the standard error of the last command.

        
        """
        return self.stderr

    ###########################################################################

    def getReturnCode(self):
        """
        Getter for the return code of the last command.

        
        """
        return self.retcode

    ###########################################################################

    def getReturns(self):
        """
        Getter for the retval, reterr & retcode of the last command.

        
        """
        return self.stdout, self.stderr, self.retcode

    ###########################################################################

    def getNlogReturns(self):
        """
        Getter for the retval, reterr & retcode of the last command.

        Will also log the values

        
        """
        self.logger.log(lp.INFO, "Output: " + str(self.stdout))
        self.logger.log(lp.INFO, "Error: " + str(self.stderr))
        self.logger.log(lp.INFO, "Return code: " + str(self.retcode))
        return self.stdout, self.stderr, self.retcode

    ###########################################################################

    def getNprintReturns(self):
        """
        Getter for the retval, reterr & retcode of the last command.

        Will also print the values

        
        """
        print("Output: " + str(self.stdout))
        print("Error: " + str(self.stderr))
        print("Return code: " + str(self.retcode))
        return self.stdout, self.stderr, self.retcode

    ###########################################################################

    def communicate(self, silent=True):
        """
        Use the subprocess module to execute a command, returning
        the output of the command

        @param: silent - Whether or not to print the command as part of
                         standard logging practices.  Silent = True to
                         not print the command being run.  Silent = False
                         to print the command.

        
        """
        self.stdout = ''
        self.stderr = ''
        self.retcode = 999
        if self.command and isinstance(silent, bool):
            try:
                proc = Popen(self.command, stdout=PIPE, stderr=PIPE, shell=self.myshell, env=self.environ, close_fds=self.cfds, text=self.text)
                self.stdout, self.stderr = proc.communicate()
                self.stdout = str(self.stdout)
                self.stderr = str(self.stderr)

                self.retcode = proc.returncode

                # self.libc.sync()
            except SubprocessError as err:
                if not silent:
                    self.logger.log(lp.WARNING, "command: " + str(self.printcmd))
                    self.logger.log(lp.DEBUG, "stdout: " + str(self.stdout))
                    self.logger.log(lp.DEBUG, "stderr: " + str(self.stderr))
                    self.logger.log(lp.DEBUG, "retcode: " + str(self.retcode))
                self.logger.log(lp.WARNING, "stderr: " + str(self.stderr))
                self.logger.log(lp.WARNING, traceback.format_exc())
                self.logger.log(lp.WARNING, str(err))
                raise err
            else:
                if not silent:
                    self.logger.log(lp.DEBUG, "Done with: " + self.printcmd)
                self.logger.log(lp.DEBUG, "Command returned with error/returncode: " + str(self.retcode))
            finally:
                try:
                    proc.stdout.close()
                except SubprocessError:
                    pass
                try:
                    proc.stderr.close()
                except SubprocessError:
                    pass
                #####
                # Lines below could reveal a password if it is passed as an
                # argument to the command.  Could reveal in whatever stream
                # the logger is set to log (syslog, console, etc, etc.
                if not silent:
                    self.logger.log(lp.DEBUG, "Done with command: " + self.printcmd)
                    self.logger.log(lp.DEBUG, "stdout: " + str(self.stdout))
                    self.logger.log(lp.DEBUG, "stderr: " + str(self.stderr))
                    self.logger.log(lp.DEBUG, "retcode: " + str(self.retcode))
        else:
            self.logger.log(lp.WARNING,
                            "Cannot run a command that way...")
            self.stdout = None
            self.stderr = None
            self.retcode = None

        self.command = None
        return self.stdout, self.stderr, self.retcode

