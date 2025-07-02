#!/usr/bin/env -S python -u
"""
"""
import subprocess
import re
import sys

sys.path.append("../../..")

#--- non-native python libraries in this source tree
from ramdisk.lib.dev.getMemStatusTemplate import GetMemStatusTemplate


class GetLinuxMemStatus(GetMemStatusTemplate):
    def __init__(self):
        # super if necessary
        print("linux initialization complete...")

    def getTotalMemSize(self):

        memory_size = 0

        try:
            mem_output = subprocess.run(["free", "-t", "-m"], capture_output=True, text=True, check=True).stdout

            memory_line = next((line for line in mem_output.splitlines() if "Total:" in line), None)

            if memory_line:
                memory_size_match = re.search(r"Total:\s+(\d+).*", memory_line)
                if memory_size_match:
                    memory_size = int(memory_size_match.group(1))
        except Exception as err:
            raise (err)

        return memory_size

    def getAvailableMem(self):

        memory_size=0

        try:
            mem_output = subprocess.run(["free", "-t", "-m"], capture_output=True, text=True, check=True).stdout

            memory_line = next((line for line in mem_output.splitlines() if "Mem:" in line), None)

            if memory_line:
                memory_size_match = re.search(r"Mem:\s+\d+\s+\d+\s+(\d+).*", memory_line)
                if memory_size_match:
                    memory_size = int(memory_size_match.group(1))
        except Exception as err:
            raise(err)

        return memory_size


if __name__=="__main__":
    memStat = GetLinuxMemStatus()

    totalMem = memStat.getTotalMemSize()

    availableMem = memStat.getAvailableMem()

    print("Total Mem: " + str(totalMem))
    print("Available Mem: " + str(availableMem))


