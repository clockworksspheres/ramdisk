"""
Class for ramdisk management specific creations

Should be OS agnostic


"""



class MemoryNotAvailableError(Exception):
    """
    Meant for being thrown when an action/class being run/instanciated is not
    applicable for the running operating system.

    
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class UnsupportedOSError(Exception):
    """
    Meant for being thrown when an action/class being run/instanciated is not
    applicable for the running operating system.

    
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class NotValidForThisOS(Exception):
    """
    Meant for being thrown when an action/class being run/instanciated is not
    applicable for the running operating system.

    
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class SystemToolNotAvailable(Exception):
    """
    Meant for being thrown when a system command is not available for
    use by the library.

    
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class NotEnoughMemoryError(Exception):
    """
    Thrown when there is not enough memory for this operation.

    
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class NotACyLoggerError(Exception):
    """
    Custom Exception
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class UserMustBeRootError(Exception):
    """
    Custom Exception
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
