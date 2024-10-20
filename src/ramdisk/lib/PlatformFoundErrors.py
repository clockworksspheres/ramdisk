'''
Exceptions related to finding specific platforms, specifically to ease the 
creation and management of mocking libraries that may not be available on
a specific platform.  Design specifically started to mock libc and libc 
functions  on the Windows platform, although I can see mocking via this 
kind of exception architecture could be useful for more than just the 
windows platform.

Providing an example exeption for the macOS platform.

Child exceptions could be created for speceific versions of OS's that 
inherit these exceptions.

'''

###
# Windows platform exception

class Win32PlatformFoundError(BaseException):
    """
    Custom Exception
    """
    def __init__(self, *args, **kwargs):
        BaseException.__init__(self, *args, **kwargs)


###
# macOS platform exception

class DarwinPlatformFoundError(BaseException):
    """
    Custom Exception
    """
    def __init__(self, *args, **kwargs):
        BaseException.__init__(self, *args, **kwargs)



