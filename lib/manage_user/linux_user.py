"""
Cross platform user creation and management

Created for testing cross platform user testing for the ramdisk project, 
specifically unionfs functionality.

@author: Roy Nielsen
"""
from __future__ import absolute_import
import re
import os
import pty
import sys
import shutil
from subprocess import Popen

########## 
# local app libraries
from .manage_user_template import ManageUserTemplate
from .manage_user_template import BadUserInfoError
from lib.run_commands import RunWith
from lib.loggers import LogPriority as lp
from lib.loggers import CyLogger
from lib.libHelperExceptions import NotACyLoggerError

class MacOSUser(ManageUserTemplate):
    """
    Class to manage users on Mac OS.

    #----- Getters
    @method findUniqueUid
    @method uidTaken
    @method getUser
    @method getUserShell
    @method getUserComment
    @method getUserUid
    @method getUserPriGid
    @method getUserHomeDir
    @method isUserInstalled
    @method isUserInGroup
    @method authenticate
    #----- Setters
    @method createStandardUser
    @method createBasicUser
    @method setUserShell
    @method setUserComment
    @method setUserUid
    @method setUserPriGid
    @method setUserHomeDir
    @method createHomeDirectory
    @method addUserToGroup
    @method setUserPassword
    @method fixUserHome
    #----- User removal
    @method rmUser
    @method rmUserHome
    @method rmUserFromGroup

    @author: Roy Nielsen
    """
    def __init__(self, logger, userName="", userShell="/bin/bash",
                 userComment="", userUid=1000, userPriGid=20,
                 userHomeDir="/tmp"):
        super(MacOSUser, self).__init__(logger, userName, userShell,
                                         userComment, userUid, userPriGid,
                                         userHomeDir)
        self.module_version = '20160225.125554.540679'
        if isinstance(logger, CyLogger):
            self.logger = logger
        else:
            raise NotACyLoggerError("Passed in value for logger is invalid, try again.")
        self.dscl = "/usr/bin/dscl"
        self.userData = []
        self.runWith = RunWith(self.logger)

    #----------------------------------------------------------------------
    # Getters
    #----------------------------------------------------------------------

    def findUniqueUid(self):
        """
        """
        pass

    #----------------------------------------------------------------------

    def uidTaken(self, uid):
        """
        """
        pass

    #----------------------------------------------------------------------

    def getUser(self, userName=""):
        """
        """
        pass

    #----------------------------------------------------------------------

    def getUserShell(self, userName=""):
        """
        """
        pass

    #----------------------------------------------------------------------

    def getUserComment(self, userName=""):
        """
        """
        pass

    #----------------------------------------------------------------------

    def getUserUid(self, userName=""):
        """
        """
        pass

    #----------------------------------------------------------------------

    def getUserPriGid(self, userName=""):
        """
        """
        pass

    #----------------------------------------------------------------------

    def getUserHomeDir(self, userName=""):
        """
        """
        pass

    #----------------------------------------------------------------------

    def isUserInstalled(self, user=""):
        """
        """
        pass

    #----------------------------------------------------------------------

    def isUserInGroup(self, userName="", groupName=""):
        """
        """
        pass

    #----------------------------------------------------------------------

    def authenticate(self, user="", password=""):
        """
        """
        pass

    #----------------------------------------------------------------------
    # Setters
    #----------------------------------------------------------------------

    def createStandardUser(self, userName, password):
        """
        Creates a user that has the "next" uid in line to be used, then puts
        in in a group of the same id.  Uses /bin/bash as the standard shell.
        The userComment is left empty.  Primary use is managing a user
        during test automation, when requiring a "user" context.

        @author: Roy Nielsen
        """
        pass

    #----------------------------------------------------------------------

    def createBasicUser(self, userName=""):
        """
        Create a username with just a moniker.  Allow the system to take care of
        the rest.

        Only allow usernames with letters and numbers.

        @author: Roy Nielsen
        """
        pass

    #----------------------------------------------------------------------

    def setUserShell(self, user="", shell=""):
        """
        """
        pass

    #----------------------------------------------------------------------

    def setUserComment(self, user="", comment=""):
        """
        """
        pass

    #----------------------------------------------------------------------

    def setUserUid(self, user="", uid=""):
        """
        """
        pass

    #----------------------------------------------------------------------

    def setUserPriGid(self, user="", priGid=""):
        """
        """
        pass

    #----------------------------------------------------------------------

    def setUserHomeDir(self, user="", userHome=""):
        """
        """
        pass

    #----------------------------------------------------------------------

    def addUserToGroup(self, user="", group=""):
        """
        """
        pass

    #----------------------------------------------------------------------

    def rmUserFromGroup(self, user="", group=""):
        """
        """
        pass

    #----------------------------------------------------------------------

    def setUserPassword(self, user="", password=""):
        """
        """
        pass

    #----------------------------------------------------------------------
    # User Property Removal
    #----------------------------------------------------------------------

    def rmUser(self, user=""):
        """
        """
        pass

    #----------------------------------------------------------------------

    def rmUserHome(self, user=""):
        """
        """
        pass

    #----------------------------------------------------------------------

    def fixUserHome(self, userName=""):
        """
        Get the user information from the local directory and fix the user
        ownership and group of the user's home directory to reflect
        what is in the local directory service.

        @author: Roy Nielsen
        """
        pass

    #----------------------------------------------------------------------
    # Unix related OS Specific Methods, uses /etc/password user management
    #----------------------------------------------------------------------

    def acquireUserData(self):
        """
        Acquire local user data that can be found in /etc/password and 
        /etc/shadow.
        
        @author: Roy Nielsen
        """
        success = False
        
        #####
        # Check the UID of the user, only try processing what is available
        # to the uid running this code.
        if not os.getuid() == 0:
            success = self.processEtcPassword()
            if success:
                self.processEtcGroup()
        else:
            success = self.processEtcPassword()
            if success:
                success = self.processEtcGroup()
            if success:
                self.processEtcShadow()

        return success
        
    def processEtcPassword(self):
        """
        Acquire user data from /etc/passwd
        """
        success = False
        userinfo = {}
        #####
        # Process /etc/passwd
        try:
            pass_file = open("/etc/password", 'r')
        except OSError, err:
            self.logger.log(lp.INFO, "Error trying to acquire /etc/password data: " + str(err))
        else:
            for line in pass_file.readlines():
                #####
                # Pull apart the line from the password file to acquire the data
                col = line.split(':')
                userinfo = {}
                user = col[0]
                userinfo['uid'] = col[2]
                userinfo['pgid'] = col[3]
                userinfo['ucomment'] = col[4]
                userinfo['uhome'] = col[5]
                userinfo['ushell'] = col[6]
                #####
                # Put the acquired user data into the class variable
                self.userData[user] = userinfo
            pass_file.close()
            success = True
        return success

    def processEtcShadow(self):
        """
        Acquire user data from /etc/shadow

        @author: Roy Nielsen
        """
        success = False
        #####
        # Process /etc/passwd
        try:
            pass_file = open("/etc/password", 'r')
        except OSError, err:
            self.logger.log(lp.INFO, "Error trying to acquire /etc/shadow data: " + str(err))
        else:
            for line in pass_file.readlines():
                #####
                # Pull apart the line from the password file to acquire the data
                col = line.split(':')
                userinfo = {}
                user = ""
                user = col[0]
                userinfo['lastchanged']    = col[2]
                userinfo['min']   = col[3]
                userinfo['max'] = col[4]
                userinfo['warn']  = col[5]
                userinfo['inactive'] = col[6]
                userinfo['expore']  = col[5]
                #####
                # Put the acquired user data into the class variable
                self.userData[user] = userinfo
            pass_file.close()
            success = True
        return success

    def processEtcGroup(self):
        """
        Acqure a list of groups each user is in
        
        @author: Roy Nielsen
        """
        success = False
        grps = "/usr/bin/groups"

        for user in self.userData:
            #####
            # Run the 'groups <user>' command to acquire the user's groups
            cmd = [grps, user]
            self.runWith.setCommand(cmd)
            self.runWith.communicate()
            retval, reterr, retcode = self.runWith.getNlogReturns()
            #####
            # If there is no error, process the data.
            if not reterr:
                #####
                # Acquire the user's groups from the output
                userGrps = retval.split()
                #####
                # create a dictionary, which will later be added to userData
                # class variable.
                groups = {'groups' : userGrps}
                #####
                # Add the groups the user is a member of.
                self.userData[user] += groups
        return success
