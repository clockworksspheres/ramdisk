'''
'''


# --- Native python libraries
import os
import sys

# --- non-native python libraries in this source tree

class LibcNotAvailableError(BaseException):
    """
    Custom Exception
    """
    def __init__(self, *args, **kwargs):
        BaseException.__init__(self, *args, **kwargs)


##############################################################################

def getLibc( ):
    """
    Acquire a reference to the system libc, initially to access the
    filesystem "sync" function.

    @returns: python reference to the C libc object, or False, if it can't
              find libc on the system.

    @author: Roy Nielsen
    """
    libc = True

    import ctypes


    #####
    # For Linux
    possible_paths = ["/usr/lib/x86_64-linux-gnu/libc.so.6",
                      "/lib/x86_64-linux-gnu/libc.so.6",
                      "/lib/i386-linux-gnu/libc.so.6",
                      "/usr/lib64/libc.so.6",
                      "/usr/lib/libc.so.6",
                      "/lib64/libc.so.6",
                      "/lib/libc.so.6"]
    for path in possible_paths:
        if os.path.exists(path):
            libc = ctypes.CDLL(path)
            break

    try:
        if libc:
            libc.sync()
    except AttributeError:
        raise LibcNotAvailableError("............................Cannot Sync.")

    return libc

##############################################################################
