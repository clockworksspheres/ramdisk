
import subprocess

output = subprocess.check_output("mountvol")

for line in output:

    print(line)

