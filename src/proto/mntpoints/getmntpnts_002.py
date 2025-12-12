# doesn't take into account what volumes are
# ramdisks and not ramdisks.
#

import re
import subprocess

mounts = {}
mount  = ""
device = ""

result = subprocess.run(['mountvol'], capture_output=True, text=True)
for line in result.stdout.splitlines():
    line = line.strip()
    pattern = r"([C-Z]:)\\(?:[^\\]*\\.*)\\?$"
    try:
        match = re.match(pattern, line)
        #if match:
        mount = match.group(1)
        print(f"WOW: {match.group(1)} {match.group(2)}")
    except AttributeError as err:
        pass
    except NameError as err:
        pass
    except IndexError as err:
        pass
    # line = line.strip("\\\\")
    if re.search(":\\\\", line):
        print(line)
    if re.search(":\\\\$", line):
        try:
            m = re.search("([C-Z]:)\\\\$", line)
            print(m.group(1))
        except:
            pass

    try:
        pattern = "Device number (\d+)"
        match = re.match(pattern, line)
        device = match.group(1)
        print("Device NUMBER: " + device)
    except AttributeError as err:
        pass
    except NameError as err:
        pass
    except IndexError as err:
        pass
        
    if re.search("^\s+$", line):
        mounts[device] = mount
        device = ""
        mount  = ""
        continue

for key, value in mounts:
    print(f"Device: {key}, Mountpoint: {value}")


