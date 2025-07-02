

import sys

sys.path.append("../../..")

from ramdisk.lib.fsHelper.FsHelperTemplate import FsHelperTemplate

class FsHelper(FsHelperTemplate):
    """
    Class applicable in python 3.0 and higher
    Will inherit the above class as is and be able to 
        use parent methods as is.
    """
    def __init__(self):
        pass

