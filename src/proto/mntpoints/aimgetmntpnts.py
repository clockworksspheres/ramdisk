import subprocess
import re

result = subprocess.run(['aim_ll', '-l'], capture_output=True, text=True)
for line in result.stdout.splitlines():
    line = line.strip()
    if re.search("\\\\\\\\", line):
        continue
    elif re.search("000", line):
        # print(line)
        amchor = True
        device = line.split()[-1]
    elif re.search(':\\\\.*', line):
        # print(line)
        mountname = line.split()[-1]
    elif not line:
        anchor = False
        print(f"{mountname} : {device}")
        continue

     
