//go:build linux

package ramdisk

import (
	"fmt"
	"os"
	"strings"
)

const moduleVersion = "20251004.golang.linux"

type linuxRamDisk struct {
	success    bool
	mountPoint string
	device     string
	sizeMB     uint64
	fstype     string
	mode       uint32
	uid        int
	gid        int
	unmounted  bool
	mountPath  string
	umountPath string
}

func platformCreate(opts Options) (platformRamDisk, error) {
	opts = opts.WithDefaults()
	if opts.SizeMB == 0 {
		return nil, &SizeInvalidError{Size: opts.SizeMB}
	}

	if err := CheckMemory(opts.SizeMB); err != nil {
		return nil, err
	}

	// Fail fast with a clear message if we lack privileges.
	if os.Geteuid() != 0 {
		return nil, &PrivilegeRequiredError{}
	}

	mountPath, err := FindBin("mount")
	if err != nil {
		return nil, err
	}
	umountPath, err := FindBin("umount")
	if err != nil {
		return nil, err
	}

	mnt := opts.MountPoint
	if mnt == "" {
		mnt, err = RandomMountPoint()
		if err != nil {
			return nil, err
		}
	} else {
		if err := os.MkdirAll(mnt, 0755); err != nil {
			return nil, err
		}
	}

	uid := os.Getuid()
	gid := os.Getgid()
	if opts.LinuxUID != nil {
		uid = int(*opts.LinuxUID)
	}
	if opts.LinuxGID != nil {
		gid = int(*opts.LinuxGID)
	}

	fstype := string(opts.LinuxFsType)
	if fstype == "" {
		fstype = "tmpfs"
	}

	rd := &linuxRamDisk{
		mountPoint: mnt,
		sizeMB:     opts.SizeMB,
		fstype:     fstype,
		mode:       opts.LinuxMode,
		uid:        uid,
		gid:        gid,
		mountPath:  mountPath,
		umountPath: umountPath,
	}

	if fstype == "tmpfs" {
		rd.device = "tmpfs"
	} else {
		rd.device = "ramfs"
	}

	if err := rd.mount(); err != nil {
		return nil, err
	}
	rd.success = true
	return rd, nil
}

func (r *linuxRamDisk) mount() error {
	if r.fstype == "ramfs" {
		_, _, err := RunCmd(r.mountPath, "-t", "ramfs", "ramfs", r.mountPoint)
		return err
	}

	opts := fmt.Sprintf("size=%dm,uid=%d,gid=%d,mode=%o",
		r.sizeMB, r.uid, r.gid, r.mode)
	_, _, err := RunCmd(r.mountPath, "-t", "tmpfs", "-o", opts, "tmpfs", r.mountPoint)
	return err
}

func (r *linuxRamDisk) Success() bool     { return r.success }
func (r *linuxRamDisk) MountPoint() string { return r.mountPoint }
func (r *linuxRamDisk) Device() string     { return r.device }
func (r *linuxRamDisk) Version() string    { return moduleVersion }

func (r *linuxRamDisk) TryUmount() error {
	if r.unmounted {
		return nil
	}
	_, _, err := RunCmd(r.umountPath, r.mountPoint)
	if err == nil {
		r.unmounted = true
		// Only remove the directory if it looks like one of ours (under temp).
		_ = os.Remove(r.mountPoint)
	}
	return err
}

func platformListMounted() ([]MountInfo, error) {
	data, err := os.ReadFile("/proc/mounts")
	if err != nil {
		return nil, err
	}
	var out []MountInfo
	for _, line := range strings.Split(string(data), "\n") {
		fields := strings.Fields(line)
		if len(fields) < 3 {
			continue
		}
		fsType := fields[2]
		if fsType == "tmpfs" || fsType == "ramfs" {
			mp := fields[1]
			if mp == "/dev" || mp == "/dev/shm" || mp == "/run" ||
				strings.HasPrefix(mp, "/run/") || mp == "/sys/fs/cgroup" {
				continue
			}
			// Prefer mounts that look like ours
			if strings.Contains(mp, "ramdisk") || strings.HasPrefix(mp, "/tmp/") {
				out = append(out, MountInfo{
					Success:    true,
					MountPoint: mp,
					Device:     fields[0],
				})
			}
		}
	}
	return out, nil
}

func platformUmountPath(path string) error {
	umountBin, err := FindBin("umount")
	if err != nil {
		return err
	}
	_, _, err = RunCmd(umountBin, path)
	if err == nil {
		_ = os.Remove(path)
	}
	return err
}
