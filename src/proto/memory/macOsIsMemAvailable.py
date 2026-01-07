import re
import sys

sys.path.append("../..")

from ramdisk.lib.run_commands import RunWith
from ramdisk.lib.loggers import LogPriority as lp
from ramdisk.lib.loggers import CyLogger
from ramdisk.lib.libHelperExceptions import MemoryNotAvailableError

logger = CyLogger()
logger.initializeLogs()
runWith = RunWith(logger)

def __isMemAvailable(diskSize) :
    """
    """
    print("diskSize: " + str(diskSize))
    logger.log(lp.DEBUG, "diskSize: " + str(diskSize))
    success = False
    line = ""
    free = 0
    freeNumber = 0
    freeMagnitute = ""
    tmpFree = ""

    #####
    # Set up and run the command
    cmd = ["/usr/bin/top", "-l", "1"]

    runWith.setCommand(cmd)
    output, _, _ = runWith.communicate()
    # output, _, _ = self.runWith.waitNpassThruStdout("Networks")

    for line in output.splitlines():

        tmpData = line.split()
        try:
            lastWord = tmpData[-1]
            nextWord = tmpData[-2]
        except IndexError as err:
            pass # self.logger.log(self.lp.DEBUG, )
            continue

        print("words: " + lastWord + " : " + nextWord)
        logger.log(lp.DEBUG, "words: " + lastWord + " : " + nextWord)
        if re.search("unused", line):
            tmpFree = nextWord
            break
    logger.log(lp.DEBUG, "tmpFree: " + str(tmpFree))

    if tmpFree:
        sizeCompile = re.compile(r"(\d+)(\w+)")

        split_size = sizeCompile.search(tmpFree)
        freeNumber = split_size.group(1)
        freeMagnitude = split_size.group(2)

        freeNumber = str(freeNumber).strip()
        freeMagnitude = str(freeMagnitude).strip()

        print(" free Number: " + freeNumber)
        print(" free Magnitude: " + freeMagnitude)
        if re.match(r"^\d+$", freeNumber.strip()):
            if re.match(r"^\w$", freeMagnitude.strip()):

                #####
                # Calculate the size of the free memory in Megabytes
                if re.search("G", freeMagnitude.strip()):
                    freeMem = 1024 * int(freeNumber)
                    freeNumber = str(freeMem)
                    free = freeNumber
                    freeMagnitude = "M"
                elif re.search("M", freeMagnitude.strip()):
                    free = freeNumber.strip() 
    print("Free Memory: " + str(free))
    print("disk size:   "  + str(diskSize))
    logger.log(lp.DEBUG, "Free Memory: " + str(free))
    logger.log(lp.DEBUG, "disk size:   "  + str(diskSize))
    # if int(self.free) > int(float(self.diskSize)/(2*1024)):
    if int(free) > int(float(diskSize)):
        success = True
    else:
        raise MemoryNotAvailableError("Memory Not Available for Creating the Ramdisk, Free up Memory to Create a Ramdisk...")

    # return freeNumber, freeMagnitude
    return success


###########################################################################


if __name__=="__main__":

    print("Started....")
    size = "512"
    if __isMemAvailable(size):
        print("Memory is available!!")
    else:
        print("Memory is NOT AVAILABLE....")
    print("Ended......")

