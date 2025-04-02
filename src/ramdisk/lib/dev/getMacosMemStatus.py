#!/usr/bin/env -S python -u
"""
"""
import subprocess
import re
import sys

sys.path.append("../../..")

#--- non-native python libraries in this source tree
from ramdisk.lib.dev.getMemStatus import GetMemStatus


class GetMacosMemStatus(GetMemStatus):
    def __init__(self):
        # super if necessary
        pass


    def getTotalMemSize(self):
        """Retrieves the total physical memory size in GB on macOS."""
        try:
            process = subprocess.run(['system_profiler', 'SPHardwareDataType'], capture_output=True, text=True, check=True)
            output = process.stdout
            memory_line = next((line for line in output.splitlines() if "Memory:" in line), None)
            if memory_line:
                memory_size_match = re.search(r"Memory:\s+(\d+)\s+GB", memory_line)
                if memory_size_match:
                    return int(memory_size_match.group(1))
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
        except StopIteration:
             print("Memory information not found in system_profiler output.")   
        except Exception as e:
            print(f"An error occurred: {e}")
        return None

    def getAvailableMem(self):
        """Retrieves available memory size in MB on macOS."""
        vm_output = subprocess.run(['vm_stat'], capture_output=True, text=True, check=True).stdout
    
        pages_free_line = next((line for line in vm_output.splitlines() if "Pages free" in line), None)
        if pages_free_line:
            pages_free = int(re.search(r'(\d+)', pages_free_line).group(1))
            page_size = 4096  # macOS page size is 4096 bytes
            available_memory_bytes = pages_free * page_size
            float_available_memory_mb = available_memory_bytes / (1024 * 1024)
            available_memory_mb = int(float_available_memory_mb)
            return available_memory_mb
        else:   
            return None


if __name__=="__main__":
    memStat = GetMacosMemStatus()

    totalMem = memStat.getTotalMemSize()

    availableMem = memStat.getAvailableMem()

    print("Total Mem: " + str(totalMem))
    print("Available Mem: " + str(availableMem))


