# Testing Matrix for the Ramdisk project

This document only pertains to the python project.  As the other language project mature, each will either be added to this document, or split out into language specific sets of tables.

## Testing Methods

Some of the testing is provided by a Jenkins pipeline, but most of the testing is currently done by hand.

### Runs on

 []() | Linux | macOS | Windows
 ---|------------|-------------|---------------
 C++ | yes | yes | in progress
 python | yes | yes | yes
 Golang | in progress | in progress | in progress
 Rust | in progress | in progress | in progress

### Hardware

Developed on Apple Silicon and VM's on Apple Silicon, except for the 
python code, which has also been tested on 64 bit Intel.

### OS's Tested

Time has allowed for the following

[]() | C++ | Golang | Python | Rust
 ---|------------|-------------|---------------|---------------
macOS | in progress | in progress | Yes | in progress
Windows | in progress | in progress | Yes | in progress
Debian | in progress | in progress | Yes | in progress
Ubuntu | not currently | not currently | Yes | not currently
Rocky Linux | in progress | in progress | Yes | in progress
Alma Linux | not currently | not currently | Yes | not currently

Python has automated CI/CD with the above OS's in Jenkins.  All other languages are manually tested on the above OSs.
