# functionality that collects a handle to libc

Contains a generic interface class that either calls OS specific libc setup functionality, or classes that 'mock' (see: [The Art of Mocking in Python: A Comprehensive Guide](https://medium.com/@moraneus/the-art-of-mocking-in-python-a-comprehensive-guide-8b619529458f) ) that functionality for OS's that don't support that library properly.

