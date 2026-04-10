"""
Library for running executables from the command line in different ways
"""

# TODO: BUG - Class needs to return either byte streams or strings.  Check return, error and retcode values to see if they are strings, byte streams or int and treat accordingly
# TODO: FEATURE - Possibly have a bool to set or not determining if the class will return byte streams or strings

import os
import re
import sys

sys.path.append("../..")

from ramdisk.lib.libHelperExceptions import NotValidForThisOS

if not sys.platform.startswith("linux"):
    raise NotValidForThisOS("Not Valid For This OS...")

import pty
import time
import types
import select
import termios
import threading
import traceback
# import tracemalloc
from subprocess import Popen, PIPE
from subprocess import SubprocessError as SubprocessError

sys.path.append("../..")

from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.loggers import MockLogger
from ramdisk.lib.getLibc.linuxGetLibc import getLibc


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
        if use_logger:

            if isinstance(logger, type(CyLogger)):
                self.logger = logger
            else:
                self.logger = MockLogger
                # raise NotACyLoggerError("Passed in value for logger" +
                #                        " is invalid, try again.")
        elif not use_logger:
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

    def setCommand(self, command, env=None, myshell=None, close_fds=None, text=True, creationflags=None):
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

        # Windows Parameters - pass in a comma separated list of parameters, will deal with in here...
        valid_creationflags = [ "CREATE_NEW_CONSOLE",
                                "CREATE_NEW_PROCESS_GROUP",
                                "ABOVE_NORMAL_PRIORITY_CLASS",
                                "BELOW_NORMAL_PRIORITY_CLASS",
                                "HIGH_PRIORITY_CLASS",
                                "IDLE_PRIORITY_CLASS",
                                "NORMAL_PRIORITY_CLASS",
                                "REALTIME_PRIORITY_CLASS",
                                "CREATE_NO_WINDOW",
                                "DETACHED_PROCESS",
                                "CREATE_DEFAULT_ERROR_MODE",
                                "CREATE_BREAKAWAY_FROM_JOB"
                               ]
        self.logger.log(lp.INFO, "creationflags: {0}".format(str(creationflags)))
        self.creationflags = ""
        # if creationflags is not None:
        #    if re.search(",", creationflags):
        #        self.creationflags = re.sub(",", " | ", creationflags)
        #if creationflags is True:
        #    self.creationflags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        #    self.creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

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

    def getNlogReturns(self, nolog=True):
        """
        Getter for the retval, reterr & retcode of the last command.

        Will also log the values
        """
        if nolog == False:
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
                if not self.creationflags:
                    proc = Popen(self.command, stdout=PIPE, stderr=PIPE, shell=self.myshell, env=self.environ, close_fds=self.cfds, text=self.text)
                if self.creationflags:
                    proc = Popen(self.command, stdout=PIPE, stderr=PIPE, shell=self.myshell, env=self.environ, close_fds=self.cfds, text=self.text, creationflags=self.creationflags)
                self.logger.log(lp.INFO, "creationflags: {0}".format(str(self.creationflags)))

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
                except (SubprocessError, UnboundLocalError):
                    pass
                try:
                    proc.stderr.close()
                except (SubprocessError, UnboundLocalError):
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

    ###########################################################################

    def wait(self, silent=True):
        """
        Use subprocess to call a command and wait until it is finished before
        moving on...
        """
        self.stdout = ''
        self.stderr = ''
        if self.command:
            try:
                proc = Popen(self.command,
                             stdout=PIPE, stderr=PIPE,
                             shell=self.myshell,
                             env=self.environ,
                             close_fds=self.cfds,
                             text=self.text)
                proc.wait()
                for line in proc.stdout.readline():
                    if line:
                        self.stdout = str(self.stdout) + str(line) + "\n"
                if proc.stderr:
                    for line in proc.stderr.readline():
                        if line:
                            self.stderr = str(self.stderr) + str(line) + "\n"
                else:
                    self.stderr = ""
                proc.wait()
                self.retcode = proc.returncode
                # self.libc.sync()
            except SubprocessError as err:
                if not silent:
                    self.logger.log(lp.WARNING, "command: " + str(self.printcmd))
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
                except UnboundLocalError:
                    pass
                except SubprocessError:
                    pass 
                try:
                    proc.stderr.close()
                except UnboundLocalError:
                    pass
                except SubprocessError:
                    pass 
                if not silent:
                    self.logger.log(lp.DEBUG, "Done with command: " + self.printcmd)
                    self.logger.log(lp.DEBUG, "stdout: " + str(self.stdout))
                    self.logger.log(lp.DEBUG, "stderr: " + str(self.stderr))
                    self.logger.log(lp.DEBUG, "retcode: " + str(self.retcode))
        else:
            self.logger.log(lp.WARNING,
                            "Cannot run a command that is empty...")
            self.stdout = None
            self.stderr = None
            self.retcode = None

        self.command = None
        return self.stdout, self.stderr, self.retcode

    ###########################################################################

    def waitNpassThruStdout(self, chk_string=None, respawn=False, silent=True):
        """
        Use the subprocess module to execute a command, returning
        the output of the command
        """
        self.stdout = ''
        self.stderr = ''
        self.retcode = 999
        if self.command:
            try:
                proc = Popen(self.command, stdout=PIPE, stderr=PIPE,
                             shell=self.myshell,
                             env=self.environ,
                             close_fds=self.cfds,
                             text=self.text)
                if proc:
                    while True:
                        #####
                        # process stdout
                        myout = proc.stdout.readline()
                        if myout == '' and proc.poll() is not None:
                            break
                        tmpline = str(myout)
                        tmpline = str(tmpline).strip()
                        self.stdout += str(tmpline) + "\n"

                        # if tmpline and not silent:
                        #     self.logger.log(lp.DEBUG, str(tmpline))

                        if isinstance(chk_string, str):
                            if not chk_string:
                                continue
                            else:
                                if re.search(chk_string, tmpline):
                                    try:
                                        proc.stdout.close()
                                    except SubprocessError as err:
                                        self.logger.log(lp.INFO, traceback.format_exc())
                                    try:
                                        proc.stderr.close()
                                    except SubprocessError as err:
                                        self.logger.log(lp.INFO, traceback.format_exc())

                                    if respawn:
                                        pass
                                    else:
                                        self.logger.log(lp.INFO,
                                                        "chk_string found" +
                                                        "... exiting process.")
                                    break

                        if isinstance(chk_string, list):
                            if not chk_string:
                                continue
                            else:
                                found = False
                                for mystring in chk_string:
                                    if chk_string(mystring, tmpline):
                                        try:
                                            proc.stdout.close()
                                        except SubprocessError as err:
                                            self.logger.log(lp.INFO, traceback.format_exc())

                                        try:
                                            proc.stderr.close()
                                        except SubprocessError as err:
                                            self.logger.log(lp.INFO, traceback.format_exc())

                                        proc.stderr.close()
                                        if respawn:
                                            pass
                                        else:
                                            self.logger.log(lp.INFO,
                                                            "chk_string " +
                                                            "found... " +
                                                            "exiting process.")
                                            found = True
                                            break
                                if found:
                                    break

                    while True:
                        myerr = proc.stderr.readline()
                        if myerr == '' and proc.poll() is not None:
                            break
                        tmpline = str(myerr).strip()
                        self.stderr += tmpline + "\n"

                        if tmpline and not silent:
                            self.logger.log(lp.DEBUG, str(tmpline))

                        if isinstance(chk_string, str):
                            if not chk_string:
                                continue
                            else:
                                if re.search(chk_string, tmpline):
                                    try:
                                        proc.stdout.close()
                                    except SubprocessError as err:
                                        self.logger.log(lp.INFO, traceback.format_exc())

                                    try:
                                        proc.stderr.close()
                                    except SubprocessError as err:
                                        self.logger.log(lp.INFO, traceback.format_exc())

                                    if respawn:
                                        pass
                                    else:
                                        self.logger.log(lp.INFO,
                                                        "chk_string found" +
                                                        "... exiting process.")
                                    break

                        if isinstance(chk_string, list):
                            if not chk_string:
                                continue
                            else:
                                found = False
                                for mystring in chk_string:
                                    if chk_string(mystring, tmpline):
                                        try:
                                            proc.stdout.close()
                                        except SubprocessError as err:
                                            self.logger.log(lp.INFO, traceback.format_exc())

                                        try:
                                            proc.stderr.close()
                                        except SubprocessError as err:
                                            self.logger.log(lp.INFO, traceback.format_exc())

                                        if respawn:
                                            pass
                                        else:
                                            self.logger.log(lp.INFO,
                                                            "chk_string " +
                                                            "found... " +
                                                            "exiting process.")
                                            found = True
                                            break
                                if found:
                                    break

                proc.wait()
                try:
                    proc.stdout.close()
                except SubprocessError as err:
                    self.logger.log(lp.INFO, traceback.format_exc())
                try:
                    proc.stderr.close()
                except SubprocessError as err:
                    self.logger.log(lp.INFO, traceback.format_exc())

                self.retcode = proc.returncode
                # self.libc.sync()

            except SubprocessError as err:
                if not silent:
                    self.logger.log(lp.WARNING, "command: " + str(self.printcmd))
                self.logger.log(lp.WARNING, "stderr: " + str(self.stderr))
                self.logger.log(lp.WARNING, traceback.format_exc())
                self.logger.log(lp.WARNING, str(err))
                raise err
            else:
                if not silent:
                    self.logger.log(lp.DEBUG, "Done with: " + self.printcmd)
            finally:
                print(self.retcode)
                # self.retcode = self.retcode
                if not silent:
                    self.logger.log(lp.DEBUG, "Done with command: " + self.printcmd)
                self.logger.log(lp.DEBUG, "stdout: " + str(self.stdout))
                self.logger.log(lp.DEBUG, "stderr: " + str(self.stderr))
                self.logger.log(lp.DEBUG, "retcode: " + str(self.retcode))
        else:
            self.logger.log(lp.WARNING,
                            "Cannot run a command that is empty...")
            self.stdout = None
            self.stderr = None
            self.retcode = None

        self.command = None
        return self.stdout, self.stderr, self.retcode

    ###########################################################################

    def killProc(self, proc, timeout):
        """
        Support function for the "runWithTimeout" function below
        """
        timeout["value"] = True
        proc.kill()

    ###########################################################################

    def timeout(self, timout_sec, silent=True):
        """
        Run a command with a timeout - return:
        Returncode of the process
        stdout of the process
        stderr of the process
        timout - True if the command timed out
                 False if the command completed successfully
        """
        if self.command:
            try:
                proc = Popen(self.command,
                             stdout=PIPE, stderr=PIPE, shell=self.myshell)

                timeout = {"value": False}
                timer = threading.Timer(timout_sec, self.killProc,
                                        [proc, timeout])
                timer.start()
                self.stdout, self.stderr = proc.communicate()
                timer.cancel()
                self.retcode = proc.returncode
            except SubprocessError as err:
                if not silent:
                    self.logger.log(lp.WARNING, "command: " + str(self.printcmd))
                self.logger.log(lp.WARNING, "stderr: " + str(self.stderr))
                self.logger.log(lp.WARNING, traceback.format_exc())
                self.logger.log(lp.WARNING, str(err))
                raise err
            else:
                if not silent:
                    self.logger.log(lp.DEBUG, "Done with: " + self.printcmd)
                # DO NOT overwrite stdout/stderr with file objects
                # self.stdout = proc.stdout
                # self.stderr = proc.stderr
                # self.retcode = proc.returncode
                # self.libc.sync()
                proc.stdout.close()
                proc.stderr.close()
            finally:
                if not silent:
                    self.logger.log(lp.DEBUG, "Done with command: " +
                                    str(self.printcmd))
                    self.logger.log(lp.DEBUG, "stdout: " + str(self.stdout))
                    self.logger.log(lp.DEBUG, "stderr: " + str(self.stderr))
                    self.logger.log(lp.DEBUG, "retcode: " + str(self.retcode))
        else:
            self.logger.log(lp.WARNING,
                            "Cannot run a command that is empty...")
            self.stdout = None
            self.stderr = None
            self.retcode = None

        self.command = None
        try:
            retvalue = self.stdout, self.stderr, self.retcode, timeout["value"]
        except UnboundLocalError:
            retvalue = self.stdout, self.stderr, self.retcode, ""
        return retvalue
            
    ###########################################################################

    def runAs(self, user="", password="", silent=True):
        """
        Use pexpect to run "su" to run a command as another user...

        Required parameters: user, password, command
        """
        self.stdout = ""
        self.stderr = ""
        self.retcode = 999
        # pretcode = 0
        if re.match(r"^\s*$", user) or \
           re.match(r"^\s*$", password) or \
           not self.command:
            self.logger.log(lp.WARNING, "Cannot pass in empty parameters...")
            self.logger.log(lp.WARNING, "user = \"" + str(user) + "\"")
            self.logger.log(lp.WARNING, "check password...")
            if not silent:
                self.logger.log(lp.WARNING,
                                "command = \"" + str(self.command) + "\"")
            return 255
        else:
            output = ""
            internal_command = ["/usr/bin/su", "-", str(user.strip()), "-c"]

            if isinstance(self.command, list):
                internal_command.append(" ".join(self.command))
                if not silent:
                    self.logger.log(lp.DEBUG, "Trying to execute: \"" +
                                    " ".join(internal_command) + "\"")
            elif isinstance(self.command, str):
                internal_command += self.command
                if not silent:
                    self.logger.log(lp.DEBUG, "Trying to execute: \"" +
                                    " ".join(internal_command) + "\"")

            (master, slave) = pty.openpty()

            proc = Popen(internal_command,
                         stdin=slave, stdout=slave, stderr=slave,
                         close_fds=True, text=self.text)

            prompt = os.read(master, 10)

            if re.match("^Password:", str(prompt)):
                os.write(master, password + "\n")
                line = os.read(master, 512)
                output = output + line
                while True:
                    #####
                    # timeout of 0 means "poll"
                    ready, _, _ = select.select([master], [], [], 0)
                    if ready:
                        line = os.read(master, 512)
                        #####
                        # Warning, uncomment at your own risk - several
                        # programs print empty lines that will cause this to
                        # break and the output will be all goofed up.
                        # if not line :
                        #    break
                        # print output.rstrip()
                        output = output + line
                    elif proc.poll() is not None:
                        break
                os.close(master)
                os.close(slave)
                # self.libc.sync()
                proc.wait()
                # self.libc.sync()
                self.stdout = proc.stdout
                self.stderr = proc.stderr
                self.retcode = proc.returncode
            else:
                output = prompt
                while True:
                    #####
                    # timeout of 0 means "poll"
                    ready, _, _ = select.select([master], [], [], 0)
                    if ready:
                        line = os.read(master, 512)
                        #####
                        # Warning, uncomment at your own risk - several
                        # programs print empty lines that will cause this to
                        # break and the output will be all goofed up.
                        # if not line :
                        #    break
                        # print output.rstrip()
                        output = output + line
                    elif proc.poll() is not None:
                        break
                os.close(master)
                os.close(slave)
                proc.wait()
                self.stdout = output
                self.stderr = str(proc.stderr)
                self.retcode = proc.returncode
            output = output.strip()
            if not silent:
                self.logger.log(lp.DEBUG, "retcode: " + str(self.stdout))
                self.logger.log(lp.DEBUG, "retcode: " + str(self.stderr))
                self.logger.log(lp.DEBUG, "retcode: " + str(self.retcode))

        self.command = None
        return self.stdout, self.stderr, self.retcode

    ###########################################################################

    def liftDown(self, user="", target_dir="", silent=True):
        """
        Use the lift (elevator) to execute a command from privileged mode
        to a user's context with that user's uid.  Does not require a password.

        @param: user - name of user to run as
        @param: target_dir - directory to run the command from
        """
        self.stdout = ""
        self.stderr = ""
        self.retcode = 999
        user = user.strip()

        if os.getuid() != 0:
            self.logger.log("This can only run if running in privileged mode.")
            return 256

        if isinstance(target_dir, str) and target_dir:
            return_dir = os.getcwd()
            if os.path.exists(target_dir):
                os.chdir(target_dir)

        if re.match(r"^\s*$", user) or not self.command:
            self.logger.log(lp.WARNING, "Cannot pass in empty parameters...")
            self.logger.log(lp.WARNING, "user = " + str(user))
            if not silent:
                self.logger.log(lp.WARNING,
                                "command = \"" + str(self.command) + "\"")
            return 255
        else:
            internal_command = ["/usr/bin/su", "-", str(user), "-c"]

            if isinstance(self.command, list):
                cmd = []
                for i in range(len(self.command)):
                    try:
                        cmd.append(str(self.command[i]('utf-8')))
                    except UnicodeDecodeError:
                        cmd.append(str(self.command[i]))

                internal_command.append(str(" ".join(cmd)))
            elif isinstance(self.command, str):
                internal_command.append(self.command)

        self.setCommand(internal_command)
        self.stdout, self.stderr, self.retcode = self.communicate()
        if not silent:
            for line in self.stdout.split('\n'):
                self.logger.log(lp.DEBUG, "out: " + str(line))
            for line in self.stderr.split('\n'):
                self.logger.log(lp.DEBUG, "err: " + str(line))
            self.logger.log(lp.DEBUG, "retcode: " + str(self.retcode))

        if target_dir:
            os.chdir(return_dir)

        self.command = None
        return self.stdout, self.stderr, self.retcode

    ###########################################################################

    def getecho (self, fileDescriptor):
        """This returns the terminal echo mode. This returns True if echo is
        on or False if echo is off. Child applications that are expecting you
        to enter a password often set ECHO False. See waitnoecho().

        Borrowed from pexpect - acceptable to license
        """
        attr = termios.tcgetattr(fileDescriptor)
        if attr[3] & termios.ECHO:
            return True
        return False

    ###########################################################################

    def waitnoecho (self, fileDescriptor, timeout=3):
        """This waits until the terminal ECHO flag is set False. This returns
        True if the echo mode is off. This returns False if the ECHO flag was
        not set False before the timeout. This can be used to detect when the
        child is waiting for a password. Usually a child application will turn
        off echo mode when it is waiting for the user to enter a password. For
        example, instead of expecting the "password:" prompt you can wait for
        the child to set ECHO off::

            see below in runAsWithSudo

        If timeout is None or negative, then this method to block forever until
        ECHO flag is False.

        Borrowed from pexpect - acceptable to license
        """
        if timeout is not None and timeout > 0:
            end_time = time.time() + timeout
        while True:
            if not self.getecho(fileDescriptor):
                return True
            if timeout < 0 and timeout is not None:
                return False
            if timeout is not None:
                timeout = end_time - time.time()
            time.sleep(0.1)

    ###########################################################################

    def runAsWithSudo(self, user="", password="", silent=True) :
        """
        Use pty method to run "su" to run a command as another user...

        Required parameters: user, password, command
        """
        self.logger.log(lp.DEBUG, "Starting runAsWithSudo: ")
        self.logger.log(lp.DEBUG, "\tuser: \"" + str(user) + "\"")
        self.logger.log(lp.DEBUG, "\tcmd : \"" + str(self.command) + "\"")
        if re.match(r"^\s+$", user) or re.match(r"^\s+$", password) or \
           not user or not password or \
           not self.command:
            self.logger.log(lp.WARNING, "Cannot pass in empty parameters...")
            self.logger.log(lp.WARNING, "user = \"" + str(user) + "\"")
            self.logger.log(lp.WARNING, "check password...")
            if not silent:
                self.logger.log(lp.WARNING, "command: " + str(self.command))
            return 255
        else:
            output = ""

            internal_command = ["/usr/bin/su", str("-m"),
                                str(user).strip(), str("-c")]

            if isinstance(self.command, list):
                cmd = []
                for i in range(len(self.command)):
                    try:
                        cmd.append(str(self.command[i]))
                    except UnicodeDecodeError:
                        cmd.append(str(self.command[i]))

                internal_command.append(str("/usr/bin/sudo -S -s '" +
                                            " ".join(cmd) + "'"))
            elif isinstance(self.command, str):
                try:
                    internal_command.append(str("/usr/bin/sudo -E -S -s " +
                                                "'" +
                                                str(self.command) +
                                                "'").encode())
                except UnicodeDecodeError:
                    internal_command.append(str("/usr/bin/sudo -E -S -s " +
                                                "'" +
                                                str(self.command) + "'"))

            try:
                (master, slave) = pty.openpty()
            except SubprocessError as err:
                self.logger.log(lp.WARNING, "Error trying to open pty: " +
                                str(err))
                self.logger.log(lp.WARNING, traceback.format_exc())
                self.logger.log(lp.WARNING, str(err))
                raise err
            else:
                try:
                    proc = Popen(internal_command,
                                 stdin=slave, stdout=slave, stderr=slave,
                                 close_fds=True,
                                 text=self.text)
                except SubprocessError as err:
                    self.logger.log(lp.WARNING,
                                    "Error opening process to pty: " +
                                    str(err))
                    self.logger.log(lp.WARNING, traceback.format_exc())
                    self.logger.log(lp.WARNING, str(err))
                    raise err
                else:
                    #####
                    # Catch the su password prompt
                    # prompt = os.read(master, 512)
                    self.waitnoecho(master, 3)
                    self.prompt = os.read(master, 512)

                    #####
                    # pass in the password
                    #os.write(master, password.strip() + "\n")
                    os.write(master, password + "\n".encode())

                    #####
                    # catch the password
                    self.prompt = os.read(master, 512)

                    #####
                    # Wait for the next password prompt
                    self.waitnoecho(master, 3)

                    #####
                    # catch the password prompt
                    self.prompt = os.read(master, 512)

                    #####
                    # Enter the sudo password
                    os.write(master, password + "\n")

                    #####
                    # Catch the password
                    os.read(master, 512)

                    # output = tmp + output
                    while True:
                        #####
                        # timeout of 0 means "poll"
                        ready, _, _ = select.select([master], [], [], 0)
                        if ready:
                            line = os.read(master, 512)
                            #####
                            # Warning, uncomment at your own risk - several
                            # programs print empty lines that will cause this
                            # to break and the output will be all goofed up.
                            # if not line :
                            #    break
                            # print output.rstrip()
                            output = output + line
                        elif proc.poll() is not None:
                            break
                        # print output.strip()
                    os.close(master)
                    os.close(slave)
                    self.libc.sync()
                    proc.wait()
                    self.libc.sync()
                    self.stdout = proc.stdout
                    self.stderr = proc.stderr
                    self.retcode = proc.returncode
                    # print output.strip()
            if not silent:
                self.logger.log(lp.DEBUG, "\n\nLeaving runAs with Sudo: \"" +
                                str(self.stdout) + "\"\n\n")
        self.command = None
        return self.stdout, self.stderr, self.retcode

    ###########################################################################

    def runWithSudo(self, password="", silent=True, timeout_sec=15):
        '''
        Use pty method to run "sudo" to run a command with elevated privilege.

        Required parameters: password
        '''
        self.stdout = ""
        self.stderr = ""
        self.retcode = 255

        self.logger.log(lp.DEBUG, "Starting runWithSudo: ")
        self.logger.log(lp.DEBUG, "\tcmd : " + str(self.command))
        if re.match(r"^\s+$", password) or \
           not password or \
           not self.command:
            self.logger.log(lp.WARNING, "Cannot pass in empty parameters...")
            self.logger.log(lp.WARNING, "check password...")
            if not silent:
                self.logger.log(lp.WARNING, "command: " + str(self.command))
            return 255
        else:
            output = "".encode()
            cmd = ["/usr/bin/sudo", "-S", "-s"]

            if isinstance(self.command, list):
                cmd = cmd + [" ".join(self.command)]

            elif isinstance(self.command, str):
                cmd = cmd + [self.command]

            try:
                (master, slave) = pty.openpty()
            except SubprocessError as err:
                self.logger.log(lp.WARNING, "Error trying to open pty: " +
                                str(err))
                self.logger.log(lp.WARNING, traceback.format_exc())
                self.logger.log(lp.WARNING, str(err))
                raise err
            else:
                try:
                    proc = Popen(cmd, stdin=slave, stdout=slave, stderr=slave,
                                 close_fds=True,
                                 text=self.text)
                    timeout = {"value": False}
                    timer = threading.Timer(timeout_sec, self.killProc,
                                            [proc, timeout])
                    timer.start()
                except SubprocessError as err:
                    self.logger.log(lp.WARNING,
                                    "Error opening process to pty: " +
                                    str(err))
                    self.logger.log(lp.WARNING, traceback.format_exc())
                    self.logger.log(lp.WARNING, str(err))
                    raise err
                else:
                    #####
                    # Catch the sudo password prompt
                    # prompt = os.read(master, 512)
                    self.waitnoecho(master, 3)
                    self.prompt = os.read(master, 512)

                    #####
                    # Enter the sudo password
                    os.write(master, str(password + "\n").encode())

                    #####
                    # Catch the password
                    os.read(master, 512)

                    # output = tmp + output
                    while True:
                        #####
                        # timeout of 0 means "poll"
                        ready, _, _ = select.select([master], [], [], 0)
                        if ready:
                            line = os.read(master, 512)
                            #####
                            # Warning, uncomment at your own risk - several
                            # programs print empty lines that will cause this
                            # to break and the output will be all goofed up.
                            # if not line :
                            #    break
                            # print output.rstrip()
                            output = output + line
                        elif proc.poll() is not None:
                            break
                        # print output.strip()
                    os.close(master)
                    os.close(slave)
                    self.libc.sync()
                    proc.wait()
                    self.libc.sync()
                    timer.cancel()
                    self.stdout = output.decode()
                    self.stderr = proc.stderr
                    self.retcode = proc.returncode
                    #print output.strip()
            #output = output.strip()
            if not silent:
                #####
                # ONLY USE WHEN IN DEVELOPMENT AND DEBUGGING OR YOU MAY
                # REVEAL MORE THAN YOU WANT TO IN THE LOGS!!!
                self.logger.log(lp.DEBUG, "\n\nLeaving runAs with Sudo: \"" + \
                                str(output) + "\"\n" + str(self.stdout) + "\n")
            return self.stdout, self.stderr, self.retcode

##############################################################################

class RunThread(threading.Thread):
    """
    Use a thread & subprocess.Popen to run something

    To use - where command could be an array, or a string... :

    run_thread = RunThread(<command>, message_level)
    run_thread.start()
    run_thread.join()
    print run_thread.stdout
    """
    def __init__(self, command, logger, myshell=False):
        """
        Initialization method
        """
        self.command = command
        self.logger = logger
        self.retout = None
        self.reterr = None
        self.shell = myshell
        threading.Thread.__init__(self)

        if isinstance(self.command, list):
            self.shell = True
            self.printcmd = " ".join(self.command)
        if isinstance(self.command, (str,)):
            self.shell = False
            self.printcmd = self.command

        if isinstance(logger, type(CyLogger)):
            self.logger = logger
        else:
            raise NotACyLoggerError("Passed in value for logger " +
                                    "is invalid, try again.")

        self.logger.log(lp.INFO, "Initialized runThread...")

    ##########################################################################

    def run(self):
        if self.command:
            try:
                p = Popen(self.command, stdout=PIPE,
                                        stderr=PIPE,
                                        shell=self.shell)
                self.retout, self.reterr = p.communicate()
                self.logger.log(lp.WARNING, "Finished \"run\" of: " +
                                str(self.command))
            except SubprocessError as err:
                self.logger.log(lp.WARNING, "Exception trying to open: " +
                                str(self.command))
                self.logger.log(lp.WARNING, traceback.format_exc())
                self.logger.log(lp.WARNING, str(err))
                raise err
            else:
                try:
                    self.retout, self.reterr = p.communicate()
                except SubprocessError as err:
                    self.logger.log(lp.WARNING, "Exception trying to open: " +
                                    str(self.printcmd))
                    self.logger.log(lp.WARNING, "Associated exception: " +
                                    str(err))
                    raise err
                else:
                    self.logger.log(lp.WARNING, "Finished \"run\" of: " +
                                    str(self.printcmd))

    ############################################################################

    def runWithSudoRs(self, password="", silent=True, timeout_sec=15) :
        """
        Use pty method to run "sudo-rs" to run a command with elevated privilege.

        sudo-rs is the rust version of sudo being integrated into the Ubuntu platform.

        Required parameters: password
        """
        self.stdout = ""
        self.stderr = ""
        self.retcode = 255

        self.logger.log(lp.DEBUG, "Starting runWithSudo: ")
        self.logger.log(lp.DEBUG, "\tcmd : " + str(self.command))
        if re.match(r"^\s+$", password) or \
           not password or \
           not self.command:
            self.logger.log(lp.WARNING, "Cannot pass in empty parameters...")
            self.logger.log(lp.WARNING, "check password...")
            if not silent:
                self.logger.log(lp.WARNING, "command: " + str(self.command))
            return(255)
        else:
            output = "".encode()
            sudocmd = ["/usr/bin/sudo-rs", "-S"]

            if isinstance(self.command, list):
                #cmd = " ".join(sudocmd) + " " + " ".join(self.command)
                cmd = sudocmd + self.command
            elif isinstance(self.command, str):
                #cmd = " ".join(sudocmd) + " " + self.command
                cmd = sudocmd + self.command.split()

            # Create a subprocess
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Set file descriptors to non-blocking
            os.set_blocking(process.stdin.fileno(), False)
            os.set_blocking(process.stdout.fileno(), False)
            os.set_blocking(process.stderr.fileno(), False)

            # Data to send to stdin
            if isinstance(password, str):
                input_data = password.encode()
            else:
                input_data = password
            stdin_closed = False
            stdout_closed = False
            stderr_closed = False

            # Use select to monitor file descriptors and send data to stdin
            while True:
                # Wait for data to be ready for reading and writing
                read_ready, write_ready, _ = select.select(
                    [process.stdout] if not stdout_closed else [],
                    [process.stdin] if not stdin_closed else [],
                    []
                )

                for stream in read_ready:
                    if stream is process.stdout:
                        output = stream.read()
                        if output:
                            # print("Output:", output.decode())
                            self.stdout = output.decode() + "\n"
                        else:
                            # No more data to read, mark stdout as closed
                            stdout_closed = True
                    elif stream is process.stderr:
                        error = stream.read()
                        if error:
                            # print("Error:", error.decode())
                            self.stderr = error.decode() + "\n"
                        else:
                            # No more data to read, mark stderr as closed
                            stderr_closed = True

                for stream in write_ready:
                    if stream is process.stdin:
                        if input_data:
                            # Write data to stdin
                            stream.write(input_data)
                            stream.flush()
                            input_data = None  # Clear input_data to avoid sending it again
                        else:
                            # Close stdin if no more data to send
                            stream.close()
                            stdin_closed = True

                # Check if the process has terminated
                if process.poll() is not None:
                    break

                # Check if all file descriptors are closed
                #    Looks like stderr behaves badly in this instance,
                #    and it is likely ok to close the process if stderr
                #    is hanging like a loose hangnail...  If not, there
                #    may be bigger problems that need to be solved in
                #    process.  It is likely that you still want to catch
                #    and report stderr however.
                if stdin_closed and stdout_closed: # and stderr_closed:
                    break

            self.output = process.stdout
            self.stderr = process.stderr

            # Clean up
            if not stdin_closed:
                process.stdin.close()
            if not stdout_closed:
                process.stdout.close()
            if not stderr_closed:
                process.stderr.close()
            self.retcode = process.wait()

            if not silent:
                #####
                # ONLY USE WHEN IN DEVELOPMENT AND DEBUGGING OR YOU MAY
                # REVEAL MORE THAN YOU WANT TO IN THE LOGS!!!
                self.logger.log(lp.DEBUG, "\n\nLeaving runAs with Sudo: \"" + \
                                str(output) + "\"\n" + str(self.stdout) + "\n")
            return self.stdout, self.stderr, self.retcode

    ##########################################################################

def runCommand2check(self, check_string="", get_my_pass=None):
    found_prompt = False

    output = ""

    # Create a pseudo-terminal
    master, slave = pty.openpty()

    # Start the process with the slave side of the pty as its stdout/stderr
    proc = subprocess.Popen(
        command,
        stdin=slave,
        stdout=slave,
        stderr=slave,
        close_fds=True
    )

    # Close the slave fd in the parent process
    os.close(slave)

    found_prompt = False

    # Monitor the master fd for output
    output = ""
    while proc.poll() is None:
        ready, _, _ = select.select([master], [], [], 0.1)
        if ready:
            try:
                data = os.read(master, 1024).decode('utf-8')
                if not data:
                    break
                output += data.strip()
                #sys.stdout.write(data)
                sys.stdout.flush()

                # Check for the prompt in the accumulated output
                if check_string in output:
                    found_prompt = True
                    # passwd = getpass.getpass("VM password: ")

                    try:
                        # Use the passed in function call to get
                        # the password instead of getpass.getpass()
                        passwd = get_my_pass()
                        #break
                        # Send the password
                        #os.write(master, b"your_password\n")
                        os.write(master, f"{passwd}\n".encode())
                    except Exception as err:
                        raise("can't acquire the password, and input it to the command")
                # Clear the output buffer to avoid re-matching the prompt
                output = ""

            except OSError:
                break

    if found_prompt:
        os.close(master)
        found_prompt = True
        # print("FOUND PROMPT")

    else:
        # Read any remaining output
        try:
            while True:
                data = os.read(master, 1024).decode('utf-8')
                if not data:
                    break
                sys.stdout.write(data)
                sys.stdout.flush()
        except OSError:
            pass

        # Close the master fd
        os.close(master)   

    return found_prompt, output


#############################################################################


class RunThread(threading.Thread):
    """
    Use a thread & subprocess.Popen to run something

    To use - where command could be an array, or a string... :

    run_thread = RunThread(<command>, message_level)
    run_thread.start()
    run_thread.join()
    print run_thread.stdout
    """
    def __init__(self, command, logger, myshell=False):
        """
        Initialization method
        """
        self.command = command
        self.logger = logger
        self.retout = None
        self.reterr = None
        self.shell = myshell
        threading.Thread.__init__(self)

        if isinstance(self.command, list):
            self.shell = True
            self.printcmd = " ".join(self.command)
        if isinstance(self.command, (str,)):
            self.shell = False
            self.printcmd = self.command

        if isinstance(logger, type(CyLogger)):
            self.logger = logger
        else:
            raise NotACyLoggerError("Passed in value for logger " +
                                    "is invalid, try again.")

        self.logger.log(lp.INFO, "Initialized runThread...")

    ##########################################################################

    def run(self):
        if self.command:
            try:
                p = Popen(self.command, stdout=PIPE,
                                        stderr=PIPE,
                                        shell=self.shell)
                self.retout, self.reterr = p.communicate()
                self.logger.log(lp.WARNING, "Finished \"run\" of: " +
                                str(self.command))
            except SubprocessError as err:
                self.logger.log(lp.WARNING, "Exception trying to open: " +
                                str(self.command))
                self.logger.log(lp.WARNING, traceback.format_exc())
                self.logger.log(lp.WARNING, str(err))
                raise err
            else:
                try:
                    self.retout, self.reterr = p.communicate()
                except SubprocessError as err:
                    self.logger.log(lp.WARNING, "Exception trying to open: " +
                                    str(self.printcmd))
                    self.logger.log(lp.WARNING, "Associated exception: " +
                                    str(err))
                    raise err
                else:
                    self.logger.log(lp.WARNING, "Finished \"run\" of: " +
                                    str(self.printcmd))

    ##########################################################################

    def getStdout(self):
        """
        Getter for standard output
        """
        self.logger.log(lp.INFO, "Getting stdout...")
        return self.retout

    ##########################################################################

    def getStderr(self):
        """
        Getter for standard err
        """
        self.logger.log(lp.DEBUG, "Getting stderr...")
        return self.reterr

##############################################################################

def runMyThreadCommand(cmd, logger, myshell=False):
    """
    Use the RunThread class to get the stdout and stderr of a command
    """
    retval = None
    reterr = None
    if not isinstance(logger, type(CyLogger)):
        raise NotACyLoggerError("Passed in value for logger is invalid, try again.")
    print(str(cmd))
    print(str(logger))
    if cmd and logger:
        run_thread = RunThread(cmd, logger, myshell)
        run_thread.start()
        # run_thread.run()
        run_thread.join()
        retval = run_thread.getStdout()
        reterr = run_thread.getStderr()
    else:
        logger.log(lp.INFO, "Invalid parameters, please report this as a bug.")

    return retval, reterr

