#!/usr/bin/python3

import os
import re
import sys

sys.path.append("../../..")

from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp

class FsHelperTemplate(object):
    """
    """
    def __init__(self, logger, **kwargs):
        """
        """
        if not logger and isinstance(logger, CyLogger):
            self.logger = CyLogger()
            self.logger.initializeLogs()
        else:
            self.logger.initializeLogs()

    def getFsBlockSize(self):
        """
        """
        success = False
        blockSize = 0
        # Run logic or command to get block size        

        return success, blockSize

    def getDiskSize(self):
        """
        """
        success = False
        diskSize = 0
        # Run logic or command to get disk size       

        return success, diskSize

    def getSizeInMb(self):
        """
        """
        success = False
        diskSizeInMb = 0
        # Run logic or command to get disk size in megabytes       

        return success, diskSizeInMb
    
    def chown(self, path, user, group=None, withRoot=False, permissions=None, recursive=True):
        """

        """
        success = False
        return success

    def validatePath(self, path):
        """
        """
        success = False

        # Handling str based path validation
        if not path:
            message = "Path passed in is not valid"
        elif isinstance(path, str):
            # Check if the path is a valid path on the system.
            if os.path.exists(path):
                # valid characters are alpha-numeric and "/", "\", '"' and space
                if re.match(r'[a-zA-Z0-9/ "\\]+', path):
                    success = True

                    message = "Path is valid, proceeding."
                else:
                    message = "Path has invalid characters..."
            else:
                message = "Path non-existent, or you don't have permission to it."
        else:
            message = "Path parameter needs to be a valid type"

        self.logger.log(lp.DEBUG, message)
        return success, message

    def mkdirs(self, path):
        """
        python 3.2 or greater only
        """
        if self.validatePath(path):
            try:
                os.makedirs(path, exist_ok=True)
                self.logger.log(lp.DEBUG, "Directory created successfully")
            except OSError as error:
                self.logger.log(f"Error: {error}")
        return True, path


if __name__=="__main__":
    fshelpers = FsHelpers()
    success, blocksize = fshelpers.getFsBlockSize()
    print("success = " + str(success) + " , " + "blocksize = " +  str(blocksize))


