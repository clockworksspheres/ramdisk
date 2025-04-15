import ctypes

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

def get_available_memory():
    memory_status = MEMORYSTATUSEX()
    memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))
    return memory_status.ullAvailPhys

print(f"Available Physical Memory: {get_available_memory()} bytes")

"""
import subprocess
import re

def get_available_win32_memory():
    """Retrieves available memory size in MB on win32."""
    pass

def getMaxWin32MemSize():
    pass
"""
#available_memory = get_available_memory()
"""
#if available_memory is not None:
    print(f"Available memory: {available_memory:.2f} MB")
else:
    print("Could not retrieve available memory.")
"""

