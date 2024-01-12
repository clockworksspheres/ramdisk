# ramdisk

Interface to use, eventually for cross-platform setup and maintenance of ramdisk, primarily for unittesting and compiling code.

Initial work done and now tested only on the Mac platform, but developed for both Linux kernels and macOS.

## NOTE:
The code has two branches, master (hopefully stable) and develop (not necessarily stable).  The goal is to only merge to develop when functionality is stable and tests have been written for that functionality.

Initially developed for python 2.6, but code has since been migrated to 3.7+.  Not believed to work on the python 2 branch any longer.

### Mac Note

Instanciating the RamDisk class will create a ramdisk that you can use - in chunks of 1Mb.

Initial work done only for the Mac platform.

### Linux Note

Ramdisk class that can use either current method for creating a ramdisk on Linux, currently working on a tmpfs version....


## Used As a library

### macRamdisk

## Only developed for Linux

## As a library

### linuxLoopRamdisk

### linuxTmpfsRamdisk

## Only developed for macOS and Linux

### ramdisk

Will correctly inherit either a macRamdisk on macOS or a linuxTmpfsRamdisk (by default) on Linux, depending on which OS kernel one is running on.

## Only developed for Windows

### Nothing yet

## Developed for macOS, Linux and Windows

Nothing yet....

## Example code

This directory provides examples on how to use various libraries, even beyond the ramdisk libraries in this code base.  Some are used for testing the ramdisk code base.  Any user creation or manipulation example code is in an alpha state, and macOS only at this time.

Unionfs related code is in an alpha state and also macOS only.

The ramdisk example code is cross platform in an alpha state.

The menu code is cross platform, in an alpha state.

# Future work:

## Windows

Will call a currently available ramdisk executable to create a ramdisk.

## Languages

Currently written/tested in only python v3.9+

Future plans to duplicate libraries, tests and examples in other languages as well.

