#!/usr/bin/env -S python -u
# ! /usr/bin/python

'''
TODO: Fix this example
'''


#--- Native python libraries
import sys

sys.path.append("../")

#--- non-native python libraries in this source tree
from ramdisk.lib.manage_user.macos_user import MacOSUser
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp

logger = CyLogger(debug_mode=True)
logger.initializeLogs()

mu = MacOSUser(logDispatcher=logger)

user = input("User to collect properties for: ")

success, userProperties = mu.getUserProperties(str(user))

print(str(userProperties))

for key, value in userProperties.iteritems():
    if not re.search("JPEG", key):
        print key + " : " + value

