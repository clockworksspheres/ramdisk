import subprocess
import re

result = subprocess.run(['aim_ll', '-l'], capture_output=True, text=True)
for line in result.stdout.splitlines():
    if re.search("\\\\\\\\", line):
        continue
    elif re.search("000", line):
        print(line)
    elif re.search(':\\\\.*', line):
        print(line)
