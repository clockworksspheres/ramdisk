//go:build windows

package ramdisk

import (
	"fmt"
	"os"
	"regexp"
	"strings"
)

const moduleVersion = "20251005.golang.windows"

type windowsRamDisk struct {
	success    bool
	mountPoint string
	device     string // AIM device number, e.g. "000001" or "1:"
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
		return nil, fmt.Errorf("%w – install Arsenal Image Mounter CLI (aim_ll.exe), put it on PATH, or place aim_ll.exe next to this program", err)
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
	// Collapse repeated backslashes (Python cleanPath)
	mnt = regexp.MustCompile(`\\{2,}`).ReplaceAllString(mnt, `\`)

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
	// Match Python:
	//   aim_ll -a -s {size}M -m "{path}" -p "/fs:{fs} /q /y"
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

	// Python:
	//   if re.match("Created device", line) and re.search("memory", last field):
	//       device = line.split()[2]
	r.device = parseCreatedDevice(stdout + "\n" + stderr)
	if r.device == "" {
		r.device = r.mountPoint
	}
	return nil
}

// parseCreatedDevice extracts the device id from aim_ll create output.
// Example lines:
//
//	Created device 000001 -> memory
//	Created device 1: Size is 536870912 bytes in memory
func parseCreatedDevice(output string) string {
	reCreated := regexp.MustCompile(`(?i)^Created device\s+(\S+)`)
	for _, line := range strings.Split(output, "\n") {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		m := reCreated.FindStringSubmatch(line)
		if m == nil {
			continue
		}
		// Prefer lines that mention memory (Python filter); still accept others.
		lower := strings.ToLower(line)
		if strings.Contains(lower, "memory") || strings.Contains(lower, "ram") {
			return strings.TrimRight(m[1], ",")
		}
		if dev := strings.TrimRight(m[1], ","); dev != "" {
			return dev
		}
	}
	// Fallback: first "Created device X" without memory filter
	for _, line := range strings.Split(output, "\n") {
		line = strings.TrimSpace(line)
		if m := reCreated.FindStringSubmatch(line); m != nil {
			return strings.TrimRight(m[1], ",")
		}
	}
	return ""
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
	if err != nil {
		return err
	}
	r.unmounted = true
	// Python also runs: mountvol <mountName> /D for path mount points
	_ = detachMountPoint(r.mountPoint)
	return nil
}

func detachMountPoint(mount string) error {
	// Drive letters like "R:" or "R:\" — mountvol /D is mainly for folder mount points
	m := strings.TrimSpace(mount)
	if m == "" || len(m) <= 3 {
		return nil
	}
	_, _, err := RunCmd("mountvol", m, "/D")
	return err
}

// platformListMounted runs `aim_ll -l` and parses blocks the same way as
// Python getMountDisks() / Rust parse_mounted_devices():
//
//	Device number 000001
//	  ...
//	  Image file: Virtual Memory  (or similar "memory"/"ram" marker)
//	  Mounted at R:\
//	<blank line ends the record>
func platformListMounted() ([]MountInfo, error) {
	aimLL, err := FindBin("aim_ll")
	if err != nil {
		return nil, err
	}
	stdout, stderr, err := RunCmd(aimLL, "-l")
	if err != nil {
		return nil, fmt.Errorf("aim_ll -l failed: %w (%s)", err, stderr)
	}
	return parseAimList(stdout), nil
}

func parseAimList(output string) []MountInfo {
	var out []MountInfo
	var device string
	var mountPoint string
	isRamdisk := false

	finish := func() {
		if isRamdisk && device != "" {
			mp := strings.TrimRight(mountPoint, `\/`)
			out = append(out, MountInfo{
				Success:    true,
				MountPoint: mp,
				Device:     device,
			})
		}
		device = ""
		mountPoint = ""
		isRamdisk = false
	}

	for _, raw := range strings.Split(output, "\n") {
		line := strings.TrimSpace(raw)
		// Python skips lines with many backslashes (noise)
		if strings.Count(line, `\`) >= 4 && !strings.Contains(strings.ToLower(line), "mounted") {
			continue
		}

		if strings.HasPrefix(line, "Device number ") {
			finish()
			id := strings.TrimSpace(strings.TrimPrefix(line, "Device number "))
			// first token only
			if fields := strings.Fields(id); len(fields) > 0 {
				device = fields[0]
			}
			continue
		}

		lower := strings.ToLower(line)
		// Mark as in-memory / ramdisk (Python + Rust)
		if strings.Contains(lower, "virtual memory") ||
			strings.Contains(lower, "memory") ||
			(strings.Contains(lower, "ram") && !strings.Contains(lower, "program")) {
			isRamdisk = true
		}

		if strings.HasPrefix(line, "Mounted at ") {
			mountPoint = strings.TrimSpace(strings.TrimPrefix(line, "Mounted at "))
			continue
		}
		// Alternate phrasing some builds use
		if idx := strings.Index(lower, "mounted at "); idx >= 0 {
			mountPoint = strings.TrimSpace(line[idx+len("mounted at "):])
			continue
		}

		// Blank line ends a device block (Python)
		if line == "" {
			finish()
		}
	}
	finish()
	return out
}

func platformUmountPath(path string) error {
	aimLL, err := FindBin("aim_ll")
	if err != nil {
		return err
	}

	// Resolve path → device id via list when needed
	device := path
	mountForCleanup := path
	if !isAimDeviceID(path) {
		list := parseAimList(mustAimList(aimLL))
		found := false
		want := normalizeWinPath(path)
		for _, m := range list {
			if normalizeWinPath(m.MountPoint) == want || normalizeWinPath(m.Device) == want {
				device = m.Device
				if m.MountPoint != "" {
					mountForCleanup = m.MountPoint
				}
				found = true
				break
			}
		}
		if !found {
			// Try using path directly with -u (drive letter etc.)
			device = path
		}
	}

	_, stderr, err := RunCmd(aimLL, "-R", "-u", device)
	if err != nil {
		return fmt.Errorf("aim_ll -R -u %s failed: %w (%s)", device, err, stderr)
	}
	_ = detachMountPoint(mountForCleanup)
	return nil
}

func mustAimList(aimLL string) string {
	stdout, _, _ := RunCmd(aimLL, "-l")
	return stdout
}

func isAimDeviceID(s string) bool {
	s = strings.TrimSpace(s)
	if s == "" {
		return false
	}
	// Six hex digits (AIM unit) or trailing colon form "1:"
	if len(s) == 6 {
		for _, c := range s {
			if !((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F')) {
				return false
			}
		}
		return true
	}
	if strings.HasSuffix(s, ":") && len(s) <= 4 {
		return true
	}
	return false
}

func normalizeWinPath(p string) string {
	p = strings.ReplaceAll(p, "/", `\`)
	p = strings.TrimRight(p, `\`)
	return strings.ToLower(p)
}

// platformUmountPathWithPassword ignores password on non-Linux.
func platformUmountPathWithPassword(path, password string) error {
	return platformUmountPath(path)
}
