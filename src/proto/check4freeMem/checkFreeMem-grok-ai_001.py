import psutil

# Get virtual memory stats
mem = psutil.virtual_memory()

# Free memory in bytes
free_memory = mem.free

# Convert to human-readable format (e.g., MB or GB)
free_memory_mb = free_memory / (1024 ** 2)  # Convert to MB
free_memory_gb = free_memory / (1024 ** 3)  # Convert to GB

print(f"Free memory: {free_memory_mb:.2f} MB")
print(f"Free memory: {free_memory_gb:.2f} GB")

