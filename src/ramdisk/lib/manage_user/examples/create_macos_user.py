#!/usr/bin/env -S python -u


"""


This script must be run with sudo to work....

To see if the user has been created:

  dscl . list /Users

To delete that user:

  sudo dscl . delete /Users/don

"""

#--- Native python libraries
import sys
import time
import traceback
from getpass import getpass
from optparse import OptionParser

sys.path.append("../../../..")
#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.config import DEFAULT_LOG_LEVEL
from ramdisk.lib.libHelperExceptions import UnsupportedOSError
from ramdisk.lib.manage_user.manage_user import ManageUser
from ramdisk.lib.manage_user.manage_user_exceptions import UserExistsError, UserCreationUnsuccessfullError

#####
# Load OS specific Ramdisks
if sys.platform.startswith("darwin"):
    #####
    # For Mac
    from ramdisk.macRamdisk import RamDisk
elif sys.platform.startswith("linux"):
    #####
    # For Linux
    print("'Linux: " + str(sys.platform) + "' platform not supported...")
    raise(UnsupportedOSError)
elif sys.platform.startswith("win32"):
    #####
    # For Windows
    print("'Windows: " + str(sys.platform) + "' platform not supported...")
    raise(UnsupportedOSError)
else:
    print("'" + str(sys.platform) + "' platform not supported...")
    raise(UnsupportedOSError)

parser = OptionParser(usage="\n\n%prog [options]\n\n", version="2.8.6")

user=""
parser.add_option("-u", "--user", dest="user",
                  default=str(user),
                  help="Name of the user you want to create")
parser.add_option("-p", "--password", action="store_true", dest="password",
                  default=0, help="Ask for a password prompt")
parser.add_option("-d", "--debug", action="store_true", dest="debug",
                  default=0, help="Print debug messages")
parser.add_option("-v", "--verbose", action="store_true",
                  dest="verbose", default=0,
                  help="Print status messages")

(opts, args) = parser.parse_args()

if opts.verbose != 0:
    level = lp.INFO
elif opts.debug != 0:
    level = level=lp.DEBUG
else:
    level=DEFAULT_LOG_LEVEL

if not opts.user:
    print("Need a username, please minimally give username argument")
    parser.print_help()
    sys.exit(1)
else:
    user = opts.user

def getPass():
    password = getpass("Enter your password: ")
    password2 = getpass("Verify your password: ")
    
    if password == password2:
        return password
    else:
        getPass()

if opts.password:
    password = getPass()    

logger = CyLogger(level)
logger.initializeLogs()

#####
# Put Creating User functionality here...

mu = ManageUser(logger)

#####
# see if user exists
try:
    if mu.getUser(user):
        raise(UserExistsError)
    else:
        logger.log(lp.INFO, "No user of this name exists, good to go...")
except UserExistsError as err:
    print("Cannot create this user, exiting... try a different username")
    sys.exit()
except NameError as err:
    print("Name does not exists, go ahead...")
except Exception as err:
    print(traceback.format_exc())

try:
    mu.createStandardUser(user, password)
except UserCreationUnsuccessfullError as err:
    print("User Creation Unsuccessful, exiting... Check the system logs for more information...")
    print(traceback.format_exc())
    sys.exit()

print("Good to go: " + str(user) + " created!") 


####



