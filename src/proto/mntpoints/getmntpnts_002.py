#
# Using the system's mountvol command - 
# doesn't take into account what volumes are
# ramdisks and not ramdisks.
#

import re
import subprocess

result = subprocess.run(['mountvol'], capture_output=True, text=True)
for line in result.stdout.splitlines():
    if re.search(":\\\\", line):
        print(line)
    else:
        continue

