#!/usr/bin/python3

import os

class FsHelper(object):
    """
    """
    def __init__(self):
        """
        """
        pass

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
    
    def chown(path, user, group=None, withRoot=False, permissions=None, recursive=True):
        """

        """
        success = False
        return success

        
if __name__=="__main__":
    fshelpers = FsHelpers()
    success, blocksize = fshelpers.getFsBlockSize()
    print("success = " + str(success) + " , " + "blocksize = " +  str(blocksize))


