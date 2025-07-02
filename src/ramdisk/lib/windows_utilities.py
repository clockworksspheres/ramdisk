
#####
# come from the external library pywin32
# needed for function is_windows_process_elevated()
import win32security
import win32process
import win32api
#####

def is_windows_process_elevated():
    try:
        # Open the process token
        hProcess = win32process.GetCurrentProcess()
        hToken = win32security.OpenProcessToken(hProcess, win32security.TOKEN_QUERY)

        try:
            # Get the administrators group SID
            sid = win32security.LookupAccountName(None, "Administrators")[0]

            # Check if the token is a member of the administrators group
            is_admin = win32security.CheckTokenMembership(hToken, sid)

            return is_admin
        except Exception as e:
            print(f"Error checking token membership: {e}")
            return False
        finally:
            # Close the token handle
            win32api.CloseHandle(hToken)
    except Exception as e:
        print(f"Error opening process token: {e}")
        return False

