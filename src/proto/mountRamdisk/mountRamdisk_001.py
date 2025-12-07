import subprocess
import sys

sys.path.append("../..")

from ramdisk.lib.fsHelper.winDriveTools import cleanDrivePath

params = "/fs:ntfs /v:TestRam /q /y"
size = "500M"
mntpnt = "F:"

#####
# Works
mntpnt = "r:\\\\\\"
path = cleanDrivePath(mntpnt)
result = subprocess.check_output(f"aim_ll -a -s {size} -m \"{path}\" -p \"{params}\"")

#####
# Works
# result = subprocess.check_output(f"aim_ll -a -s {size} -m \"{mntpnt}\" -p \"{params}\"")

# Works
#mntpnt = "C:\\Users\\royni\\tmp tmp"
#result = subprocess.check_output(f"aim_ll -a -s {size} -m \"{mntpnt}\" -p \"{params}\"")

# Did NOT work
#mntpnt = "C:/Users/royni/tmp tmp"
#mntpnt = "C:\Users\royni\tmp tmp"
#result = subprocess.check_output(f"aim_ll -a -s {size} -m \"{mntpnt}\" -p \"{params}\"")

print(result)
