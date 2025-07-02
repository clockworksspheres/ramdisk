import ctypes
from ctypes import wintypes
import traceback

# Define necessary constants
TOKEN_QUERY = 0x0008
TOKEN_READ = 0x00020008
TOKEN_IMPERSONATE = 0x0004
TOKEN_ADJUST_PRIVILEGES = 0x0020
TOKEN_ADJUST_GROUPS = 0x0040
TOKEN_ADJUST_DEFAULT = 0x0080
TOKEN_ADJUST_SESSIONID = 0x0100

SE_DEBUG_NAME = "SeDebugPrivilege"
SE_PRIVILEGE_ENABLED = 0x00000002

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
advapi32 = ctypes.WinDLL('advapi32', use_last_error=True)

if not advapi32:
    raise BaseException("No DLL by that name...")

# Define necessary structures
class LUID(ctypes.Structure):
    _fields_ = [
        ('LowPart', wintypes.DWORD),
        ('HighPart', wintypes.LONG)
    ]

class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ('Luid', LUID),
        ('Attributes', wintypes.DWORD)
    ]

class TOKEN_PRIVILEGES(ctypes.Structure):
    _fields_ = [
        ('PrivilegeCount', wintypes.DWORD),
        ('Privileges', LUID_AND_ATTRIBUTES * 1)
    ]

# Define necessary functions
def open_current_process_token():
    hProcess = kernel32.GetCurrentProcess()
    hToken = wintypes.HANDLE()
    if not advapi32.OpenProcessToken(hProcess, TOKEN_QUERY, ctypes.byref(hToken)):
        raise ctypes.WinError(ctypes.get_last_error())
    return hToken

def lookup_privilege_value(lpSystemName, lpName):
    luid = LUID()
    if not advapi32.LookupPrivilegeValueW(lpSystemName, lpName, ctypes.byref(luid)):
        raise ctypes.WinError(ctypes.get_last_error())
    return luid

def check_token_membership(hToken, pSid):
    is_member = wintypes.BOOL()
    if not advapi32.CheckTokenMembership(hToken, pSid, ctypes.byref(is_member)):
        raise ctypes.WinError(ctypes.get_last_error())
    return bool(is_member)

def check_if_admin():
    hToken = open_current_process_token()
    sid = ctypes.c_void_p()
    if not advapi32.OpenProcessToken(kernel32.GetCurrentProcess(), TOKEN_QUERY, ctypes.byref(hToken)):
        pass
        #raise ctypes.WinError(ctypes.get_last_error())

    if not advapi32.GetTokenInformation(hToken, 1, None, 0, ctypes.byref(wintypes.DWORD())):
        error = ctypes.get_last_error()
        if error != 122:  # ERROR_INSUFFICIENT_BUFFER
            raise ctypes.WinError(error)

    dwSize = wintypes.DWORD()
    advapi32.GetTokenInformation(hToken, 1, None, 0, ctypes.byref(dwSize))
    buffer = ctypes.create_string_buffer(dwSize.value)
    if not advapi32.GetTokenInformation(hToken, 1, buffer, dwSize, ctypes.byref(dwSize)):
        raise ctypes.WinError(ctypes.get_last_error())

    sid = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_void_p)).contents
    return check_token_membership(hToken, sid)

# Check if the current process is running with elevated privileges
try:
    if check_if_admin():
        print("The process is running with elevated privileges.")
    else:
        print("The process is not running with elevated privileges.")
except ctypes.WinError as error:
    print(traceback.format_exc())
