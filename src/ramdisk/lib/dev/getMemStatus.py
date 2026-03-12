
import sys
from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

parent_dir = Path(__file__).parent
sys.path.append(str(parent_dir))

#--- non-native python libraries in this source tree
# from ramdisk.lib.dev.getMemStatusTemplate import GetMemStatusTemplate

if sys.platform.startswith("linux"):
    from lib.dev.getLinuxMemStatus import GetLinuxMemStatus
elif sys.platform.startswith("darwin"):
    from lib.dev.getMacosMemStatus import GetMacosMemStatus
elif sys.platform.startswith("win32"):
    from lib.dev.getWin32MemStatus import GetWin32MemStatus
else:
    pass


class GetMemStatus(object):
    def __init__(self):
        """
        """
        if sys.platform.startswith("linux"):
            self.getMemStatus = GetLinuxMemStatus()
        elif sys.platform.startswith("darwin"):
            self.getMemStatus = GetMacosMemStatus()
        elif sys.platform.startswith("win32"):
            self.getMemStatus = GetWin32MemStatus()
        else:
            self.getMemStatus = None
 
    def getTotalMemSize(self):
        """
        """
        totalMemSize = self.getMemStatus.getTotalMemSize()
        return int(totalMemSize)


    def getAvailableMem(self):
        """
        """
        availableMem = self.getMemStatus.getAvailableMem()
        return int(availableMem)


if __name__=="__main__":
    getMemStatus = GetMemStatus()
    freeMem = getMemStatus.getAvailableMem()
    totalMem = getMemStatus.getTotalMemSize()
    print("Free Memory: " + str(freeMem))
    print("Total Memory: " + str(totalMem))
