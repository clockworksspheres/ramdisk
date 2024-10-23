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

    import ctypes

    libc = ctypes.CDLL("/usr/lib/libc.dylib")
    # libc = ctypes.CDLL("libc.dylib")

    try:
        if libc:
            libc.sync()
    except AttributeError:
        raise LibcNotAvailableError("............................Cannot Sync.")

    return libc

##############################################################################
