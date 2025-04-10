
import subprocess
import getpass

passwd = getpass.getpass('Password: ')
# print('Password entered:', passwd)


# Define the password and the command
command = "ls"

# Create the subprocess
proc = subprocess.Popen(['sudo', '-S', command], stdin=subprocess.PIPE, stderr=subprocess.PIPE)

# Communicate the password to the subprocess
output, error = proc.communicate((passwd + '\n').encode())

# Print the output and error
print("Output:", output)
# print("Error:", error)


