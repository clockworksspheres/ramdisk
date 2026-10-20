

def getMaxMemSize():
    """
    get the max mem size for the slider to go to...
    
    be careful to only go to usable memory - not to 
    total physical memory.

    physical memory - memory being used, somehow - 
    different ways for different OS's.
    
    actually each ramdisk has it's own way to do this 
    - probably should be pulled out to do it here, or 
    mirrored here.  something like:   
    if sys.platform.startswith(????): 
    - - do this elif --- do that -- elif ------ do the 
    other -- etc.... pulling the appropriate part out 
    of each ramdisk.
    """
    return 100

