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
    """ get win32 memory in terms of megabytes """
    memory_status = MEMORYSTATUSEX()
    memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))
    mbmem = int(memory_status.ullAvailPhys/(1024*1024))
    return mbmem

def get_total_memory():
    """ get win32 memory in terms of megabytes """
    memory_status = MEMORYSTATUSEX()
    memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))
    mbmem = int(memory_status.ullTotalPhys/(1024*1024))
    return mbmem


if __name__ == "__main__":

    available_mem = get_available_memory()

    print(f"Available Physical Memory: {available_mem} megabytes")

    total_mem = get_total_memory()

    print(f"Total Physical Memory: {total_mem} megabytes")
