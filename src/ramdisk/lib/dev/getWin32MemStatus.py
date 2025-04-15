#!/usr/bin/env -S python -u
"""
"""
import sys
import ctypes

sys.path.append("../../..")

#--- non-native python libraries in this source tree
from ramdisk.lib.dev.getMemStatusTemplate import GetMemStatusTemplate


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


class GetWin32MemStatus(GetMemStatusTemplate):
    def __init__(self):
        # super if necessary
        print("macos initialization complete...")

    def getTotalMemSize(self):
        """Retrieves the total physical memory size in MB on Win32."""
        memory_status = MEMORYSTATUSEX()
        memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))
        mbmem = int(memory_status.ullTotalPhys/(1024*1024))
        return mbmem


    def getAvailableMem(self):
        """Retrieves available memory size in MB on Win32."""
        memory_status = MEMORYSTATUSEX()
        memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))
        mbmem = int(memory_status.ullAvailPhys / (1024 * 1024))
        return mbmem


if __name__=="__main__":
    memStat = GetMacosMemStatus()

    totalMem = memStat.getTotalMemSize()

    availableMem = memStat.getAvailableMem()

    print("Total Mem: " + str(totalMem))
    print("Available Mem: " + str(availableMem))


