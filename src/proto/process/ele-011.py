import subprocess
import select
import os

# Start a subprocess
proc = subprocess.Popen(["command", "arg1", "arg2"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Function to send input and read output
def interact_with_subprocess(proc, input_data):
    outputs = []
    while True:
        # Check if the process has finished
        if proc.poll() is not None:
            break

        # Check if there is data to read from stdout and stderr
        readable, _, _ = select.select([proc.stdout, proc.stderr], [], [], 0)
        for stream in readable:
            if stream is proc.stdout:
                output = os.read(stream.fileno(), 1024).decode()
                outputs.append(output)
                print(f"Output: {output}")
            elif stream is proc.stderr:
                error = os.read(stream.fileno(), 1024).decode()
                print(f"Error: {error}")

        # Check if there is input to send
        if input_data:
            proc.stdin.write(input_data.encode() + b'\n')
            proc.stdin.flush()
            input_data = None

    # Close the input stream
    proc.stdin.close()

    # Wait for the process to complete
    exit_code = proc.wait()
    return outputs, exit_code

# Example usage
input_data = "first input"
outputs, exit_code = interact_with_subprocess(proc, input_data)

print(f"Final outputs: {outputs}")
print(f"Exit code: {exit_code}")



