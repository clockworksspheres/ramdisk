import re
import subprocess
from subprocess import PIPE
import getpass



def run_cmd_w_sudo(passwd):
    # Define the password and the command
    command = 'ps -ef'.split()

    sudocmd = ["sudo", "-s"] + command

    # Create the subprocess
    proc = subprocess.Popen(sudocmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Send the first input
    proc.stdin.write(passwd)
    #proc.stdin.flush()


    # Read the first output
    output = proc.stdout.readline()
    print(f"First output: {output.decode()}")

    # Send the second input
    proc.stdin.write(b'second input\n')
    proc.stdin.flush()

    # Read the second output
    output = proc.stdout.readline()
    print(f"Second output: {output.decode()}")

    proc.stdin.close()

    exit_code = proc.wait()
    print(f"Process exited with code: {exit_code}")
    # Communicate the password to the subprocess
    # output, error = proc.communicate(passwd)


if __name__ == "__main__":
    
    passwd = getpass.getpass('Password: ')
    # print('Password entered:', passwd)a
    passwd = (passwd + "\n").encode()
    run_cmd_w_sudo(passwd)




