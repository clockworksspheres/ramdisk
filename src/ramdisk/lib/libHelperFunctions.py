"""
Helper functions, OS agnostic


"""

#--- Native python libraries
import re
import os
import sys
import time
import ctypes
if sys.platform.lower().startswith("win32"):
    print("importing termios not supported on Windows")
else:
    import termios
import traceback
from subprocess import Popen, STDOUT, PIPE
from pathlib import Path

sys.path.append(Path(__file__).parent.parent)

#--- non-native python libraries in this source tree
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp
from lib.run_commands import RunWith
from lib.libHelperExceptions import UnsupportedOSError

logger = CyLogger()
run = RunWith(logger)

###########################################################################

class FoundException(Exception) :
    """
    Exeption to raise when the condition is met in a for/while

    Accompanying code (in collect_for_hostmaster.py) derived from example
    in "Rapid GUI Programming with Python and QT" pgs 66 - 71, 
    by Mark Summerfeild
    
    For more examples on python user defined exceptions:
    http://docs.python.org/2/tutorial/errors.html
    """
    pass

##############################################################################

def get_console_user():
    """
    Get the user that owns the console on macOS or Linux.
    Returns False if no valid username is found.
    """

    if sys.platform.lower().startswith("darwin"):
        # macOS command
        cmd = ["/usr/bin/stat", "-f", "%Su", "/dev/console"]
    elif sys.platform.lower().startswith("linux"):
        cmd = ["stat", "-c", "%U", "/dev/console"]
    else:
        raise UnsupportedOSError("Function not supported on this OS")
        
    try:
        retval = Popen(cmd, stdout=PIPE, stderr=STDOUT).communicate()[0]

        # Properly decode bytes
        decoded = retval.decode("utf-8", errors="ignore").strip()

        # Remove stray quotes if present
        decoded = decoded.strip("'").strip('"')

    except Exception as err:
        logger.log(lp.VERBOSE, "Exception trying to get the console user...")
        logger.log(lp.VERBOSE, "Associated exception: " + str(err))
        logger.log(lp.WARNING, traceback.format_exc())
        logger.log(lp.WARNING, str(err))
        raise

    # Accept realistic usernames:
    # letters, digits, underscore, hyphen, dot
    if re.match(r"^[A-Za-z][A-Za-z0-9._-]*$", decoded):
        logger.log(lp.VERBOSE, f"user: {decoded}")
        return decoded

    logger.log(lp.VERBOSE, "user: False")
    return False

###########################################################################


def touch(filename=""):
    """
    Python implementation of the touch command..
    
    """
    if re.match(r"^\s+$", filename) :
        logger.log(lp.INFO, "Cannot touch a file without a filename....")
    else :
        try:
            os.utime(filename, None)
        except:
            try :
                open(filename, 'a').close()
            except Exception as err :
                logger.log(lp.INFO, "Cannot open to touch: " + str(filename))

###########################################################################

def getecho (fileDescriptor):
    """This returns the terminal echo mode. This returns True if echo is
    on or False if echo is off. Child applications that are expecting you
    to enter a password often set ECHO False. See waitnoecho().

    Borrowed from pexpect - acceptable to license
    """
    attr = termios.tcgetattr(fileDescriptor)
    if attr[3] & termios.ECHO:
        return True
    return False

############################################################################

def waitnoecho (fileDescriptor, timeout=3):
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
        if not getecho(fileDescriptor):
            return True
        if timeout < 0 and timeout is not None:
            return False
        if timeout is not None:
            timeout = end_time - time.time()
        time.sleep(0.1)

###########################################################################

def isSaneFilePath(filepath):
    """
    Check for a good file path in the passed in string.
    
    
    """
    sane = False
    if filepath and isinstance(filepath, str):
        if re.match(r"^[A-Za-z0-9_\-/\.]+$", filepath):
            sane = True
    return sane

###########################################################################

