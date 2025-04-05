
import sys

sys.path.append("../../..")

#--- non-native python libraries in this source tree
# from ramdisk.lib.dev.getMemStatusTemplate import GetMemStatusTemplate

if sys.platform.startswith("linux"):
    from ramdisk.lib.dev.getLinuxMemStatus import GetLinuxMemStatus
elif sys.platform.startswith("darwin"):
    from ramdisk.lib.dev.getMacosMemStatus import GetMacosMemStatus
elif sys.platform.startswith("win32"):
    pass
else:
    pass


class GetMemStatus(object):
    def __init__(self):
        """
        """
        if sys.platform.startswith("linux"):
            self.getMemStatus = GetLinuxMemStatus()
            pass
        elif sys.platform.startswith("darwin"):
            self.getMemStatus = GetMacosMemStatus()
        elif sys.platform.startswith("win32"):
            #self.getMemStatus = GetWin32MemStatus()
            pass
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
