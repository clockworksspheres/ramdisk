#!/usr/bin/python3

import subprocess
import re
import traceback
from subprocess import Popen
import os
import sys
appendDir = "/".join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-3])
sys.path.append(appendDir)
####
# import ramdisk libraries
#--- non-native python libraries in this source tree
import ramdisk
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.run_commands import RunWith
class FsHelpers(object):
    """
    """
    def __init__(self):
        """
        """
        #self.logger = CyLogger()
        #self.runner = RunWith()

    def getFsBlockSize(self, path="c:"):
        """
        """
        success = False
        blockSize = 0
        # Run logic or command to get block size        
        """
                    cmd = [self.diskutil, "mount", "-mountPoint",
                           self.mntPoint, self.devPartition]
                    self.runWith.setCommand(cmd)
                    self.runWith.communicate()
                    retval, reterr, retcode = self.runWith.getNlogReturns()

                    if not reterr:
                        success = True
        """
        cmd = ["fsutil", "fsinfo", "ntfsinfo", path]
        self.runner.setCommand(cmd)
        self.runner.communicate()
        retval, reterr, retcode = self.runner.getNlogReturns()

        print(retval)

        return success, blockSize

if __name__=="__main__":
    fshelpers = FsHelpers()
    success, blocksize = fshelpers.getFsBlockSize()
    print("success = " + str(success) + " , " + "blocksize = " +  str(blocksize))

    #####
    # Include the parent project directory in the PYTHONPATH
    appendDir = "/".join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-3])
    print(appendDir)
