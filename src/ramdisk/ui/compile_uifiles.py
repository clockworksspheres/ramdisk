

import os
import sys 

from ramdisk.lib.run_commands import RunWith

ui_files = [file for file in os.listdir() if file.endswith(".ui")]

print(ui_files)

#        self.rw.setCommand(['/bin/ls', '-l', '/usr/local'])
#        _, _, retval = self.rw.communicate(silent=False)

rw = RunWith()

for myfile in ui_files:
    uipyfile = "ui_" + ".".join(myfile.split(".")[:-1]) + ".py"
    print(str(uipyfile))
    rw.setCommand(["pyside6-uic", myfile, "-o", uipyfile])
    _, _, retval = rw.communicate(silent=False)
    print(str(retval))



