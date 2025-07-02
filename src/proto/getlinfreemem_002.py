import subprocess
import re

memory_size=0

try:
    mem_output = subprocess.run(["free", "-t", "-m"], capture_output=True, text=True, check=True).stdout

    print(str(mem_output))

    memory_line = next((line for line in mem_output.splitlines() if "Mem:" in line), None)

    print(str(memory_line))

    if memory_line:
        memory_size_match = re.search(r"Mem:\s+\d+\s+\d+\s+(\d+).*", memory_line)
        if memory_size_match:
            memory_size = int(memory_size_match.group(1))
except:
    print("Damnit Jim!!!")

print("Mem Size: " + str(memory_size))

"""
# Getting all memory using os.popen()
total_memory, used_memory, free_memory = map(
    int, os.popen('free -t -m').readlines()[-1].split()[1:])
print(f"Free Memory: {free_memory} MB")
"""

