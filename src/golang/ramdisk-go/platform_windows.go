//go:build windows

package ramdisk

import (
	"fmt"
	"os"
	"regexp"
	"strings"
)

const moduleVersion = "20251004.golang.windows"

type windowsRamDisk struct {
	success    bool
	mountPoint string
	device     string // AIM device id, e.g. "1:"
	sizeMB     uint64
	unmounted  bool
	aimLL      string
	fsType     string
}

func platformCreate(opts Options) (platformRamDisk, error) {
	opts = opts.WithDefaults()
	if opts.SizeMB == 0 {
		return nil, &SizeInvalidError{Size: opts.SizeMB}
	}

	aimLL, err := FindBin("aim_ll")
	if err != nil {
		return nil, fmt.Errorf("%w – install Arsenal Image Mounter CLI (aim_ll.exe) and ensure it is on PATH", err)
	}

	mnt := opts.MountPoint
	if mnt == "" {
		mnt, err = RandomMountPoint()
		if err != nil {
			return nil, err
		}
	} else {
		mnt = strings.ReplaceAll(mnt, "/", `\`)
		if err := os.MkdirAll(mnt, 0755); err != nil {
			return nil, err
		}
	}

	rd := &windowsRamDisk{
		mountPoint: mnt,
		sizeMB:     opts.SizeMB,
		aimLL:      aimLL,
		fsType:     opts.WindowsFsType,
	}

	if err := rd.create(); err != nil {
		return nil, err
	}
	rd.success = true
	return rd, nil
}

func (r *windowsRamDisk) create() error {
	params := fmt.Sprintf("/fs:%s /q /y", r.fsType)
	cmd := []string{
		"-a",
		"-s", fmt.Sprintf("%dM", r.sizeMB),
		"-m", r.mountPoint,
		"-p", params,
	}

	stdout, stderr, err := RunCmd(r.aimLL, cmd...)
	if err != nil {
		return err
	}

	re := regexp.MustCompile(`(?i)Created device\s+(\S+)`)
	combined := stdout + "\n" + stderr
	if m := re.FindStringSubmatch(combined); len(m) > 1 {
		r.device = m[1]
	} else {
		r.device = r.mountPoint
	}
	return nil
}

func (r *windowsRamDisk) Success() bool     { return r.success }
func (r *windowsRamDisk) MountPoint() string { return r.mountPoint }
func (r *windowsRamDisk) Device() string     { return r.device }
func (r *windowsRamDisk) Version() string    { return moduleVersion }

func (r *windowsRamDisk) TryUmount() error {
	if r.unmounted {
		return nil
	}
	target := r.device
	if target == "" {
		target = r.mountPoint
	}
	_, _, err := RunCmd(r.aimLL, "-R", "-u", target)
	if err == nil {
		r.unmounted = true
	}
	return err
}

func platformListMounted() ([]MountInfo, error) {
	aimLL, err := FindBin("aim_ll")
	if err != nil {
		return nil, err
	}
	stdout, _, err := RunCmd(aimLL, "-l")
	if err != nil {
		return nil, err
	}
	var out []MountInfo
	for _, line := range strings.Split(stdout, "\n") {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		fields := strings.Fields(line)
		if len(fields) >= 2 {
			out = append(out, MountInfo{
				Success:    true,
				MountPoint: fields[len(fields)-1],
				Device:     fields[0],
			})
		}
	}
	return out, nil
}

func platformUmountPath(path string) error {
	aimLL, err := FindBin("aim_ll")
	if err != nil {
		return err
	}
	_, _, err = RunCmd(aimLL, "-R", "-u", path)
	return err
}
