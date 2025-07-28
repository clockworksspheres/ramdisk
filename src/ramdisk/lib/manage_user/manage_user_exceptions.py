"""
Exeptions for managing users.

"""
class UserExistsError(Exception):
    """ 
    Meant for being thrown when a user already exists in the system

    
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class UserCreationUnsuccessfullError(Exception):
    """ 
    Meant for being thrown when a user can't be created
    for some reason... Will likely need to check the
    system logs for the reason why....

    
    """
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)



