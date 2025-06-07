#!/usr/bin/env -S python -u
"""
"""
import os
import sys

mytest = os.isatty(sys.stdin.fileno())
#mytest = os.isatty(sys.stdout.fileno)
#mytest = os.isatty()

if mytest:
    print("We're running in the terminal people...")
else:
    print("we're running in GUI mode...")


