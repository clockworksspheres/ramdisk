

import re

dev1 = "/dev/disk3"

tmpMatch = re.match(r"(\S+)(\d+)", dev1)

tmpDisk = tmpMatch.group(1)
tmpNum = tmpMatch.group(2)

tmpNum = int(tmpNum) + 1

print("dev: " + tmpDisk + str(tmpNum))

