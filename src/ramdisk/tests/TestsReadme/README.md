
Test Bug #1

the genericRamdiskTest.py should change to test_Ramdisk.py and just test the
ramdisk factory...

Each OS version should test that OS's ramdisk specifically, excluding all other
OS's ramdisks...

Those two are not exclusive as of 2/5/25...

test bug #2

all the files in the test directory should be test_*.py - all other files should
be in the "helper/helpers" or "lib" directory, or rely on files in the ../ramdisk
directory.  This allows for better compatibility with pytest.

Test bug #3

Tests should be written for the fsHelpers.

Feature #1

CI/CD

currently running Jenkins, and testing per OS family at a time.
 Wrote the vmm rep and jenkinsTools repo to assist in automation
of CI/CT.  Currently building app/executables with PyInstaller.
Still need to create installer builds for project across operating
systems, to get the CD part going.  Jenkins server currently running
in a container.

