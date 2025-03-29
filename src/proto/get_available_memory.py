import subprocess
import re

def get_available_memory():
    """Retrieves available memory size in MB on macOS."""
    vm_output = subprocess.run(['vm_stat'], capture_output=True, text=True, check=True).stdout
    
    pages_free_line = next((line for line in vm_output.splitlines() if "Pages free" in line), None)
    if pages_free_line:
        pages_free = int(re.search(r'(\d+)', pages_free_line).group(1))
        page_size = 4096  # macOS page size is 4096 bytes
        available_memory_bytes = pages_free * page_size
        available_memory_mb = available_memory_bytes / (1024 * 1024)
        return available_memory_mb
    else:
        return None

available_memory = get_available_memory()

if available_memory is not None:
    print(f"Available memory: {available_memory:.2f} MB")
else:
    print("Could not retrieve available memory.")


