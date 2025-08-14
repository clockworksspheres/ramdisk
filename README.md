
Runs on both macOS and Linux.

Python 3.9+

# ramdisk

Interface to use, eventually for cross-platform setup and maintenance of ramdisk, primarily for build pipelines and unittesting, for DevOps purposes.  This interface is the same across platforms, so you don't need to know how ramdisks work on every platform.  One interface, multiple OS platforms.

* faster builds
* get around corrupt build cache problems (cache poisoning)
* testing code requiring a clean, fast disk

Historically speaking, this was a problem around the turn of the century, unless one had a large memory Solaris system, or expensive other kind of unix system.

This is why the ramdisk code was written for non-windows systems first.

The primary author of the ramdisk code first became a fan of building scientific software where he could in ramdisk where he could on systems with IDE spinning disks.  This is when he became aware of problems where builds were taking just as long, or errors would persist between builds, then becoming aware of build systems having caching type mechanisms, often in completely separate, proprietary parts of the operating system, to keep their secret sauce secret.  Using filesystem watching, or tripwire software, watching for those locations, one could find those locations, and mount a ramdisk at those locations as well, just prior to a build, perform a build, for a clean cache, and once the build was complete, unmount both the disk where the build was done, and the build where the cache was mounted, so next build, there would be no cache to pick up the old build, instead of the new changes, and the new changes would automatically get picked up and built.

Let me try again.

Caches are great.  What happens with caching - if part of a cached build is found, that cached part will be used, instead of recompiling that part, and continue the process the compile.  This makes building software much faster.  However, the compile is supposed to check to make sure none of the code that makes up that chunk has changed... significantly.... then there's an argument over what significantly means or not... the person that wants the compiling done may really need that part compiled, while the person that made the build tool may not think that part is meaningful to compile... then we start calling that "cache poisoning"..... 

Then the importance of the prior paragraph makes more sense.  Cache poisoning becomes a big deal, and ramdisks become very important in build chains when specific needs aren't met, especially when building per specific needs in scientific build tool stacks.a build will skip compiling and one will never be able to get the feature one needs in the build tool unless they can figure out how to fix the build tool chain.  Or use a ramdisk, or similar method to get past the cache poisoning problem.

One can recursively remove or erase caches - but they're not in the same location from project to project.

Recursively removing directory structures is very dangerous, if one gets it wrong, parts of the operating system can go missing, personal directories, shared scientific data that is worth millions of dollars, etc, etc.  It's easier to deal with mounted ramdisks, that if necessary, can be mounted safely over top of existing structures, than arbitrarily erasing potentially large parts of a file system without a safe recovery mechanism.

Unmounting a ramdisk is much faster than removing or erasing a potentially large cashe set as well.


## NOTE:
The code has two branches, ux (hopefully stable) and dev (not necessarily stable).  The goal is to only merge to develop when functionality is stable and tests have been written for that functionality.

Initially developed for python 2.6, but code has since been migrated to 3.9+.  Not believed to work on the python 2 branch any longer.

### Mac Note

Instanciating the RamDisk class will create a ramdisk that you can use - in chunks of 1Mb.

ramdisks do not need to be managed by root on macOS.   Tests & DevOps creating and managing ramdisks can be run as a user.

### Linux Note

Ramdisk class that can use either current method for creating a ramdisk on Linux, currently working on a tmpfs version....  Tests & DevOps creating and managing ramdisks must be carefully managed by root.

## Used As a library

### macRamdisk

tested on macOS Sierra, Ventura, Sonoma and Sequoia

## Only developed for Linux

## As a library

### linuxLoopRamdisk

### linuxTmpfsRamdisk

tested on Rocky 9, 10 and Ubuntu 24.04 & 25.04

## Only developed for macOS and Linux

### ramdisk

Will correctly inherit either a macRamdisk on macOS or a linuxTmpfsRamdisk (by default) on Linux, depending on which OS kernel one is running on.

## Only developed for Windows

### Looking at working with ImDisk - so far - nothing yet

## Developed for macOS, Linux and Windows

Windows ramdisk is a prototype in flux, may or may not work.

## Example code

The exaamples directory provides examples on how to use various libraries, even beyond the ramdisk libraries in this code base.  Some are used for testing the ramdisk code base.  Any user creation or manipulation example code is in an alpha state, and some are macOS only at this time.

Unionfs related code is in an alpha state and also macOS only.

The ramdisk example code is cross platform in an alpha state.

The menu code is cross platform, in an alpha state.

# Future work:

## Windows

Will call a currently available ramdisk executable, like ImDisk, to create a ramdisk.

Prototype in flux, may or may not work.

## Languages

Currently written/tested in only python v3.9+

Future plans to duplicate libraries, tests and examples in other languages as well.

## Tracking

Very greatful for any contributions/pull requests to help with the project!

## Python Libraries to include, and how to include them for running the UI, the Environment.py, etc.


### Cross Platform

pyside6
pyinstaller
packaging


PySide6 cross platform library for the Graphical User Interface

Pyinstaller cross platform library to create the installer to bundle the GUI into a windows app package

packaging.version.parse is to replace distutils.version.LooseVersion, for comparing versions of operating systems in CheckApplicable.  As of 4/13/25, CheckApplicable is entirely distutils, and needs to be refactored to packaging for python 3.10+.

#### Macos Specific

##### None need currently

##### How to install non-native python libraries on Macos

``` bash

directory="./packenv"
actfile="./packenv/bin/activate"

if [ ! -d "$directory" ] || [ ! -f "$actfile" ] ; then
  python3 -m venv packenv
  source packenv/bin/activate
  pip3 install --upgrade pip

  pip3 install PySide6 PyInstaller
  pip3 install --upgrade PyInstaller pyinstaller-hooks-contrib
  pip3 install packaging
else
  source packenv/bin/activate
fi
```

### Linux Specific

##### None need currently

##### How to install non-native python libraries on Linux

``` bash

directory="./packenv"
actfile="./packenv/bin/activate"

if [ ! -d "$directory" ] || [ ! -f "$actfile" ] ; then
  python3 -m venv packenv
  source packenv/bin/activate
  pip3 install --upgrade pip

  pip3 install PySide6 PyInstaller
  pip3 install --upgrade PyInstaller pyinstaller-hooks-contrib
  pip3 install packaging
else
  source packenv/bin/activate
fi
```

#### Windows Specific

pywin32  

pywin32 windows library to add windows functionality for the Environment.py to match the python functionality found natively in unix environments.

##### How to to install non-native python libraries in windows


