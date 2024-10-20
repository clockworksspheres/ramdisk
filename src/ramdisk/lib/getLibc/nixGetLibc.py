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
    # libc = True

    if sys.platform is "win32":
        return(0)
    else:
        import ctypes


    #####
    # For Mac
    try:
        libc = ctypes.CDLL("/usr/lib/libc.dylib")
        # libc = ctypes.CDLL("libc.dylib")
    except OSError:
        #####
        # For Linux
        possible_paths = ["/lib/x86_64-linux-gnu/libc.so.6",
                          "/lib/i386-linux-gnu/libc.so.6",
                          "/usr/lib64/libc.so.6",
                          "/usr/lib/libc.so.6",
                          "/lib64/libc.so.6",
                          "/lib/libc.so.6"]
        for path in possible_paths:

                break

    try:
        if libc:
            libc.sync()
    except AttributeError:
        raise LibcNotAvailableError("............................Cannot Sync.")

    return libc

##############################################################################
