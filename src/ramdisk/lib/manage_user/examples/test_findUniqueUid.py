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

level = lp.DEBUG

logger = CyLogger(level)
logger.initializeLogs()

#####
# Put Creating User functionality here...

mu = ManageUser(logger)

nextUserNumber = mu.findUniqueUid()
print(str(nextUserNumber))


