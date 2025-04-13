import win32security
import win32process
import win32api


def get_current_user_sid():
    # Get the current process token
    ph = win32security.OpenProcessToken(win32process.GetCurrentProcess(), win32security.TOKEN_QUERY)

    # Get the user SID from the token
    user_sid, _ = win32security.GetTokenInformation(ph, win32security.TokenUser)

    return user_sid


sid = get_current_user_sid()
print(f"User SID: {sid}")
