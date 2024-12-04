#!/usr/bin/python3

import subprocess
import re
import traceback
from subprocess import Popen
import os
import sys

sys.path.append("../../..")

####
# import ramdisk libraries
#--- non-native python libraries in this source tree
import ramdisk
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.run_commands import RunWith


class FsHelper(object):
    """
    """
    def __init__(self):
        """
        """
        self.logger = CyLogger()
        self.runner = RunWith()

    def getFsBlockSize(self, path="c:"):
        """
        path:  path could be a drive, with a colon, or a full path - drive, plus path to
               a mount point, ie, directory.

        """
        success = False
        blockSize = 0
        # Run logic or command to get block size        

        cmd = ["fsutil", "fsinfo", "ntfsinfo", path]
        self.runner.setCommand(cmd)
        self.runner.communicate()
        retval, reterr, retcode = self.runner.getNlogReturns()
       
        lines = retval.split("\n")

        for line in lines:
            try:
                match = re.match(r"Bytes Per Cluster\s+[:;]\s+(\d+).*", line)
                blockSize = match.group(1)
                # print(blockSize)
                success = True
                break
            except:
                pass
                
        return success, blockSize

if __name__=="__main__":
    fshelpers = FsHelpers()
    success, blocksize = fshelpers.getFsBlockSize()
    print("success = " + str(success) + " , " + "blocksize = " +  str(blocksize))




