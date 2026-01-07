'''
'''
# --- Native python libraries
import os
import sys

sys.path.append("../..")

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

    
    """

    if sys.platform.startswith("win32"):
        from ramdisk.lib.getLibc.linuxGetLibc import getLibc
        return getLibc()
    elif sys.platform.startswith("linux"):
        from ramdisk.lib.getLibc.linuxGetLibc import getLibc
        return getLibc()
    elif sys.platform.startswith("darwin"):
        from ramdisk.lib.getLibc.macGetLibc import getLibc
        return getLibc()
    else:
        raise LibcNotAvailableError("Libc is Not Avaiable via this Software for this OS")

##############################################################################
