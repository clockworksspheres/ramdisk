
Test Bug #1

the genericRamdiskTest.py should change to test_Ramdisk.py and just test the
ramdisk factory...

Test Bug #2

Each OS version should test that OS's ramdisk specifically, excluding all other
OS's ramdisks...

#1 and #2 are not exclusive as of 2/5/25...

Feature #1

CI/CD

Currently running Jenkins, and testing per OS family at a time.

Wrote the [vmm](https://github.com/clockworksspheres/vmm.git)
tool and [jenkinsTools](https://github.com/clockworksspheres/jenkinsTools.git)
tools to assist in automation of CI/CT. Currently building
app/executables with PyInstaller.

Still need to create installer builds for project across operating
systems, to get the CD part going.  Jenkins server currently running
in a container.

