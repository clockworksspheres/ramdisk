
import re
import sys

sys.path.append("../..")

from ramdisk.lib.run_commands import RunWith

rw = RunWith()

rw.setCommand(["/usr/bin/lsb_release", "-dr"])
output, _, _ = rw.communicate()

output = output.splitlines()
description = output[0]  
release = output[1]

print(description)
print(release)

