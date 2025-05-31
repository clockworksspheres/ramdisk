import subprocess
import select
import sys
import os
import time
import getpass

passwd = getpass.getpass('Password: ')

passwd = (passwd + "\n").encode()

cmd = "ls -lah /tmp/".split()

sudocmd = ["sudo", "-S"] + cmd

# Create a subprocess
process = subprocess.Popen(sudocmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Set file descriptors to non-blocking
os.set_blocking(process.stdin.fileno(), False)
os.set_blocking(process.stdout.fileno(), False)
os.set_blocking(process.stderr.fileno(), False)

# Data to send to stdin
input_data = passwd
stdin_closed = False
stdout_closed = False
stderr_closed = False

# Use select to monitor file descriptors and send data to stdin
while True:
    # Wait for data to be ready for reading and writing
    read_ready, write_ready, _ = select.select(
        [process.stdout] if not stdout_closed else [],
        [process.stdin] if not stdin_closed else [],
        []
    )

    for stream in read_ready:
        if stream is process.stdout:
            output = stream.read()
            if output:
                print("Output:", output.decode())
            else:
                # No more data to read, mark stdout as closed
                stdout_closed = True
        elif stream is process.stderr:
            error = stream.read()
            if error:
                print("Error:", error.decode())
            else:
                # No more data to read, mark stderr as closed
                stderr_closed = True

    for stream in write_ready:
        if stream is process.stdin:
            if input_data:
                # Write data to stdin
                stream.write(input_data)
                stream.flush()
                input_data = None  # Clear input_data to avoid sending it again
            else:
                # Close stdin if no more data to send
                stream.close()
                stdin_closed = True

    # Check if the process has terminated
    if process.poll() is not None:
        break

    # Check if all file descriptors are closed
    #    Looks like stderr behaves badly in this instance,
    #    and it is likely ok to close the process if stderr 
    #    is hanging like a loose hangnail...  If not, there
    #    may be bigger problems that need to be solved in 
    #    process.  It is likely that you still want to catch
    #    and report stderr however.
    if stdin_closed and stdout_closed: # and stderr_closed:
        break

# Clean up
if not stdin_closed:
    process.stdin.close()
if not stdout_closed:
    process.stdout.close()
if not stderr_closed:
    process.stderr.close()
process.wait()

print("Done, continuing to proces...")
time.sleep(5)

sys.exit()

