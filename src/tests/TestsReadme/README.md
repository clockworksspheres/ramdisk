
Test Bug #1

the genericRamdiskTest.py should change to test_Ramdisk.py and just test the
ramdisk factory...

Each OS version should test that OS's ramdisk specifically, excluding all other
OS's ramdisks...

Those two are not exclusive as of 2/5/25...

Test Bug #2

tests should just take 512 as the size of Mb to make for the size of the ramdisk.
They should not have to calculate the the size via the number of sectors - they
should allow for the ramdisk code to figure all that out - that should be part
of the test - rely on the ramdisk code to get it right.

test bug #3

all the files in the test directory should be test_*.py - all other files should
be in the "helper/helpers" or "lib" directory, or rely on files in the ../ramdisk
directory.  This allows for better compatibility with pytest.

Test bug #4

Tests should be written for the fsHelpers.

Test bug #5

CI/CD

Someday, years down the road - Remote machine testing for automated testing.  VM's or machines should be set up for remote login to remote login to download and/or run the latest code and test Possibly cloud testing if one can get a cloud provider to donate VM's for automated testing, if I can't figure out local hardware.  Ansible, terraform should be involved.  Possibly containers with/for kubernetes, Go/Jenkins, graphana-loki-promtail, Redmine/Jira... as free as possible, as I have no money for anything....

