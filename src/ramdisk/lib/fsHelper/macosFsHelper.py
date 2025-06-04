#!/usr/bin/python3
import subprocess
import re
import traceback
from subprocess import Popen
import os
import sys

if __name__ == "__main__":
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

        self.rw = RunWith(self.logger)

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
        if re.match("default", str(size)):
            blockSize = 512
            success = True
        elif size == 512 or size == "512":
            blockSize = 512
            success = True
        elif size == 1024 or size == "1024":
            blockSize = 1024
            success = True
        else:
            success = False

        return success, blockSize

    def getDiskSizeInMb(self, size="0"):
        """
        size:  when size is given without postfix, it is assumed to be in 
               megabytes, otherwise it is in terms of postfix Gb, gb, Mb, mb.
               Larger (Tb, Pb, etc) could be supported, and the base (currently 
               megabyte) could be changed to suit the user.

               when getting input for the size of the ramdisk, use 
               regex d+[GgMm][Bb] for size

        """
        success = False
        diskSizeInMb = "0"
        # Run logic or command to get disk size in megabytes
        print(str(size)) 
        try:
            match = re.match(r"^(\d+)([MmGg][Bb])", str(size))
            diskSizeTmp = match.group(1)
            diskSizePostfix = match.group(2)
            diskSizeInMb = diskSizeTmp
            if re.match(r"^[Gg][Bb]", diskSizePostfix):
                #####
                # Make the disk size in terms of Mb
                numerator = 1024 * 1024 * int(diskSizeTmp)
                denominator = 512 # sector size
                diskSizeInMb = numerator / denominator # for hdiutil command
        except AttributeError as err:
            try:
                match = re.match(r"^(\d+)$", str(size))
                diskSizeInMb = match.group(0)
            except AttributeError as err:
                self.logger.log(lp.DEBUG, "Unexpected input, size input when only numbers is only in calculated in megabytes...")
                self.logger.log(lp.DEBUG, "Or possibly, unexpected input, size input must be XXXXSS where XXXX is decimal value and SS is either Mb or Gb")
                raise(err)
            except Exception as err:
                print(traceback.format_exc())
                raise(err)
        except Exception as err:
            print(traceback.format_exc())
            raise(err)
        """
        diskSizeTmp = match.group(1)
        diskSizePostfix = match.group(2)
        diskSizeInMb = diskSizeTmp
        if re.match(r"^[Gg][Bb]", diskSizePostfix):
            #####
            # Make the disk size in terms of Mb
            diskSizeInMb = 1024 * int(diskSizeTmp)
        """
        print(diskSizeInMb)
        # print(diskSizePostfix)

        return success, diskSizeInMb


    def validateUser(self, user=""):
        """
        """
        success = False
        message = ""

        # Handling User ID validation
        if not user:
            message = "Value not passed in for User validation"
        elif isinstance(user, str):
            # perform a 're' check to see if it's a decimal string
            if re.match("\d+", user):
                # Check to see if it's a valid uid on the system
                user = int(user.strip())
            elif re.match("\w+", user):
                # look for username in list of valid users on the system
                cmd = ["/usr/bin/dscl", ".", "-list", "/Users"]
                self.rw.setCommand(cmd)
                output, _, _ = self.rw.communicate()

                for item in output.split("\n"):
                    if re.match("^_\w.+"):
                        continue
                    not_allowed = ["daemon", "root", "nobody"]
                    if item in not_allowed:
                        continue

                    if item.strip() == user.strip():
                        success = True
                        break
        # Take into account that the user string above could be converted cleanly to an int
        if isinstance(user, int):
            cmd = ["/usr/bin/dscl", ".", "-list", "/Users"]
            self.rw.setCommand(cmd)
            output, _, _ = self.rw.communicate()
            for account in output.split("\n"):
                if re.match("^_\w.+"):
                    continue
                elif re.match("\w.+"):
                    cmd = ["/usr/bin/dscl", ".", "-read", "/Users/" + account, "uid"]
                    self.rw.setCommand(cmd)
                    output, _, _ = self.rw.communicate()
                    if re.search("ERROR", output, re.IGNORECASE):
                        success = False
                        message = "Not a valid user on this system"
                    else:
                        uid = output.split()[-1]
                        message("User uid" + str(uid) + " found")
                        break
                else:
                    message = "Valid user not found"
                    success = False
            else:
                message = "Not valid input for the user parameter"
                success = False
        else:
            message = "Not valid input for the user parameter"
            success = False
        return success, message

        

    def validateGroup(self, user, group):
        """
        """
        success = False
        message = ""

        success, message = self.validateUser(user)

        if success:
            cmd = ["/usr/bin/id", "-Gn", user]
            self.rw.setCommand(cmd)
            output, _, _ = self.rw.communicate()

            for accountGroup in output.split():
                if re.match("^_\w.+"):
                    message = "Not a valid Group"
                    success = False
                elif re.search("ERROR", accountGroup, re.IGNORECASE):
                    message = "Not a valid Group"
                    success = False
                elif accountGroup.strip() == group.strip():
                    message = "Found a valid group for this user."
                    success = False
                else:
                    message = "Not a valid group for this user"
                    success = False

        return success, message

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
                message = "Path is valid, proceeding."
                success = True
            else:
                message = "Path non-existent, or you don't have permission to it."
        else:
            message = "Path parameter needs to be a valid type"

        return success, message


    def chown_recursive(path, uid, gid):
        """
        Recursively change the owner and group id of a directory and its contents.
        """
        try:
            # Change the owner and group id of the current path
            os.chown(path, uid, gid)
            
            # If the path is a directory, iterate over its contents
            if os.path.isdir(path):
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    self.chown_recursive(item_path, uid, gid)
        except Exception as e:
            print(f"Error changing ownership of {path}: {e}")

    def chown(path, user, group=None, withRoot=False, permissions=None, recursive=True):
        """
        """
        success = False
        worked = False
        message = ""
        uid = ""
        gid = ""


        worked, message = self.validatePath(path)
        self.logger.log(lp.DEBUG, message)
        if not worked:
            return success, message


        # handling 'user' input value
        worked, message = self.validateUser(user)
        self.logger.log(lp.DEBUG, message)
        if not worked:
            return success, message


        # Handling Group ID validation
        worked, message = self.validateGroup(user)
        self.logger.log(lp.DEBUG, message)
        if not worked:
            return success, message
        
        self.chown_recursive(path, uid, gid)


if __name__=="__main__":
    fshelper = FsHelper()
    success, blocksize = fshelper.getFsBlockSize()
    print("success = " + str(success) + " , " + "blocksize = " +  str(blocksize))

    success, diskSizeInMb = fshelper.getDiskSizeInMb("1gb")

    print("success = " + str(success) + " , " + "diskSizeInMb = " +  str(diskSizeInMb))


