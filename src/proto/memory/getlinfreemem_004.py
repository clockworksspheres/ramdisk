import psutil

# Get system memory info
mem = psutil.virtual_memory()

# Free memory (strictly unused)
print(f"Free Memory: {mem.free / (1024**2):.2f} MB")

# Available memory (usable by applications)
print(f"Available Memory: {mem.available / (1024**2):.2f} MB")   

