//go:build linux

package ramdisk

import (
	"bytes"
	"fmt"
	"os"
	"os/exec"
	"regexp"
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
	sudoPass   string // non-empty → elevate via sudo -S (Python local_auth style)
}

func platformCreate(opts Options) (platformRamDisk, error) {
	opts = opts.WithDefaults()
	if opts.SizeMB == 0 {
		return nil, &SizeInvalidError{Size: opts.SizeMB}
	}

	if err := CheckMemory(opts.SizeMB); err != nil {
		return nil, err
	}

	mountPath, err := FindBin("mount")
	if err != nil {
		return nil, err
	}
	umountPath, err := FindBin("umount")
	if err != nil {
		return nil, err
	}

	needElevate := os.Geteuid() != 0
	if needElevate && opts.LinuxSudoPassword == "" {
		return nil, &PrivilegeRequiredError{}
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
		sudoPass:   opts.LinuxSudoPassword,
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

// runSudoS runs argv under `sudo -S`, feeding password on stdin.
// Mirrors Python RunWith.runWithSudo().
func runSudoS(password string, argv ...string) (stdout, stderr string, err error) {
	sudo, err := FindBin("sudo")
	if err != nil {
		return "", "", err
	}
	full := append([]string{sudo, "-S"}, argv...)
	cmd := exec.Command(full[0], full[1:]...)
	cmd.Stdin = bytes.NewBufferString(password + "\n")
	var outBuf, errBuf bytes.Buffer
	cmd.Stdout = &outBuf
	cmd.Stderr = &errBuf
	err = cmd.Run()
	return outBuf.String(), errBuf.String(), err
}

func runMaybeSudo(password string, argv ...string) (stdout, stderr string, err error) {
	if password != "" && os.Geteuid() != 0 {
		return runSudoS(password, argv...)
	}
	return RunCmd(argv[0], argv[1:]...)
}

func (r *linuxRamDisk) mount() error {
	if r.fstype == "ramfs" {
		_, stderr, err := runMaybeSudo(r.sudoPass, r.mountPath, "-t", "ramfs", "ramfs", r.mountPoint)
		if err != nil {
			return fmt.Errorf("mount ramfs failed: %w (%s)", err, stderr)
		}
		return nil
	}

	opts := fmt.Sprintf("size=%dm,uid=%d,gid=%d,mode=%o",
		r.sizeMB, r.uid, r.gid, r.mode)
	_, stderr, err := runMaybeSudo(r.sudoPass, r.mountPath, "-t", "tmpfs", "-o", opts, "tmpfs", r.mountPoint)
	if err != nil {
		return fmt.Errorf("mount tmpfs failed: %w (%s)", err, stderr)
	}
	return nil
}

func (r *linuxRamDisk) Success() bool     { return r.success }
func (r *linuxRamDisk) MountPoint() string { return r.mountPoint }
func (r *linuxRamDisk) Device() string     { return r.device }
func (r *linuxRamDisk) Version() string    { return moduleVersion }

func (r *linuxRamDisk) TryUmount() error {
	if r.unmounted {
		return nil
	}
	_, stderr, err := runMaybeSudo(r.sudoPass, r.umountPath, r.mountPoint)
	if err != nil {
		return fmt.Errorf("umount failed: %w (%s)", err, stderr)
	}
	r.unmounted = true
	if strings.Contains(r.mountPoint, "ramdisk-") {
		_ = os.Remove(r.mountPoint)
	}
	return nil
}

func platformListMounted() ([]MountInfo, error) {
	// Match Python linuxTmpfsRamdisk.getMountDisks():
	//   - only lines whose device field is "tmpfs"
	//   - skip the system exclude list and a few path patterns
	//   - everything else is treated as a user/tmpfs ramdisk
	stdout, _, err := RunCmd("mount")
	if err != nil {
		return nil, err
	}

	// Same systemDisks list as Python getMountDisks()
	systemDisks := map[string]bool{
		"/dev/shm": true,
		"/run":     true,
		"/run/credentials/systemd-journald.service": true,
		"/run/credentials/systemd-resolved.service": true,
		"/run/snapd/ns": true,
		"/var/snap":     true,
	}
	reRunUser := regexp.MustCompile(`^/run/user/\d+$`)

	var out []MountInfo
	seen := map[string]bool{}
	for _, line := range strings.Split(stdout, "\n") {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		fields := strings.Fields(line)
		// mount format: tmpfs on /path type tmpfs (...)
		// Python uses split()[0] as device and split()[2] as mount name
		if len(fields) < 3 {
			continue
		}
		if fields[0] != "tmpfs" {
			continue
		}
		name := fields[2] // mount point (Python: line.split()[2])

		// Python excludes:
		//   re.match(r"/run/user/\d+$", name)
		//   re.match("^/tmp$", name)
		//   re.match("^/run/lock$", name)
		//   re.search("/var/snap", name)
		//   name in systemDisks
		if reRunUser.MatchString(name) {
			continue
		}
		if name == "/tmp" || name == "/run/lock" {
			continue
		}
		if strings.Contains(name, "/var/snap") {
			continue
		}
		if systemDisks[name] {
			continue
		}
		if seen[name] {
			continue
		}
		seen[name] = true
		// Python stores diskDict[name] = "/dev/tmpfs"
		out = append(out, MountInfo{Success: true, MountPoint: name, Device: "/dev/tmpfs"})
	}
	return out, nil
}

func platformUmountPath(path string) error {
	return platformUmountPathWithPassword(path, "")
}

func platformUmountPathWithPassword(path, password string) error {
	umountPath, err := FindBin("umount")
	if err != nil {
		return err
	}
	if password == "" && os.Geteuid() != 0 {
		return &PrivilegeRequiredError{}
	}
	_, stderr, err := runMaybeSudo(password, umountPath, path)
	if err != nil {
		return fmt.Errorf("umount %s failed: %w (%s)", path, err, stderr)
	}
	if strings.Contains(path, "ramdisk-") {
		_ = os.Remove(path)
	}
	return nil
}
