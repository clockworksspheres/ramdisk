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
        self.logger.initializeLogs()
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
        uid = 999999999
        self.logger.log(lp.DEBUG, "User: " + user)
        # print("User: " + user)
        # Handling User ID validation
        if not user:
            message = "Value not passed in for User validation"
        elif isinstance(user, str):
            # perform a 're' check to see if it's a decimal string
            if re.match("\d+", user):
                # Check to see if it's a valid uid on the system
                uid = int(user.strip())
            elif re.match("^\w.+", user.strip()):
                # look for username in list of valid users on the system
                cmd = ["/usr/bin/dscl", ".", "-list", "/Users"]
                self.rw.setCommand(cmd)
                output, _, _ = self.rw.communicate()

                for item in output.split("\n"):
                    #print(item)
                    if re.match("^_\w.+", item):
                        continue
                    not_allowed = ["daemon", "nobody"]
                    if item in not_allowed:
                        continue
                    #print("...ITEM: " + item.strip() + " user: " + user.strip())
                    if item.strip() == user.strip():
                        #print("........FOUND USER.......")
                        cmd = ["/usr/bin/dscl", ".", "-read", "/Users/" + item.strip(), "uid"]
                        self.rw.setCommand(cmd)
                        output, _, _ = self.rw.communicate()
                        self.logger.log(lp.DEBUG, "output: " + output)
                        if re.search("ERROR", output, re.IGNORECASE):
                            success = False
                            message = "Not a valid user on this system"
                        else:
                            tmpuid = output.split()[-1]
                            uid = int(tmpuid)
                            message = ".........User uid " + str(uid) + " found"
                            self.logger.log(lp.DEBUG, message)
                            # print(message)
                            success = True
                            break
        else:
            message = "Not valid input for the user parameter"
            success = False
        # print("...UID: " + str(uid) + " message: " + message + " success: " + str(success))
        return success, message, uid
    
    def getGid(self, group):
        """
        """
        success = False
        gid = 99999999
        message = ""

        cmd = ["/usr/bin/dscl", ".", "-read", "/Groups/" + str(group), "PrimaryGroupID"]
        self.rw.setCommand(cmd)
        output, _, _  = self.rw.communicate()

        try:
            gid = output.split()[-1]
            gid = int(gid)
            message = "Found gid: " + str(gid)
            success = True
        except IndexError:
            message = "Error attempting to get GID"
            success = False
            gid = 20

        return success, message, gid

    def validateGroup4user(self, user, group):
        """
        """
        success = False
        message = ""
        gid = 99999999

        success, message, _ = self.validateUser(user)

        if success:
            cmd = ["/usr/bin/id", "-Gn", user]
            self.rw.setCommand(cmd)
            output, _, _ = self.rw.communicate()

            for accountGroup in output.split():
                # print(".. .. .. AccountGroup: " + accountGroup.strip() + " Group: " + group.strip())
                if re.match("^_\w.+", accountGroup):
                    message = "Not a valid Group"
                    success = False
                elif re.search("ERROR", accountGroup, re.IGNORECASE):
                    message = "Not a valid Group"
                    success = False
                elif accountGroup.strip() == group.strip():
                    message = "Found a valid group for this user."
                    success = True
                    break
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
        success = False
        try:
            # Change the owner and group id of the current path
            os.chown(path, uid, gid)
            
            # If the path is a directory, iterate over its contents
            if os.path.isdir(path):
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    self.chown_recursive(item_path, uid, gid)
                    success = True
        except Exception as e:
            print(f"Error changing ownership of {path}: {e}")
            success = False
        return success

    def chown(path, user, group="staff", withRoot=False, permissions=None, recursive=True):
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

        if group:
            # Handling Group ID validation
            worked, message = self.validateGroup4user(user)
            self.logger.log(lp.DEBUG, message)
            if not worked:
                return success, message
            success, message, gid = self.getGid(group)    
        else:
            gid = 20  # staff on macOS

        self.chown_recursive(path, uid, gid)


if __name__=="__main__":
    fshelper = FsHelper()
    success, blocksize = fshelper.getFsBlockSize()
    print("success = " + str(success) + " , " + "blocksize = " +  str(blocksize))

    success, diskSizeInMb = fshelper.getDiskSizeInMb("1gb")

    print("success = " + str(success) + " , " + "diskSizeInMb = " +  str(diskSizeInMb))


