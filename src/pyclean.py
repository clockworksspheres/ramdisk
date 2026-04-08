#!/usr/bin/env python3

import pathlib

# clean files
for p in pathlib.Path('.').rglob('*.pyc'):  # Replace '*.pyc' with your file pattern
    if p.is_file():  # Ensure it's a file, not a directory
        print(f"Deleting: {p}")
        p.unlink()

# clean directories
for p in pathlib.Path('.').rglob('__pycache__'):
    print(f"Deleting: {p}")
    p.rmdir()
