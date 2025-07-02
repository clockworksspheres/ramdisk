
import sys
import re
from subprocess import Popen, PIPE

sys.path.append("../")

#--- non-native python libraries in this source tree
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.loggers import LogPriority as lp

logger = CyLogger()
logger.initializeLogs()

def getMaxDarwinMemSize():
    success = False
    found = False
    almost_size = 0
    size = 0
    free = 0
    line = ""
    freeMagnitude = None

    #####
    # Set up and run the command
    cmd = ["/usr/bin/top", "-l", "1"]

    proc = Popen(cmd, stdout=PIPE, stderr=PIPE)

    while True:
        line = proc.stdout.readline().strip()
        #####
        # Split on spaces
        line = line.split()
        #####
        # Get the last item in the list
        found = line[-1]
        almost_size = line[:-1]
        size = almost_size[-1]

        found = str(found).strip()
        #almost_size = almost_size.strip()
        size = str(size).strip()

        logger.log(lp.INFO, "size: " + str(size))
        logger.log(lp.INFO, "found: " + str(found))

        if re.search("unused", found) or re.search("free", found):
            #####
            # Found the data we wanted, stop the search.
            break
    proc.kill()

    #####
    # Find the numerical value and magnitute of the ramdisk
    if size:
        sizeCompile = re.compile(r"(\d+)(\w+)")

        split_size = sizeCompile.search(size)
        freeNumber = split_size.group(1)
        freeMagnitude = split_size.group(2)
        
        freeNumber = str(freeNumber).strip()
        freeMagnitude = str(freeMagnitude).strip()

        if re.match(r"^\d+$", freeNumber.strip()):
            if re.match(r"^\w$", freeMagnitude.strip()):
                if freeMagnitude:
                    #####
                    # Calculate the size of the free memory in Megabytes
                    if re.search("G", freeMagnitude.strip()):
                        free = 1024 * int(freeNumber)
                        free = str(free)
                    elif re.search("M", freeMagnitude.strip()):
                        free = freeNumber
    logger.log(lp.DEBUG, "free: " + str(free))
    logger.log(lp.DEBUG, "Size requested: " + str(diskSize))
    if int(free) > int(float(diskSize)/(2*1024)):
        success = True
    else:
        raise MemoryNotAvailableError("Memory Not Available for Creating the Ramdisk, Free up Memory to Create a Ramdisk...")

    print(str(free))
    return int(free)

def getMaxWin32MemSize():
    return int("100")

def getMaxLinuxMemSize():
    return int("100")

def getMaxMemSize():
    if sys.platform.startswith("linux"):
        maxMemSize = getMaxLinuxMemSize()
    if sys.platform.startswith("win32"):
        maxMemSize = getMaxWin32MemSize()
    if sys.platform.startswith("darwin"):
        maxMemSize = getMaxDarwinMemSize()
    return maxMemSize 

if __name__=="__main__":

    maxMemSize = getMaxMemSize()

    print(str(maxMemSize))


