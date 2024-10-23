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



class libc(object):
    """
    """
    def ___init___(self):
        super(libc, self).__init__()
        pass

    def sync(self):
        """
        """
        pass


def getLibc( ):
    """
    Acquire a reference to the system libc, initially to access the
    filesystem "sync" function.

    @returns: python reference to the C libc object, or False, if it can't
              find libc on the system.

    @author: Roy Nielsen
    """
    mylibc = libc()
    return mylibc

##############################################################################
