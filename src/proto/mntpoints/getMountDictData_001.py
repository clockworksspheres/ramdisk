# doesn't take into account what volumes are
# ramdisks and not ramdisks.
#

import re
import subprocess

def getMountDisks():
    """
    should return the a dictionary with {device: diskName, ...} that contains
    every mounted disk
    """
    print("Got in")
    mnts = {}
    result = subprocess.run(r'aim_ll -l', capture_output=True, text=True)
    print(str(result.stdout))
    #result = re.sub(r"\\n", r"\n", result)
    for line in result.stdout.splitlines():
        line = line.strip()
        if re.search(r"\\\\\\\\", line):
            continue
        elif re.match("Device number \d+", line):
            print("Looking for device: " + line)
            # anchor = True
            device = line.split()[-1]
            print("Found Device: " + device)
        elif re.search(r':\\.*', line):
            # print(line)
            mountname = line.split("Mounted at ")[1]
            #mountname = line.split()[-1]
        elif not line:
            #anchor = False
            try:
                print(f"{mountname} : {device}")
                mnts[device] = mountname
            except UnboundLocalError:
                continue
            continue
    return mnts

if __name__=="__main__":
	print("Starting in __main__")
	disks = getMountDisks()
	print(str(disks))
	for key, value in disks.items():
		print(f"Device: {key}, Value: {value}")
		
