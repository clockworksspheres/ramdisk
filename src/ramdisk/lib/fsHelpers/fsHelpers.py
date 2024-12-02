#!/usr/bin/python3

class FsHelpers(object):
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

if __name__=="__main__":
    fshelpers = FsHelpers()
    success, blocksize = fshelpers.getFsBlockSize()
    print("success = " + str(success) + " , " + "blocksize = " +  str(blocksize))


