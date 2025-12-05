import os

path = r"D:\Projects\Project_2025_Version3\\"

drive, tail = os.path.splitdrive(path)

print("Drive:", drive)
print("Rest of path:", tail)
