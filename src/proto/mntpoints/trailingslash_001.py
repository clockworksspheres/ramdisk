import re

path = r"D:\Projects\Project_2025_Version3\\"

# Regex: capture everything up to but not including the final backslash
pattern = r"^(.*?)(\\*)?$"

match = re.match(pattern, path)
if match:
    directory = match.group(1)   # everything before the optional trailing slash
    print("Directory:", directory)

