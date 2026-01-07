import re
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

result = str(result)

# in result string, replast string \r\n to control characters \r\n
result = re.sub(r"\\r\\n", r"\r\n", result)

device = ""
for line in result.splitlines():
    print(str(line))
    if re.match("Created", line) and re.search("memory", line.strip().split()[-1]):
        device = line.split()[2]

print(device + "\n\n")


mntpnt = r"c:\\\\Users\\\\royni\\\\Mount"
path = cleanDrivePath(mntpnt)
result = subprocess.check_output(f"aim_ll -a -s {size} -m \"{path}\" -p \"{params}\"")

result = str(result)

# in result string, replast string \r\n to control characters \r\n
result = re.sub(r"\\r\\n", r"\r\n", result)

device = ""
for line in result.splitlines():
    print(str(line))
    if re.match("Created", line) and re.search("memory", line.strip().split()[-1]):
        device = line.split()[2]
