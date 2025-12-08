import psutil

# Get virtual memory stats
mem = psutil.virtual_memory()

print("Total memory:", mem.total / (1024**3), "GB")
print("Available memory:", mem.available / (1024**3), "GB")
print("Used memory:", mem.used / (1024**3), "GB")
print("Free memory:", mem.free / (1024**3), "GB")

print("\n-----------\n")
print("Total memory:", mem.total / (1024**2), "MB")
print("Available memory:", mem.available / (1024**2), "MB")
print("Used memory:", mem.used / (1024**2), "MB")
print("Free memory:", mem.free / (1024**2), "MB")


