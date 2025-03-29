

import sys
import os

sys.path.append("../")
from ramdisk.lib.fsHelper.macosFsHelper import FsHelper



if __name__=="__main__":
    # fsHelper = FsHelper()
    # success, mysize = fsHelper.getDiskSizeInMb()
    # success, mysize = fsHelper.getDiskSizeInMb()
    # success, blockSize = fsHelper.getFsBlockSize()
    # print(str(blockSize))
    # print(str(mysize))



    st = os.statvfs("/")
    total = (st.f_blocks * st.f_frsize)/(1024*1024*1024)
    used = ((st.f_blocks - st.f_bfree) * st.f_frsize)/(1024*1024*1024)
    free = (st.f_bavail * st.f_frsize)/(1024*1024*1024)

    print(f"Total: {total} bytes")
    print(f"Used: {used} bytes")
    print(f"Free: {free} bytes")



