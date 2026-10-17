# Testing Matrix for the Ramdisk project

This document only pertains to the python project.  As the other language project mature, each will either be added to this document, or split out into language specific sets of tables.

## Testing Methods

Some of the testing is provided by a Jenkins pipeline, but most of the testing is currently done by hand.

### Hardware

Developed on Apple Silicon and VM's on Apple Silicon, except for the 
python code, which has also been tested on 64 bit Intel.

### OS's Tested

Time has allowed for the following

64 bit arm </p>Apple Silicon | C++ | Golang | Python | Rust
 ---|------------|-------------|---------------|---------------
macOS 27 | yes, cli and gui | yes, cli and gui | Yes, cli and gui | Yes, cli and gui
Windows 11 | - | - | yes, cli and gui | -
Debian 13 | yes, cli and gui | in progress | Yes, cli and gui | yes, cli and gui
Ubuntu 2404 | yes, cli and gui | yes, cli and gui | yes, cli and gui |  no.  Build tool conflict
Ubuntu 2604 | yes, cli and gui | yes, cli and gui | yes, cli and gui |  yes, cli and gui
Rocky Linux 9 | yes, cli and gui | yes, cli and gui | yes, cli and gui | yes, cli and gui
Rocky Linux 10 | yes, cli and gui | yes, cli and gui | yes, cli and gui | yes, cli and gui
Alma Linux 10 | yes, cli and gui | yes, cli and gui | yes, cli and gui | yes, cli and gui

Python has automated CI/CD with the above OS's in Jenkins.  All other languages are manually tested on the above OSs.
