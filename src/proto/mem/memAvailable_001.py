#!/usr/bin/env -S python -u
"""
"""
import re
import sys

sys.path.append("../..")

from ramdisk.lib.run_commands import RunWith


def isMemAvailable() :
    """ 
    """
    rw = RunWith()
    success = False
    line = ""
    free = 0 
    freeNumber = 0 
    freeMagnitude = ""

    #####
    # Set up and run the command
    if sys.platform == "darwin":
        cmd = ["/usr/bin/top", "-l", "1"]
        lookingFor = "unused"

    rw.setCommand(cmd)
    # output, _, _ = rw.waitNpassThruStdout("Networks")
    output, _, _ = rw.communicate()

    for line in output.splitlines():
        tmpData = line.split()
        lastWord = tmpData[-1]
        nextWord = tmpData[-2]

        print(f"words: " + lastWord + ", " +  nextWord)
        if re.search(lookingFor, line):
            free = nextWord
            break

    print("\n\nFree: " + free)

    #####
    # Find the numerical value and magnitute of the ramdisk
    if free:
        sizeCompile = re.compile(r"(\d+)(\w+)")

        split_size = sizeCompile.search(free)
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
                        freeMem = 1024 * int(freeNumber)
                        freeNumber = str(freeMem)
                    elif re.search("M", freeMagnitude.strip()):
                        free = freeNumber


    print("Free: " + freeNumber + " " + freeMagnitude)

    return freeNumber, freeMagnitude


if __name__=="__main__":
    freeNumber, freeMagnitude = isMemAvailable()

