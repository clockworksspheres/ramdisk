#!/usr/bin/python3

import argparse
import subprocess
import sys

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Search for a process by name using ps and grep.")
    parser.add_argument('process_name', help="Name of the process to search for")

    # Parse arguments
    args = parser.parse_args()

    # Step 1: Run 'ps -eaf' and capture output
    ps_process = subprocess.Popen(['ps', '-eaf'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Step 2: Pipe ps output to 'grep' (excluding the grep command itself)
    grep_process = subprocess.Popen(
        ['grep', '-w', args.process_name],
        stdin=ps_process.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Close ps stdout in the parent process
    ps_process.stdout.close()

    # Get output from grep
    output, errors = grep_process.communicate()

    # Check for errors
    if grep_process.returncode == 1:
        print(f"No process found matching '{args.process_name}'.")
        sys.exit(0)
    elif grep_process.returncode > 1:
        print(f"Error in grep: {errors.decode('utf-8')}")
        sys.exit(1)

    # Decode and print matching processes (exclude the grep command line if shown)
    lines = output.decode('utf-8').strip().split('\n')
    for line in lines:
        if 'grep' not in line:
            print(line)

if __name__ == '__main__':
    main()   

