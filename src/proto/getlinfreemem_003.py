import subprocess
import re


def getAvailableMem():

    memory_size=0

    try:
        mem_output = subprocess.run(["free", "-t", "-m"], capture_output=True, text=True, check=True).stdout

        memory_line = next((line for line in mem_output.splitlines() if "Mem:" in line), None)

        if memory_line:
            memory_size_match = re.search(r"Mem:\s+\d+\s+\d+\s+(\d+).*", memory_line)
            if memory_size_match:
                memory_size = int(memory_size_match.group(1))
    except Exception as err:
        raise(err)

    return memory_size


if __name__=="__main__":

    availableMem = getAvailableMem()
    print("Free Memory: " + str(availableMem))


