#!/usr/bin/python3

import subprocess
import re
import traceback
from subprocess import Popen
from subprocess import SubprocessError as SubprocessError
import os
import sys

#####
# Include the parent project directory in the PYTHONPATH
appendDir = "/".join(os.path.abspath(os.path.dirname(__file__)).split('/')[:-3])
sys.path.append(appendDir)

#--- non-native python libraries in this source tree

from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.run_commands import RunWith
from ramdisk.lib.environment import Environment
from ramdisk.lib.CheckApplicable import CheckApplicable

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
        #self.chkApp = CheckApplicable(self.environ, self.logger)
        self.rw = RunWith(self.logger)
        #####
        # Check applicability to the current OS
        #linuxApplicable = {'type': 'white',
        #                 'family': ['linux']}

    def getFsBlockSize(self, size="default"):
        """
        blockdev --getsize /dev/sda
        
        returns: block size in bits
        
        """
        runcmd = ["/usr/sbin/blockdev", "--getsize", "/dev/sda"]

        blockSize = 0

        try:
            self.rw.setCommand(runcmd)
            # def waitNpassThruStdout(self, chk_string=None, respawn=False, silent=True)
            (myout, myerr, myretcode) = self.rw.waitNpassThruStdout(chk_string=None, respawn=False, silent=True)
            blockSize = myout
        except SubprocessError as Err:
            self.logger.log(lp.WARNING, traceback.format_exc())
            self.logger.log(lp.WARNING, "Exception thrown trying to find free space on device: " + dev + " assumed fstype: " + fstype)

        return blockSize

    def getFsSectorSize(self, size="default"):
        """
        
        Linux:
        
        output of fdisk -l, looking for the line where:
        
        Units: sectors of 1 * 512 = 512 bytes
        Units: sectors of (variable) * (variable) = (block size) bytes    

        Same across debian based and redhat based systems
        
        returns: sector size in bits

        """
        runcmd = ["/usr/sbin/fdisk", "-l"]

        sectorSize = 0

        try:
            self.rw.setCommand(runcmd)
            # def waitNpassThruStdout(self, chk_string=None, respawn=False, silent=True)
            (myout, myerr, myretcode) = self.rw.waitNpassThruStdout(chk_string=None, respawn=False, silent=True)
            for line in myout.split('\n'):
                # print(line.strip())
                try:
                    line = line.strip()
                    print(line)
                    # Units: sectors of 1 * 512 = 512 bytes
                    # Units: sectors of (variable) * (variable) = (block size) bytes
                    #
                    tmpvar = line.split("=")
                    tmpvar2 = tmpvar[1].split()
                    sectorSize = tmpvar2[0]
                    print(sectorSize)
                    if sectorSize:
                        break
                except:
                    continue 
        except SubprocessError as Err:
            self.logger.log(lp.WARNING, traceback.format_exc())
            self.logger.log(lp.WARNING, "Exception thrown trying to find free space on device: " + dev + " assumed fstype: " + fstype)

        return str(int(sectorSize) * 8)

    def getDiskSizeInMb(self, size="0"):
        """
        size:  when size is given without postfix, it is assumed to be in 
               megabytes, otherwise it is in terms of postfix Gb, gb, Mb, mb.
               Larger (Tb, Pb, etc) could be supported, and the base (currently 
               megabyte) could be changed to suit the user.

               when getting input for the size of the ramdisk, use 
               regex d+[GgMm][Bb] for size

        """
        pass
 

if __name__=="__main__":
    fshelper = FsHelper()
    sectorSize = fshelper.getFsSectorSize()
    print("Sector Size = " +  str(sectorSize))

    # fshelper = FsHelper()
    blockSize  = fshelper.getFsBlockSize()
    print("Block Size = " +  str(blockSize))
        
    #success, diskSizeInMb = fshelper.getDiskSizeInMb("1gb")

    #print("success = " + str(success) + " , " + "diskSizeInMb = " +  str(diskSizeInMb))
    
    print("done....")


