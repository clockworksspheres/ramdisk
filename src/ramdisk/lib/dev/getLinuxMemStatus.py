#!/usr/bin/env -S python -u
"""
"""
import subprocess
import re
import sys
import psutil
from pathlib import Path

# Get the parent directory of the current file's parent directory
#  and add it to sys.path
parent_dir = Path(__file__).parent.parent.parent
sys.path.append(str(parent_dir))

#--- non-native python libraries in this source tree
from lib.dev.getMemStatusTemplate import GetMemStatusTemplate

class GetMacosMemStatus(GetMemStatusTemplate):
    def __init__(self):
        # Get system memory info
        self.mem = psutil.virtual_memory()
        print("macos initialization complete...")

    def getTotalMemSize(self):
        """Retrieves the total physical memory size in GB on macOS."""
        print(f"Total: {self.mem.total / (1024**3):.2f} GB")

        return int(self.mem.total / (1024**2))

    def getAvailableMem(self):
        """Retrieves available memory size in MB on macOS."""
        # Free memory (strictly unused)
        print(f"Free Memory: {self.mem.free / (1024**2):.2f} MB")

        # Available memory (usable by applications)
        print(f"Available Memory: {self.mem.available / (1024**2):.2f} MB")

        return int(self.mem.free/(1024**2))


class OldGetLinuxMemStatus(GetMemStatusTemplate):
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


