package ramdisk

import "path/filepath"

// LinuxFsType selects the Linux in-memory filesystem.
type LinuxFsType string

const (
	LinuxTmpfs LinuxFsType = "tmpfs"
	LinuxRamfs LinuxFsType = "ramfs"
)

// Options configures ramdisk creation. Zero value is valid (512 MiB, temp mount).
type Options struct {
	// SizeMB is the size of the ramdisk in mebibytes (MiB). Must be > 0.
	// Default: 512
	SizeMB uint64

	// MountPoint is an optional explicit mount path. If empty a temporary
	// directory under the system temp dir is created and used.
	MountPoint string

	// LinuxFsType is Linux-only: "tmpfs" (default) or "ramfs".
	// ramfs has no size limit and can consume all RAM.
	LinuxFsType LinuxFsType

	// LinuxMode is Linux-only: directory mode (octal). Default 0700.
	LinuxMode uint32

	// LinuxUID is Linux-only: uid that should own the mount (0 = current user).
	LinuxUID *uint32

	// LinuxGID is Linux-only: gid that should own the mount (0 = current group).
	LinuxGID *uint32

	// MacOSDisableJournal is macOS-only: disable APFS journaling after creation.
	MacOSDisableJournal bool

	// WindowsFsType is Windows-only: filesystem type passed to AIM (default "ntfs").
	WindowsFsType string

	// LinuxSudoPassword is Linux-only: when non-empty and the process is not
	// root, mount/umount are run via `sudo -S` with this password (same model
	// as the Python GUI local_auth dialog).
	LinuxSudoPassword string
}

// DefaultOptions returns a sensible default Options value.
func DefaultOptions() Options {
	return Options{
		SizeMB:        512,
		LinuxFsType:   LinuxTmpfs,
		LinuxMode:     0700,
		WindowsFsType: "ntfs",
	}
}

// WithDefaults fills zero values with defaults and returns the result.
func (o Options) WithDefaults() Options {
	if o.SizeMB == 0 {
		o.SizeMB = 512
	}
	if o.LinuxFsType == "" {
		o.LinuxFsType = LinuxTmpfs
	}
	if o.LinuxMode == 0 {
		o.LinuxMode = 0700
	}
	if o.WindowsFsType == "" {
		o.WindowsFsType = "ntfs"
	}
	return o
}

// MountInfo describes a mounted (or previously mounted) ramdisk.
type MountInfo struct {
	Success    bool
	MountPoint string
	Device     string
}

// AbsMountPoint returns an absolute form of MountPoint when possible.
func (m MountInfo) AbsMountPoint() string {
	if m.MountPoint == "" {
		return ""
	}
	abs, err := filepath.Abs(m.MountPoint)
	if err != nil {
		return m.MountPoint
	}
	return abs
}
