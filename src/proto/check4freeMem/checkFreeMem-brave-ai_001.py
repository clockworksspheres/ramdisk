import psutil

# Get virtual memory details
memory_info = psutil.virtual_memory()

# Extract the free memory value
free_memory = memory_info.free

# Print the free memory in gigabytes
print(f"Free Memory: {free_memory / (1024 ** 3):.2f} GB")   


