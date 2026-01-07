
#####
# System Libraries
import sys


#####
# Custom package libraries.
from lib.loggers import CyLogger
from lib.loggers import LogPriority as lp
from lib.CheckApplicable import CheckApplicable
from lib.libHelperExceptions import UnsupportedOSError, NotACyLoggerError

class ManageUsers(object):
    """
    Class for managing groups of users
    
    
    """
    def __init__(self, logger):
        """
        
        """
        #####
        # Set up logging
        if isinstance(logger, CyLogger):
            self.logger = logger
        else:
            raise NotACyLoggerError("Passed in value for logger is invalid, try again.")
        self.logger.log(lp.INFO, "Logger: " + str(self.logger))
        '''
        if sys.platform.lower() == "darwin":
            from lib.manage_users import manage_macos_users 
            # import lib.manage_user.macos_user
            self.userMgr = manage_macos_users.MacOSUsers(logDispatcher=self.logger)
        else:
            raise UnsupportedOSError("This operating system is not supported...")
        '''
        users = {}
        
    def getAllUsers(self):
        """
        
        """
        pass

    def getUsers(self):
        """
        
        """
        pass

    def getUser(self):
        """
        
        """
        pass
    def getUserProperty(self):
        """
        
        """
        pass

    def getUserProperties(self):
        """
        
        """
        pass

    def getUsersProperty(self):
        """
        
        """
        pass

    def getUsersProperties(self):
        """
        
        """
        pass
