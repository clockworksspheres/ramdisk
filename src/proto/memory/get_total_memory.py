import subprocess
import re

def get_memory_size():
    """Retrieves the total physical memory size in GB on macOS."""
    try:
        process = subprocess.run(['system_profiler', 'SPHardwareDataType'], capture_output=True, text=True, check=True)
        output = process.stdout
        memory_line = next((line for line in output.splitlines() if "Memory:" in line), None)
        if memory_line:
            memory_size_match = re.search(r"Memory:\s+(\d+)\s+GB", memory_line)
            if memory_size_match:
                return int(memory_size_match.group(1))
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
    except StopIteration:
         print("Memory information not found in system_profiler output.")   
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

if __name__ == "__main__":
    memory_size = get_memory_size()
    if memory_size:
        print(f"Total memory: {memory_size} GB")
    else:
        print("Could not retrieve memory size.")

