import subprocess
import select
import os
import getpass

passwd = getpass.getpass('Password: ')

# Create a subprocess
process = subprocess.Popen(["sudo", "-S", "ls", "-lah", "/tmp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Set file descriptors to non-blocking
os.set_blocking(process.stdin.fileno(), False)
os.set_blocking(process.stdout.fileno(), False)
os.set_blocking(process.stderr.fileno(), False)

# Data to send to stdin
input_data = (passwd + '\n').encode()

# Use select to monitor file descriptors and send data to stdin
while True:
    # Wait for data to be ready for reading and writing
    ready_to_read, ready_to_write, _ = select.select([process.stdout, process.stderr], [process.stdin], [])

    for stream in ready_to_read:
        if stream is process.stdout:
            output = stream.read()
            if output:
                print("Output:", output.decode())
            else:
                # No more data to read, break the loop
                break
        elif stream is process.stderr:
            error = stream.read()
            if error:
                print("Error:", error.decode())
            else:
                # No more data to read, break the loop
                break

    for stream in ready_to_write:
        if stream is process.stdin:
            if input_data:
                # Write data to stdin
                stream.write(input_data)
                stream.flush()
                input_data = None  # Clear input_data to avoid sending it again
            else:
                # Close stdin if no more data to send
                stream.close()

    # Check if the process has terminated
    if process.poll() is not None:
        break

# Clean up
process.stdin.close()
process.stdout.close()
process.stderr.close()
process.wait()


