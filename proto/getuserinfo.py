#!/usr/bin/python

from lib.manage_user.macos_user import MacOSUser
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp

logger = CyLogger(debug_mode=True)
logger.initializeLogs()

mu = MacOSUser(logDispatcher=logger)

user = raw_input("User to collect properties for: ")

success, userProperties = mu.getUserProperties(str(user))

print str(userProperties)
'''
for key, value in userProperties.iteritems():
    if not re.search("JPEG", key):
        print key + " : " + value
'''

