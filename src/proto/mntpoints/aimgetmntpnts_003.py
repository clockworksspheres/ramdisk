import subprocess
import re

def get_mntpnts():

    mnts = {}
    result = subprocess.run(['aim_ll', '-l'], capture_output=True, text=True)
    for line in result.stdout.splitlines():
        line = line.strip()
        if re.search("\\\\\\\\", line):
            continue
        elif re.search("000", line):
            # print(line)
            # anchor = True
            device = line.split()[-1]
        elif re.search(r':\\.*', line):
            # print(line)
            mountname = line.split("Mounted at ")[1]
            #mountname = line.split()[-1]
        elif not line:
            #anchor = False
            print(f"{mountname} : {device}")
            mnts[mountname] = device
            continue
    return mnts

if __name__ == "__main__":
    mnts = get_mntpnts()
    print(".....")
    for key, value in mnts.items():
        print(f"{key} : {value}")
    print(".....")
    print(".....")
    print(".....")
