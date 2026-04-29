Feature #1

# Unit testing ramdisk

Tests written to exercise the support libraries - the main tools are 
primarily command line interfaces to the libraries in the ramdisk
directory.

## Pylint related

Files:

```
PylintIface.py
test_with_pylint.py
test_PylintIface.py
```

harness for running pylint on all the project python files
to expose pylint Error and Failure messages via a python
unittest.

# CI/CD

Currently running Jenkins, and testing per OS family at a time.

Wrote the [vmm](https://github.com/clockworksspheres/vmm.git)
tool and [jenkinsTools](https://github.com/clockworksspheres/jenkinsTools.git)
tools to assist in automation of CI/CT. Currently building
app/executables with PyInstaller.

Still need to create installer builds for project across operating
systems, to get the CD part going.  Jenkins server currently running
in a docker container.

# References:

