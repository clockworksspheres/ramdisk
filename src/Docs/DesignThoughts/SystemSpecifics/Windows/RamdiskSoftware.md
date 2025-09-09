# What Software is working behind the ramdisk interface?

* AIMtk supports Windows 11
* ImDisk supports Windows 10 and below

Both of these products need to be downloaded pre-installed, drivers installed and put in the user's path before the ramdisk interface software works.

NOTE: the AIMtk software must be acquired/purchased from [Arsenal Recon](https://arsenalrecon.com/products/arsenal-image-mounter)

# AIMtk

## Configuring

### Setting the windows "PATH" variable

To set AIMtk to be in your windows PATH:

```

```


## Running aim_ll

### Command line help

```
>aim_ll
Low-level command line interface to Arsenal Image Mounter virtual
SCSI miniport driver.

For version information, license, copyrights and credits, type aim_ll --version

Setup syntax:
aim_ll --install setup_directory
        Installs Arsenal Image Mounter driver from a directory with setup
        files.

aim_ll --uninstall
        Uninstalls Arsenal Image Mounter driver.

aim_ll --rescan
        Rescans SCSI bus on installed adapter Useful to cleanup virtual disks
        where connection to backend storage service is lost.

Manage virtual disks:
aim_ll -a -t type [-n] [-o opt1[,opt2 ...]] [-f|-F file] [-s size] [-b offset]
       [-S sectorsize] [-u devicenumber] [-m mountpoint]
       [-p "format-parameters"] [-P]
aim_ll -d|-D [-u devicenumber | -m mountpoint] [-P]
aim_ll -R -u unit
aim_ll -l [-u devicenumber | -m mountpoint]
aim_ll -e [-s size] [-o opt1[,opt2 ...]] [-u devicenumber | -m mountpoint]

-a      Attach a virtual disk. This will configure and attach a virtual disk
        with the parameters specified and attach it to the system.

-d      Detach a virtual disk from the system and release all resources.
        Use -D to force removal even if the device is in use.

-R      Emergency removal of hung virtual disks. Should only be used as a last
        resort when a virtual disk has some kind of problem that makes it
        impossible to detach it in a safe way. This could happen for example
        for proxy-type virtual disks sometimes when proxy communication fails.
        Note that this does not attempt to dismount filesystem or lock the
        volume in any way so there is a potential risk of data loss. Use with
        caution!

-e      Edit an existing virtual disk.

        Along with the -s parameter extends the size of an existing virtual
        disk.

        Along with the -o parameter changes media characteristics for an
        existing virtual disk. Options that can be changed on existing virtual
        disks are those specifying wether or not the media of the virtual disk
        should be writable and/or removable.

-t type
        Select the backingstore for the virtual disk.

vm      Storage for this type of virtual disk is allocated from virtual memory
        in the system process. If a file is specified with -f that file is
        is loaded into the memory allocated for the disk image.

file    A file specified with -f file becomes the backingstore for this
        virtual disk.

proxy   The actual backingstore for this type of virtual disk is controlled by
        a storage server accessed by the driver on this machine by
        sending storage I/O requests through a named pipe specified with -f.

-f file or -F file
        Filename to use as backingstore for the file type virtual disk, to
        initialize a vm type virtual disk or name of a named pipe for I/O
        client/server communication for proxy type virtual disks. For proxy
        type virtual disks "file" may be a COM port or a remote server
        address if the -o options includes "ip" or "comm".

        Instead of using -f to specify 'DOS-style' paths, such as
        C:\dir\image.bin or \\server\share\image.bin, you can use -F to
        specify 'NT-style' native paths, such as
        \Device\Harddisk0\Partition1\image.bin. This makes it possible to
        specify files on disks or communication devices that currently have no
        drive letters assigned.

-l      List configured devices. If given with -u or -m, display details about
        that particular device.

-n      When printing listing devices, print only the unit number without other
        information.

-s size
        Size of the virtual disk. Size is number of bytes unless suffixed with
        a b, k, m, g, t, K, M, G or T which denotes number of 512-byte blocks,
        thousand bytes, million bytes, billion bytes, trillion bytes,
        kilobytes, megabytes, gigabytes and terabytes respectively. The suffix
        can also be % to indicate percentage of free physical memory which
        could be useful when creating vm type virtual disks. It is optional to
        specify a size unless the file to use for a file type virtual disk does
        not already exist or when a vm type virtual disk is created without
        specifying an initialization image file using the -f or -F. If size is
        specified when creating a file type virtual disk, the size of the file
        used as backingstore for the virtual disk is adjusted to the new size
        specified with this size option.

        The size can be a negative value to indicate the size of free physical
        memory minus this size. If you e.g. type -400M the size of the virtual
        disk will be the amount of free physical memory minus 400 MB.

-b offset
        Specifies an offset in an image file where the virtual disk begins. All
        offsets of I/O operations on the virtual disk will be relative to this
        offset. This parameter is particularily useful when mounting a specific
        partition in an image file that contains an image of a complete hard
        disk, not just one partition. This parameter has no effect when
        creating a blank vm type virtual disk. When creating a vm type virtual
        disk with a pre-load image file specified with -f or -F parameters, the
        -b parameter specifies an offset in the image file where the image to
        be loaded into the vm type virtual disk begins.

        Specify auto as offset to automatically select offset for a few known
        non-raw disk image file formats. Currently auto-selection is supported
        for Nero .nrg and Microsoft .sdi image files.

-S sectorsize
        Sectorsize to use for the virtual disk device. Default value is 512
        bytes except for CD-ROM/DVD-ROM style devices where 2048 bytes is used
        by default.

-p "format-parameters"
        If -p is specified the 'format' command is invoked to create a
        filesystem when the new virtual disk has been created.
        "format-parameters" must be a parameter string enclosed within
        double-quotes. The string is added to the command line that starts
        'format'. You usually specify something like "/fs:ntfs /q /y", that
        is, create an NTFS filesystem with quick formatting and without user
        interaction.

        If you specify empty format parameters, -p "", a partition is created
        but it is not formatted.

-o option
        Set or reset options.

ro      Creates a read-only virtual disk. For vm type virtual disks, this
        option can only be used if the -f option is also specified.

rw      Specifies that the virtual disk should be read/writable. This is the
        default setting. It can be used with the -e parameter to set an
        existing read-only virtual disk writable.

fksig   If this flag is set, the driver will report a random fake disk
        signature to Windows instead of any existing one, in case the master
        boot record has otherwise apparently valid data.

sparse  Sets NTFS sparse attribute on image file. This has no effect on proxy
        or vm type virtual disks.

rem     Specifies that the device should be created with removable media
        characteristics. This changes the device properties returned by the
        driver to the system. For example, this changes how some filesystems
        cache write operations.

fix     Specifies that the media characteristics of the virtual disk should be
        fixed media, as opposed to removable media specified with the rem
        option. Fixed media is the default setting. The fix option can be used
        with the -e parameter to set an existing removable virtual disk as
        fixed.

saved   Clears the 'image modified' flag from an existing virtual disk. This
        flag is set by the driver when an image is modified and is displayed
        in the -l output for a virtual disk. The 'saved' option is only valid
        with the -e parameter.

        Note that virtual floppy or CD/DVD-ROM drives are always read-only and
        removable devices and that cannot be changed.

cd      Creates a virtual CD-ROM/DVD-ROM.

fd      Creates a virtual floppy disk.

        NOTE: cd and fd options are currently not supported by the driver.

hd      Creates a virtual hard disk. This is the default.

raw     Creates a device object with "controller" device type. The system will
        not attempt to use such devices as a storage device, but it could be
        useful in combination with third-party drivers that can provide further
        device objects using this virtual disk device as a backing store.

ip      Can only be used with proxy-type virtual disks. With this option, the
        user-mode service component is initialized to connect to a
        storage server using TCP/IP. With this option, the -f switch specifies
        the remote host optionally followed by a colon and a port number to
        connect to.

comm    Can only be used with proxy-type virtual disks. With this option, the
        user-mode service component is initialized to connect to a
        storage server through a COM port. With this option, the -f switch
        specifies the COM port to connect to, optionally followed by a colon,
        a space, and then a device settings string with the same syntax as the
        MODE command.

shm     Can only be used with proxy-type virtual disks. With this option, the
        driver communicates with a storage server on the same computer using
        shared memory block to transfer I/O data.

awe     Can only be used with file-type virtual disks. With this option, the
        driver copies contents of image file to physical memory. No changes are
        written to image file. If this option is used in combination with  no
        image file name, a physical memory block will be used without loading
        an image file onto it. In that case, -s parameter is needed to specify
        size of memory block.

bswap   Instructs driver to swap each pair of bytes read from or written to
        image file. Useful when examining images from some embedded systems
        and similar where data is stored in reverse byte order.

        NOTE: This option is currently not supported by the driver.

par     Parallel I/O. Valid for file-type virtual disks. With this flag set,
        driver sends read and write requests for the virtual disk directly down
        to the driver that handles the image file, within the SCSIOP dispatch
        routine. This flag is intended for developers who provide their own
        driver that handles image file requests. Such driver need to handle
        requests at DISPATCH_LEVEL at any time, otherwise system crashes are
        very likely to happen. *Never* use this flag when mounting image files!
        Use it *only* with special purpose drivers that can meet all neeed
        requirements!

buf     Buffered I/O. Valid for file-type virtual disks. With this flag set,
        driver opens image file in buffered I/O mode. This is usually less
        efficient, but it could be required to for example mount an image file
        with smaller sector size than the volume where the image file is
        stored.

-u devicenumber
        Six hexadecimal digits indicating SCSI path, target and lun numbers
        for a device. Format: LLTTPP. Along with -a, request a specific device
        number for the new device instead of automatic allocation. Along with
        -d or -l specifies the unit number of the virtual disk to remove or
        query.

-m mountpoint
        Specifies a drive letter or mount point for the new virtual disk, the
        virtual disk to query or the virtual disk to remove. When creating a
        new virtual disk you can specify #: as mountpoint in which case the
        first unused drive letter is automatically used.

        Note that even if you don't specify -m, Windows normally assigns drive
        letters to new volumes anyway. This behaviour can be changed using the
        MOUNTVOL command line tool.
```


# ImDisk

```
> imdisk
Control program for the ImDisk Virtual Disk Driver.
For copyrights and credits, type imdisk --version

Syntax:
imdisk -a -t type -m mountpoint [-n] [-o opt1[,opt2 ...]] [-f|-F file]
       [-s size] [-b offset] [-v partition] [-S sectorsize] [-u unit]
       [-x sectors/track] [-y tracks/cylinder] [-p "format-parameters"] [-P]
imdisk -d|-D [-u unit | -m mountpoint] [-P]
imdisk -R -u unit
imdisk -l [-u unit | -m mountpoint]
imdisk -e [-s size] [-o opt1[,opt2 ...]] [-u unit | -m mountpoint]

-a      Attach a virtual disk. This will configure and attach a virtual disk
        with the parameters specified and attach it to the system.

-d      Detach a virtual disk from the system and release all resources.
        Use -D to force removal even if the device is in use.

-R      Emergency removal of hung virtual disks. Should only be used as a last
        resort when a virtual disk has some kind of problem that makes it
        impossible to detach it in a safe way. This could happen for example
        for proxy-type virtual disks sometimes when proxy communication fails.
        Note that this does not attempt to dismount filesystem or lock the
        volume in any way so there is a potential risk of data loss. Use with
        caution!

-e      Edit an existing virtual disk.

        Along with the -s parameter extends the size of an existing virtual
        disk. Note that even if the disk can be extended successfully, the
        existing filesystem on it can only be extended to fill the new size
        without re-formatting if you are running Windows 2000 or later and the
        current filesystem is NTFS.

        Along with the -o parameter changes media characteristics for an
        existing virtual disk. Options that can be changed on existing virtual
        disks are those specifying wether or not the media of the virtual disk
        should be writable and/or removable.

-t type
        Select the backingstore for the virtual disk.

vm      Storage for this type of virtual disk is allocated from virtual memory
        in the system process. If a file is specified with -f that file is
        is loaded into the memory allocated for the disk image.

file    A file specified with -f file becomes the backingstore for this
        virtual disk.

proxy   The actual backingstore for this type of virtual disk is controlled by
        an ImDisk storage server accessed by the driver on this machine by
        sending storage I/O request through a named pipe specified with -f.

-f file or -F file
        Filename to use as backingstore for the file type virtual disk, to
        initialize a vm type virtual disk or name of a named pipe for I/O
        client/server communication for proxy type virtual disks. For proxy
        type virtual disks "file" may be a COM port or a remote server
        address if the -o options includes "ip" or "comm".

        Instead of using -f to specify 'DOS-style' paths, such as
        C:\dir\image.bin or \\server\share\image.bin, you can use -F to
        specify 'NT-style' native paths, such as
        \Device\Harddisk0\Partition1\image.bin. This makes it possible to
        specify files on disks or communication devices that currently have no
        drive letters assigned.

-l      List configured devices. If given with -u or -m, display details about
        that particular device.

-n      When printing ImDisk device names, print only the unit number without
        the \Device\ImDisk prefix.

-s size
        Size of the virtual disk. Size is number of bytes unless suffixed with
        a b, k, m, g, t, K, M, G or T which denotes number of 512-byte blocks,
        thousand bytes, million bytes, billion bytes, trillion bytes,
        kilobytes, megabytes, gigabytes and terabytes respectively. The suffix
        can also be % to indicate percentage of free physical memory which
        could be useful when creating vm type virtual disks. It is optional to
        specify a size unless the file to use for a file type virtual disk does
        not already exist or when a vm type virtual disk is created without
        specifying an initialization image file using the -f or -F. If size is
        specified when creating a file type virtual disk, the size of the file
        used as backingstore for the virtual disk is adjusted to the new size
        specified with this size option.

        The size can be a negative value to indicate the size of free physical
        memory minus this size. If you e.g. type -400M the size of the virtual
        disk will be the amount of free physical memory minus 400 MB.

-b offset
        Specifies an offset in an image file where the virtual disk begins. All
        offsets of I/O operations on the virtual disk will be relative to this
        offset. This parameter is particularily useful when mounting a specific
        partition in an image file that contains an image of a complete hard
        disk, not just one partition. This parameter has no effect when
        creating a blank vm type virtual disk. When creating a vm type virtual
        disk with a pre-load image file specified with -f or -F parameters, the
        -b parameter specifies an offset in the image file where the image to
        be loaded into the vm type virtual disk begins.

        Specify auto as offset to automatically select offset for a few known
        non-raw disk image file formats. Currently auto-selection is supported
        for Nero .nrg and Microsoft .sdi image files.

-v partition
        Specifies which partition to mount when mounting a raw hard disk image
        file containing a master boot record and partitions.

        Partitions are numbered in the order they are found in primary
        partition table and then in extended partition tables.

-S sectorsize
        Sectorsize to use for the virtual disk device. Default value is 512
        bytes except for CD-ROM/DVD-ROM style devices where 2048 bytes is used
        by default.

-x sectors/track
        See the description of the -y option below.

-y tracks/cylinder
        The -x and -y options can be used to specify a synthetic geometry.
        This is useful for constructing bootable images for later download to
        physical devices. Default values depend on the device-type specified
        with the -o option. If the 'fd' option is specified the default values
        are based on the virtual disk size, e.g. a 1440K image gets 2
        tracks/cylinder and 18 sectors/track.

-p "format-parameters"
        If -p is specified the 'format' command is invoked to create a
        filesystem when the new virtual disk has been created.
        "format-parameters" must be a parameter string enclosed within
        double-quotes. The string is added to the command line that starts
        'format'. You usually specify something like "/fs:ntfs /q /y", that
        is, create an NTFS filesystem with quick formatting and without user
        interaction.

-o option
        Set or reset options.

ro      Creates a read-only virtual disk. For vm type virtual disks, this
        option can only be used if the -f option is also specified.

rw      Specifies that the virtual disk should be read/writable. This is the
        default setting. It can be used with the -e parameter to set an
        existing read-only virtual disk writable.

sparse  Sets NTFS sparse attribute on image file. This has no effect on proxy
        or vm type virtual disks.

rem     Specifies that the device should be created with removable media
        characteristics. This changes the device properties returned by the
        driver to the system. For example, this changes how some filesystems
        cache write operations.

fix     Specifies that the media characteristics of the virtual disk should be
        fixed media, as opposed to removable media specified with the rem
        option. Fixed media is the default setting. The fix option can be used
        with the -e parameter to set an existing removable virtual disk as
        fixed.

saved   Clears the 'image modified' flag from an existing virtual disk. This
        flag is set by the driver when an image is modified and is displayed
        in the -l output for a virtual disk. The 'saved' option is only valid
        with the -e parameter.

        Note that virtual floppy or CD/DVD-ROM drives are always read-only and
        removable devices and that cannot be changed.

cd      Creates a virtual CD-ROM/DVD-ROM. This is the default if the file
        name specified with the -f option ends with either .iso, .nrg or .bin
        extensions.

fd      Creates a virtual floppy disk. This is the default if the size of the
        virtual disk is any of 160K, 180K, 320K, 360K, 640K, 720K, 820K, 1200K,
        1440K, 1680K, 1722K, 2880K, 123264K or 234752K.

hd      Creates a virtual fixed disk partition. This is the default unless
        file extension or size match the criterias for defaulting to the cd or
        fd options.

raw     Creates a device object with "unknown" device type. The system will not
        attempt to do anything by its own with such devices, but it could be
        useful in combination with third-party drivers that can provide further
        device objects using this virtual disk device as a backing store.

ip      Can only be used with proxy-type virtual disks. With this option, the
        user-mode service component is initialized to connect to an ImDisk
        storage server using TCP/IP. With this option, the -f switch specifies
        the remote host optionally followed by a colon and a port number to
        connect to.

comm    Can only be used with proxy-type virtual disks. With this option, the
        user-mode service component is initialized to connect to an ImDisk
        storage server through a COM port. With this option, the -f switch
        specifies the COM port to connect to, optionally followed by a colon,
        a space, and then a device settings string with the same syntax as the
        MODE command.

shm     Can only be used with proxy-type virtual disks. With this option, the
        driver communicates with a storage server on the same computer using
        shared memory block to transfer I/O data.

awe     Can only be used with file-type virtual disks. With this option, the
        driver copies contents of image file to physical memory. No changes are
        written to image file. If this option is used in combination with  no
        image file name, a physical memory block will be used without loading
        an image file onto it. In that case, -s parameter is needed to specify
        size of memory block. This option requires awealloc driver, which
        requires Windows 2000 or later.

bswap   Instructs driver to swap each pair of bytes read from or written to
        image file. Useful when examining images from some embedded systems
        and similar where data is stored in reverse byte order.

shared  Instructs driver to open image file in shared write mode even when
        image is opened for writing. This can be useful to mount each partition
        of a multi-partition image as separate virtual disks with different
        image file offsets and sizes. It could potentially corrupt filesystems
        if used with incorrect offset and size parameters so use with caution!

par     Parallel I/O. Valid for file-type virtual disks. With this flag set,
        driver sends read and write requests for the virtual disk directly down
        to the filesystem driver that handles the image file, within the same
        thread context as the original request was made. In some scenarios this
        flag can increase performance, particularly when you use several layers
        of virtual disks backed by image files stored on other virtual disks,
        network file shares or similar storage.

        This flag is not supported in all scenarios depending on other drivers
        that need to complete requests to the image file. It could also degrade
        performance or cause reads and writes to fail if underlying drivers
        cannot handle I/O requests simultaneously.

buf     Buffered I/O. Valid for file-type virtual disks. With this flag set,
        driver opens image file in buffered I/O mode. This is usually less
        efficient, but it could be required to for example mount an image file
        with smaller sector size than the volume where the image file is
        stored.

-u unit
        Along with -a, request a specific unit number for the ImDisk device
        instead of automatic allocation. Along with -d or -l specifies the
        unit number of the virtual disk to remove or query.

-m mountpoint
        Specifies a drive letter or mount point for the new virtual disk, the
        virtual disk to query or the virtual disk to remove. When creating a
        new virtual disk you can specify #: as mountpoint in which case the
        first unused drive letter is automatically used.

-P      Persistent. Along with -a, saves registry settings for re-creating the
        same virtual disk automatically when driver is loaded, which usually
        occurs during system startup. Along with -d or -D, existing such
        settings for the removed virtual disk are also removed from registry.
        There are some limitations to what settings could be saved in this way.
        Only features directly implemented in the kernel level driver are
        saved, so for example the -p switch to format a virtual disk will not
        be saved.
```

# Managing differences analysis

First quick scan(with [meld](https://meldmerge.org/)), and the only thing that really stands out is the -P which indicates persistence between reboots.  This interface shouldn't provide that capability, as the purpose of the interface is to provide "Temporary" ramdisks - that act as much the same as possible across OS's.

Other OS's don't provide a "persistence" option like that, and it goes against the notion of a "throw away" ramdisk which is central to this interface.

