//go:build darwin

package ramdisk

import (
	"fmt"
	"os"
	"os/user"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"
)

const moduleVersion = "20251004.golang.darwin"

type darwinRamDisk struct {
	success    bool
	mountPoint string
	device     string // whole disk, e.g. /dev/disk4
	volumeDev  string // volume/slice, e.g. /dev/disk4s1
	sizeMB     uint64
	unmounted  bool
	hdiutil    string
	diskutil   string
	volName    string
}

func platformCreate(opts Options) (platformRamDisk, error) {
	opts = opts.WithDefaults()
	if opts.SizeMB == 0 {
		return nil, &SizeInvalidError{Size: opts.SizeMB}
	}

	hdiutil, err := FindBin("hdiutil")
	if err != nil {
		return nil, err
	}
	diskutil, err := FindBin("diskutil")
	if err != nil {
		return nil, err
	}

	mnt := opts.MountPoint
	customMount := mnt != ""
	if customMount {
		if err := os.MkdirAll(mnt, 0755); err != nil {
			return nil, err
		}
	}

	volName := fmt.Sprintf("RAMDisk-%d-%d", os.Getpid(), time.Now().UnixNano()%100000)

	rd := &darwinRamDisk{
		mountPoint: mnt,
		sizeMB:     opts.SizeMB,
		hdiutil:    hdiutil,
		diskutil:   diskutil,
		volName:    volName,
	}

	if err := rd.createAndMount(customMount); err != nil {
		return nil, err
	}
	rd.success = true
	return rd, nil
}

func (r *darwinRamDisk) createAndMount(customMount bool) error {
	sectors := r.sizeMB * 2048

	stdout, stderr, err := RunCmd(r.hdiutil, "attach", "-nomount",
		fmt.Sprintf("ram://%d", sectors))
	if err != nil {
		return fmt.Errorf("hdiutil attach failed: %w (stderr: %s)", err, stderr)
	}
	dev := firstDevLine(stdout)
	if dev == "" {
		return &PathError{Msg: "hdiutil attach returned no device path; output: " + stdout}
	}
	r.device = dev

	_, stderr, err = RunCmd(r.diskutil, "erasevolume", "HFS+", r.volName, r.device)
	if err != nil {
		_, stderr2, err2 := RunCmd(r.diskutil, "apfs", "create", r.device, r.volName)
		if err2 != nil {
			_, _, _ = RunCmd(r.hdiutil, "detach", r.device)
			return fmt.Errorf("format failed (HFS+: %v; APFS: %v; stderr: %s / %s)",
				err, err2, stderr, stderr2)
		}
	}

	volPath := filepath.Join("/Volumes", r.volName)
	for i := 0; i < 30; i++ {
		if st, e := os.Stat(volPath); e == nil && st.IsDir() {
			break
		}
		time.Sleep(100 * time.Millisecond)
	}

	r.volumeDev = r.findVolumeDevice()
	if r.volumeDev == "" {
		r.volumeDev = r.device
	}

	if !customMount {
		r.mountPoint = volPath
		return nil
	}

	_, _, _ = RunCmd(r.diskutil, "unmount", volPath)

	_, stderr, err = RunCmd(r.diskutil, "mount", "-mountPoint", r.mountPoint, r.volumeDev)
	if err != nil {
		if _, e := FindBin("mount_hfs"); e == nil {
			_, stderr, err = RunCmd("mount_hfs", r.volumeDev, r.mountPoint)
		}
		if err != nil {
			if _, e := FindBin("mount_apfs"); e == nil {
				_, stderr, err = RunCmd("mount_apfs", r.volumeDev, r.mountPoint)
			}
		}
		if err != nil {
			r.mountPoint = volPath
			_, _, _ = RunCmd(r.diskutil, "mount", r.volumeDev)
			return nil
		}
	}

	if u, err := user.Current(); err == nil {
		uid, _ := strconv.Atoi(u.Uid)
		gid, _ := strconv.Atoi(u.Gid)
		_ = os.Chown(r.mountPoint, uid, gid)
	}

	return nil
}

func firstDevLine(s string) string {
	re := regexp.MustCompile(`/dev/disk\d+`)
	return re.FindString(s)
}

func (r *darwinRamDisk) findVolumeDevice() string {
	stdout, _, err := RunCmd(r.diskutil, "list")
	if err != nil {
		return r.device + "s1"
	}
	re := regexp.MustCompile(`(disk\d+s\d+)`)
	for _, line := range strings.Split(stdout, "\n") {
		if !strings.Contains(line, r.volName) {
			continue
		}
		fields := strings.Fields(line)
		if len(fields) == 0 {
			continue
		}
		id := fields[len(fields)-1]
		if strings.HasPrefix(id, "disk") {
			return "/dev/" + id
		}
		if m := re.FindStringSubmatch(line); len(m) > 1 {
			return "/dev/" + m[1]
		}
	}
	return r.device + "s1"
}

func (r *darwinRamDisk) Success() bool     { return r.success }
func (r *darwinRamDisk) MountPoint() string { return r.mountPoint }
func (r *darwinRamDisk) Device() string {
	if r.volumeDev != "" {
		return r.volumeDev
	}
	return r.device
}
func (r *darwinRamDisk) Version() string { return moduleVersion }

func (r *darwinRamDisk) TryUmount() error {
	if r.unmounted {
		return nil
	}
	target := r.device
	if target == "" {
		target = r.volumeDev
	}
	if target == "" {
		target = r.mountPoint
	}
	_, _, err := RunCmd(r.hdiutil, "detach", target)
	if err != nil {
		_, _, err = RunCmd(r.hdiutil, "detach", "-force", target)
	}
	if err != nil && r.mountPoint != "" {
		_, _, err = RunCmd(r.diskutil, "unmount", "force", r.mountPoint)
	}
	if err == nil {
		r.unmounted = true
		if strings.Contains(r.mountPoint, "ramdisk-") {
			_ = os.Remove(r.mountPoint)
		}
	}
	return err
}

// platformListMounted discovers mounted ram disks on macOS.
//
// Primary signal: hdiutil info entries whose image-path is ram://…
// For each such whole-disk device we resolve the mount point via
// diskutil info / the mount table. Only entries with a non-empty
// mount path are returned.
func platformListMounted() ([]MountInfo, error) {
	byMount := map[string]MountInfo{}

	hdiutil, err := FindBin("hdiutil")
	diskutil, _ := FindBin("diskutil")

	// --- 1. hdiutil info: find ram:// attachments ---
	if err == nil {
		stdout, _, e := RunCmd(hdiutil, "info")
		if e == nil {
			for _, block := range parseHdiutilInfo(stdout) {
				if !block.isRAM {
					continue
				}
				mp, volDev := resolveMount(diskutil, block.device)
				if mp == "" {
					continue
				}
				dev := volDev
				if dev == "" {
					dev = block.device
				}
				byMount[mp] = MountInfo{Success: true, MountPoint: mp, Device: dev}
			}
		}
	}

	// --- 2. diskutil list: "(disk image)" nodes that are actually mounted ---
	if diskutil != "" {
		stdout, _, e := RunCmd(diskutil, "list")
		if e == nil {
			for _, whole := range diskImageDevices(stdout) {
				mp, volDev := resolveMount(diskutil, whole)
				if mp == "" {
					continue
				}
				// Only keep if it looks like a RAM attachment or we already
				// know it from hdiutil; otherwise skip ordinary .dmg mounts.
				if _, already := byMount[mp]; already {
					continue
				}
				if isRamDevice(hdiutil, whole) {
					dev := volDev
					if dev == "" {
						dev = whole
					}
					byMount[mp] = MountInfo{Success: true, MountPoint: mp, Device: dev}
				}
			}
		}
	}

	// --- 3. mount table fallback for paths we created (/Volumes/RAMDisk-*) ---
	if stdout, _, e := RunCmd("mount"); e == nil {
		for _, line := range strings.Split(stdout, "\n") {
			fields := strings.Fields(line)
			if len(fields) < 3 || !strings.HasPrefix(fields[0], "/dev/disk") {
				continue
			}
			dev := fields[0]
			mp := ""
			for i := 1; i < len(fields)-1; i++ {
				if fields[i] == "on" {
					mp = fields[i+1]
					break
				}
			}
			if mp == "" {
				continue
			}
			if _, exists := byMount[mp]; exists {
				// fill device if missing
				if byMount[mp].Device == "" {
					m := byMount[mp]
					m.Device = dev
					byMount[mp] = m
				}
				continue
			}
			// Accept /Volumes/RAMDisk-* even if hdiutil parsing missed them
			base := filepath.Base(mp)
			if strings.HasPrefix(base, "RAMDisk") {
				byMount[mp] = MountInfo{Success: true, MountPoint: mp, Device: dev}
			}
		}
	}

	out := make([]MountInfo, 0, len(byMount))
	for _, m := range byMount {
		if m.MountPoint == "" {
			continue
		}
		out = append(out, m)
	}
	return out, nil
}

type hdiBlock struct {
	device string // /dev/diskN
	isRAM  bool
}

// parseHdiutilInfo walks `hdiutil info` text and returns one block per
// attached image, noting whether image-path is ram://…
func parseHdiutilInfo(stdout string) []hdiBlock {
	var blocks []hdiBlock
	var cur hdiBlock
	var have bool

	flush := func() {
		if have && cur.device != "" {
			blocks = append(blocks, cur)
		}
		cur = hdiBlock{}
		have = false
	}

	devRe := regexp.MustCompile(`^(/dev/disk\d+)\s*$`)
	// image-path line examples:
	//   image-path      : ram://1048576
	//   image-path      : /tmp/foo.dmg
	for _, line := range strings.Split(stdout, "\n") {
		trim := strings.TrimSpace(line)
		if strings.HasPrefix(trim, "====") {
			flush()
			have = true
			continue
		}
		if strings.Contains(trim, "image-path") && strings.Contains(trim, "ram://") {
			cur.isRAM = true
			have = true
		}
		if m := devRe.FindStringSubmatch(trim); len(m) > 1 {
			// First /dev/diskN in a block is the whole disk
			if cur.device == "" {
				cur.device = m[1]
				have = true
			}
		}
	}
	flush()
	return blocks
}

func diskImageDevices(diskutilList string) []string {
	re := regexp.MustCompile(`/dev/(disk\d+)\s+\(disk image\)`)
	var out []string
	for _, line := range strings.Split(diskutilList, "\n") {
		if m := re.FindStringSubmatch(line); len(m) > 1 {
			out = append(out, "/dev/"+m[1])
		}
	}
	return out
}

func isRamDevice(hdiutil, wholeDisk string) bool {
	if hdiutil == "" {
		return false
	}
	stdout, _, err := RunCmd(hdiutil, "info")
	if err != nil {
		return false
	}
	// Cheap check: within the same section as wholeDisk, is image-path ram://?
	// Fall back to scanning the whole output for ram:// near the device.
	lines := strings.Split(stdout, "\n")
	for i, line := range lines {
		if !strings.Contains(line, wholeDisk) {
			continue
		}
		// Look backwards/forwards a bit for image-path
		lo := i - 15
		if lo < 0 {
			lo = 0
		}
		hi := i + 15
		if hi > len(lines) {
			hi = len(lines)
		}
		section := strings.Join(lines[lo:hi], "\n")
		if strings.Contains(section, "ram://") {
			return true
		}
	}
	return strings.Contains(stdout, "ram://") && strings.Contains(stdout, wholeDisk)
}

// resolveMount returns (mountPoint, volumeDevice) for a whole-disk node.
func resolveMount(diskutil, wholeDisk string) (string, string) {
	if diskutil == "" || wholeDisk == "" {
		return mountTableLookup(wholeDisk)
	}

	// diskutil info on the whole disk often has "Mount Point: not mounted"
	// while the slice is mounted – so also try s1, s2.
	candidates := []string{wholeDisk, wholeDisk + "s1", wholeDisk + "s2"}
	for _, c := range candidates {
		info, _, err := RunCmd(diskutil, "info", c)
		if err != nil {
			continue
		}
		mp := extractField(info, "Mount Point:")
		if mp == "" || strings.EqualFold(mp, "not mounted") || mp == "/" {
			continue
		}
		dev := extractField(info, "Device Node:")
		if dev == "" {
			dev = c
		}
		return mp, dev
	}

	return mountTableLookup(wholeDisk)
}

func extractField(info, key string) string {
	for _, line := range strings.Split(info, "\n") {
		trim := strings.TrimSpace(line)
		if !strings.HasPrefix(trim, key) {
			continue
		}
		// "Mount Point:               /Volumes/Foo"
		val := strings.TrimSpace(strings.TrimPrefix(trim, key))
		return val
	}
	return ""
}

func mountTableLookup(wholeDisk string) (string, string) {
	stdout, _, err := RunCmd("mount")
	if err != nil {
		return "", ""
	}
	// Match /dev/diskN or /dev/diskNsM
	prefix := wholeDisk
	for _, line := range strings.Split(stdout, "\n") {
		fields := strings.Fields(line)
		if len(fields) < 3 {
			continue
		}
		dev := fields[0]
		if dev != prefix && !strings.HasPrefix(dev, prefix+"s") {
			continue
		}
		mp := ""
		for i := 1; i < len(fields)-1; i++ {
			if fields[i] == "on" {
				mp = fields[i+1]
				break
			}
		}
		if mp != "" {
			return mp, dev
		}
	}
	return "", ""
}

func platformUmountPath(path string) error {
	hdiutil, err := FindBin("hdiutil")
	if err != nil {
		return err
	}

	detachTarget := path
	if diskutil, e := FindBin("diskutil"); e == nil {
		infoOut, _, e2 := RunCmd(diskutil, "info", path)
		if e2 == nil {
			if dev := extractField(infoOut, "Device Node:"); dev != "" {
				whole := regexp.MustCompile(`(/dev/disk\d+)`).FindString(dev)
				if whole != "" {
					detachTarget = whole
				} else {
					detachTarget = dev
				}
			}
		}
	}

	_, _, err = RunCmd(hdiutil, "detach", detachTarget)
	if err != nil {
		_, _, err = RunCmd(hdiutil, "detach", "-force", detachTarget)
	}
	if err != nil {
		if diskutil, e2 := FindBin("diskutil"); e2 == nil {
			_, _, err = RunCmd(diskutil, "unmount", "force", path)
		}
	}
	return err
}

// platformUmountPathWithPassword ignores password on non-Linux.
func platformUmountPathWithPassword(path, password string) error { return platformUmountPath(path) }
