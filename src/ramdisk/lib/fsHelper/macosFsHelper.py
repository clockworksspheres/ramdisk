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
from ramdisk.lib.environment import Environment
from ramdisk.lib.CheckApplicable import CheckApplicable
from ramdisk.commonRamdiskTemplate import NotValidForThisOS


class FsHelper(object):
    """
    """
    def __init__(self):
        """
        """
        #####
        # Version/timestamp is
        # <YYYY><MM><DD>.<HH><MM>
        # in UTC time
        self.module_version = '20241204.1408'
        self.logger = CyLogger()
        self.environ = Environment()
        self.chkApp = CheckApplicable(self.environ, self.logger)

        #####
        # Check applicability to the current OS
        macApplicable = {'type': 'white',
                         'family': ['darwin'],
                         'os': {'macOS': ['12.1', '+']}}
        """
        macApplicableHere = self.chkApp.isApplicable(macApplicable)

        if macApplicableHere:
            print(getFsBlockSize())
            
        else:
            raise NotValidForThisOS("Ramdisk not available here...")
        """

    def getFsBlockSize(self, size="default"):
        """
        """
        success = False
        blockSize = 0
        # Run logic or command to get block size        

        ####
        # default
        if re.match("default", size):
            blockSize = 512
            success = True
        elif size == 1024 or size == "1024":
            blockSize = 1024
        else:
            success = False

        return success, blockSize

if __name__=="__main__":
    fshelpers = FsHelper()
    success, blocksize = fshelpers.getFsBlockSize()
    print("success = " + str(success) + " , " + "blocksize = " +  str(blocksize))


