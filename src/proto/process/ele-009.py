
import subprocess
import getpass

passwd = getpass.getpass('Password: ')
# print('Password entered:', passwd)


# Define the password and the command
command = 'ps -ef'.split()

sudocmd = ["sudo", "-s"] + command

# Create the subprocess
proc = subprocess.Popen(sudocmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

# Communicate the password to the subprocess
output, error = proc.communicate((passwd + '\n').encode())

# Print the output and error
print("Output:", output)
# print("Error:", error)


