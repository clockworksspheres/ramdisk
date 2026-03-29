import psutil

# get virtual memory details
memory_info = psutil.virtual_memory()

# Extract available memory in bytes
available_bytes = memory_info.available

# Convert to Gb
available_gb = available_bytes /(1024 ** 3)

print(f"Available Memory: {available_gb:.2f} GB")


