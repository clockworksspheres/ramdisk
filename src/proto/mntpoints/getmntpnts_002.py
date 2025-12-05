# doesn't take into account what volumes are
# ramdisks and not ramdisks.
#

import re
import subprocess

result = subprocess.run(['mountvol'], capture_output=True, text=True)
for line in result.stdout.splitlines():
    line = line.strip()
    pattern = r"([C-Z]:)\\(?:[^\\]*\\.*)\\?$"
    try:
        match = re.match(pattern, line)
        #if match:
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

