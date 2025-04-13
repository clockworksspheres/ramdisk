import win32security
import win32process
import win32api

def is_process_elevated():
    # Open the process token
    hProcess = win32process.GetCurrentProcess()
    print(str(hProcess))
    hToken = win32security.OpenProcessToken(hProcess, win32security.TOKEN_QUERY)
    print(str(hToken))
    # Get the administrators group SID
    sid = win32security.LookupAccountName(None, "Administrators")[0]
    print(str(sid))
    # Check if the token is a member of the administrators group
    is_admin = win32security.CheckTokenMembership(hToken, sid)
    print(str(is_admin))
    # Close the token handle
    win32api.CloseHandle(hToken)

    return is_admin

# Check if the current process is running with administrative privileges
if is_process_elevated():
    print("The process is running with administrative privileges.")
else:
    print("The process is not running with administrative privileges.")

