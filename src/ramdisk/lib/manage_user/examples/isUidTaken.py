#!/usr/bin/env -S python -u


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

parser = OptionParser(usage="\n\n%prog [options]\n\n", version="2.8.6")

myuid=""
parser.add_option("-u", "--uid", dest="myuid",
                  default=str(myuid),
                  help="Name of the user you want to create")
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

if not opts.myuid:
    print("Need a uid, please minimally give uid argument")
    parser.print_help()
    sys.exit(1)
else:
    myuid = opts.myuid

level = lp.DEBUG

logger = CyLogger(level)
logger.initializeLogs()

#####
# Put Creating User functionality here...

mu = ManageUser(logger)

uidTaken = mu.uidTaken(myuid)

print(str(uidTaken))


