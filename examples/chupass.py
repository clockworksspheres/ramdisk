#!/usr/bin/python
 
import traceback
import getpass
import sys

sys.path.append("../..")

from ramdisk.lib.manage_user.manage_user import ManageUser
from ramdisk.lib.manage_keychain.manage_keychain import ManageKeychain
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp

logger = CyLogger(debug_mode=True)
logger.initializeLogs()
mu = ManageUser(logger)
mk = ManageKeychain(logger)

username = raw_input("Username: " )
oldPass = getpass.getpass("Password: ")
oneNewPass = getpass.getpass("New Password: ")
twoNewPass = getpass.getpass("Repeat New Password: ")

username = username.strip()
oldPass = oldPass.strip()
oneNewPass = oneNewPass.strip()
twoNewPass = twoNewPass.strip()

upass_success = "huh?"
klock_success = "huh?"
kpass_success = "huh?"

if oneNewPass == twoNewPass:
    logger.log(lp.DEBUG, "One and two match, proceeding...")
    try:
        mu.setUserName(username)
        upass_success = mu.setUserPassword(username, oneNewPass, oldPass)
    except:
        raise Exception(traceback.format_exc())
    print str(upass_success)
    mk.setUser(username)
    keychain = "/Users/" + username + "/Library/Keychains/login.keychain"
    try:
        klock_success = mk.lockKeychain(keychain)
        kpass_success = mk.deleteKeychain(keychain)
        kpass_success = mk.createKeychain(oneNewPass, keychain)
    except Exception:
        message = "Exception attempting to change the " + keychain + \
                  " password.. \n" + traceback.format_exc()
        logger.log(lp.ERROR, message)

    logger.log(lp.DEBUG, str(klock_success) + " : " + str(kpass_success))

else:
    logger.log(lp.DEBUG, "Damn it Jim!! They didn't match!!")

logger.log(lp.DEBUG, str(upass_success) + " : " + str(klock_success) + " : " + str(kpass_success))


