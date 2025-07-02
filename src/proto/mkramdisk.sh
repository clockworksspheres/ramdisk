#!/bin/bash

# Size of the RAM disk in bytes (1 GB in this example)
size_bytes=$((1024 * 1024 * 1024))

# Calculate the number of 512-byte sectors
sectors=$((size_bytes / 512))

# Create the RAM disk
ramdisk_dev=$(hdiutil attach -nomount ram://$sectors)

# Format the RAM disk with APFS
newfs_apfs -v "RAMDisk" $ramdisk_dev

# Create the mount point
mount_point="/tmp/foobar"
mkdir -p $mount_point

# Mount the RAM disk
mount -t apfs $ramdisk_dev $mount_point

# Verify the mount
df -h $mount_point

# Output instructions to unmount and eject the RAM disk
echo "To unmount and eject the RAM disk, run:"
echo "umount $mount_point"
echo "diskutil eject $ramdisk_dev"

