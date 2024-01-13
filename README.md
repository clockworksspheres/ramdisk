# ramdisk

Interface to use, eventually for cross-platform setup and maintenance of ramdisk, primarily for build pipelines and unittesting, for DevOps purposes.

* faster builds
* get around corrupt build cache problems (cache poisoning)
* testing code requiring a clean, fast disk

Historically speaking, this was a problem around the turn of the century, unless one had a large memory Solaris system, or expensive other kind of unix system.

This is why the ramdisk code was written for non-windows systems first.

The primary author of the ramdisk code first became a fan of building scientific software where he could in ramdisk where he could on systems with IDE spinning disks.  This is when he became aware of problems where builds were taking just as long, or errors would persist between builds, then becoming aware of build systems having caching type mechanisms, often in completely separate, proprietary parts of the operating system, to keep their secret sauce secret.  Using filesystem watching, or tripwire software, watching for those locations, one could find those locations, and mount a ramdisk at those locations as well, just prior to a build, perform a build, for a clean cache, and once the build was complete, unmount both the disk where the build was done, and the build where the cache was mounted, so next build, there would be no cache to pick up the old build, instead of the new changes, and the new changes would automatically get picked up and built.

Let me try again.

Caches are great.  What happens with caching - if part of a cached build is found, that cached part will be used, instead of recompiling that part, and continue the process the compile.  This makes building software much faster.  However, the compile is supposed to check to make sure none of the code that makes up that chunk has changed... significantly.... then there's an argument over what significantly means or not... the person that wants the compiling done may really need that part compiled, while the person that made the build tool may not think that part is meaningful to compile... then we start calling that "cache poisoning"..... 

Then the importance of the prior paragraph makes more sense.  Cache poisoning becomes a big deal, and ramdisks become very important in build chains when specific needs aren't met, especially when building per specific needs in scientific build tool stacks.a build will skip compiling and one will never be able to get the feature one needs in the build tool unless they can figure out how to fix the build tool chain.  Or use a ramdisk, or similar method to get past the cache poisoning problem.


## NOTE:
The code has two branches, master (hopefully stable) and dev (not necessarily stable).  The goal is to only merge to develop when functionality is stable and tests have been written for that functionality.

Initially developed for python 2.6, but code has since been migrated to 3.9+.  Not believed to work on the python 2 branch any longer.

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

