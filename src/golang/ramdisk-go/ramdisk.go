// Package ramdisk provides a cross-platform interface for creating and
// managing in-memory disks (ramdisks) on Linux (tmpfs/ramfs), macOS
// (hdiutil + APFS) and Windows (Arsenal Image Mounter / AIM Toolkit).
//
// It is a Go port of the Python library
// https://github.com/clockworksspheres/ramdisk
//
// Example:
//
//	rd, err := ramdisk.New(ramdisk.Options{SizeMB: 512})
//	if err != nil {
//	    log.Fatal(err)
//	}
//	defer rd.Umount()
//
//	fmt.Println("Mounted at", rd.MountPoint())
package ramdisk

// platformRamDisk is the internal interface implemented by each OS backend.
type platformRamDisk interface {
	Success() bool
	MountPoint() string
	Device() string
	Version() string
	TryUmount() error
}

// RamDisk is a cross-platform handle to a mounted in-memory filesystem.
// Instantiating a RamDisk creates and mounts the filesystem. Calling
// Umount (or letting the finalizer run) detaches it.
type RamDisk struct {
	inner platformRamDisk
}

// New creates and mounts a new ramdisk with the given options.
func New(opts Options) (*RamDisk, error) {
	opts = opts.WithDefaults()
	if opts.SizeMB == 0 {
		return nil, &SizeInvalidError{Size: opts.SizeMB}
	}
	inner, err := platformCreate(opts)
	if err != nil {
		return nil, err
	}
	return &RamDisk{inner: inner}, nil
}

// WithSize is a convenience constructor: size in MiB, random temporary mount point.
func WithSize(sizeMB uint64) (*RamDisk, error) {
	return New(Options{SizeMB: sizeMB})
}

// WithSizeAndMount is a convenience constructor: size in MiB and explicit mount point.
func WithSizeAndMount(sizeMB uint64, mountPoint string) (*RamDisk, error) {
	return New(Options{SizeMB: sizeMB, MountPoint: mountPoint})
}

// Success reports whether the ramdisk was successfully created and mounted.
func (r *RamDisk) Success() bool {
	if r == nil || r.inner == nil {
		return false
	}
	return r.inner.Success()
}

// MountPoint returns the path where the ramdisk is mounted.
func (r *RamDisk) MountPoint() string {
	if r == nil || r.inner == nil {
		return ""
	}
	return r.inner.MountPoint()
}

// Device returns the underlying device identifier
// (e.g. /dev/disk4s1 on macOS, "tmpfs" on Linux, AIM id on Windows).
func (r *RamDisk) Device() string {
	if r == nil || r.inner == nil {
		return ""
	}
	return r.inner.Device()
}

// GetData returns (success, mount_point, device) – mirrors the original
// Python getData().
func (r *RamDisk) GetData() MountInfo {
	return MountInfo{
		Success:    r.Success(),
		MountPoint: r.MountPoint(),
		Device:     r.Device(),
	}
}

// Umount unmounts / detaches the ramdisk. Prefer this over relying on
// finalizers when you need to handle errors.
func (r *RamDisk) Umount() error {
	if r == nil || r.inner == nil {
		return nil
	}
	return r.inner.TryUmount()
}

// TryUmount attempts to unmount without requiring the caller to discard
// the handle (best-effort, idempotent).
func (r *RamDisk) TryUmount() error {
	return r.Umount()
}

// Detach releases the Go handle without unmounting the ramdisk.
// The OS mount remains active until UmountPath is called (or the
// system is rebooted). Returns the mount info so the caller can
// record the path/device for later cleanup.
//
// After Detach the RamDisk must not be used again (Umount becomes a no-op).
func (r *RamDisk) Detach() MountInfo {
	info := r.GetData()
	if r != nil {
		// Drop the platform handle so nothing can unmount on GC / exit.
		r.inner = nil
	}
	return info
}

// Version returns the library / platform-module version string.
func (r *RamDisk) Version() string {
	if r == nil || r.inner == nil {
		return ""
	}
	return r.inner.Version()
}

// ListMounted returns currently mounted ramdisks (platform-specific heuristics).
func ListMounted() ([]MountInfo, error) {
	return platformListMounted()
}

// UmountPath unmounts a ramdisk by mount-point or device path.
func UmountPath(path string) error {
	return platformUmountPath(path)
}
