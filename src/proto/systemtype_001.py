

import sys
import os
import re

sys.path.append("../")


from ramdisk.lib.run_commands import RunWith

rw = RunWith()


def systemtype():

    validtypes = ['launchd', 'systemd', 'init', 'upstart']
    cmdlocs = ["/usr/bin/ps", "/bin/ps"]
    cmdbase = ""
    cmd = ""
    vt = ""
    systemtype = ""

    # buld the command
    for cl in cmdlocs:
        if os.path.exists(cl):
            cmdbase = cl
    if cmdbase:
        cmd = cmdbase + " -p1"

    try:

        if cmd:
            # run the command
            rw.setCommand(cmd)
            output, _, _ = rw.communicate()
            #cmdoutput = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, close_fds=True, text=True)
            #outputlines = cmdoutput.stdout.readlines()
            outputlines = output
            for line in outputlines.splitlines():
                line = str(line)
                print("line: " + str(line))
                for vt in validtypes:
                    if re.search(vt, line, re.IGNORECASE):
                        systemtype = vt
                        print("systemtype: " + str(vt))

        else:
            print(str(__name__) + ":Unable to determine systemtype. Required utility 'ps' does not exist on this system")
    except OSError:
        print(str(__name__) + ":Unable to determine systemtype. Required utility 'ps' does not exist on this system")

    if systemtype not in validtypes:
        print(str(__name__) + ":This system is based on an unknown architecture")
    print(str(__name__) + ":Determined that this system is based on " + str(systemtype) + " architecture")

    return systemtype


if __name__=="__main__":
    systype = systemtype()
    print("system type: " + systype)


