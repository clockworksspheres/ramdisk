import subprocess

# Launch the first command (ps) and capture its output
ps_process = subprocess.Popen(['Get-WmiObject', '-Class', 'Win32_LogicalDisk'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Launch the second command (grep) and pipe the output of ps into it
grep_process = subprocess.Popen(['Select-Object', 'DeviceID'], stdin=ps_process.stdout, stdout=subprocess.PIPE)

# Close the stdout of the first process to allow it to receive a SIGPIPE if the second process exits
ps_process.stdout.close()

# Read the final output from the second process
output, _ = grep_process.communicate()

# Decode and print the result
print(output.decode('utf-8').strip())

