

import subprocess
from subprocess import PIPE
import getpass

passwd = getpass.getpass('Password: ')
print('Password entered:', passwd)


# Start the echo command
echo_cmd = subprocess.Popen(["echo", "'" + passwd + "'"], stdout=subprocess.PIPE, text=True)

# Start the sha256sum command and pipe the output of echo_cmd to it
sha256sum_cmd = subprocess.Popen(["sudo", "-S", "sha256sum"], stdin=echo_cmd.stdout, stdout=subprocess.PIPE, stderr=PIPE, text=True)

# Close the stdout of echo_cmd to send EOF to sha256sum
echo_cmd.stdout.close()

# Get the output of the sha256sum command
stdout, stderr = sha256sum_cmd.communicate()

# Print the output
print(str(stdout).strip())

print(str(stderr).strip())


