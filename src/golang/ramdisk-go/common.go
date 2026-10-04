package ramdisk

import (
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strconv"
	"strings"
	"time"
)

// CheckMemory performs a best-effort free-memory check.
// On Linux it reads /proc/meminfo. On other platforms it is a no-op.
func CheckMemory(sizeMB uint64) error {
	data, err := os.ReadFile("/proc/meminfo")
	if err != nil {
		// Not Linux or unreadable; skip hard check.
		return nil
	}
	for _, line := range strings.Split(string(data), "\n") {
		if strings.HasPrefix(line, "MemAvailable:") {
			fields := strings.Fields(line)
			if len(fields) < 2 {
				break
			}
			kb, err := strconv.ParseUint(fields[1], 10, 64)
			if err != nil {
				break
			}
			freeMB := kb / 1024
			if freeMB < sizeMB {
				return &MemoryNotAvailableError{Requested: sizeMB, Available: freeMB}
			}
			return nil
		}
	}
	return nil
}

// RandomMountPoint creates a unique temporary directory for use as a mount point.
func RandomMountPoint() (string, error) {
	base := os.TempDir()
	unique := fmt.Sprintf("ramdisk-%d-%d", os.Getpid(), time.Now().UnixNano())
	path := filepath.Join(base, unique)
	if err := os.MkdirAll(path, 0755); err != nil {
		return "", err
	}
	return path, nil
}

// FindBin locates an executable on PATH (and common Unix locations).
func FindBin(name string) (string, error) {
	if p, err := exec.LookPath(name); err == nil {
		return p, nil
	}
	// Absolute fallbacks common on Unix
	for _, prefix := range []string{"/bin", "/usr/bin", "/sbin", "/usr/sbin", "/usr/local/bin", "/usr/local/sbin"} {
		candidate := filepath.Join(prefix, name)
		if st, err := os.Stat(candidate); err == nil && !st.IsDir() {
			return candidate, nil
		}
	}
	return "", &ToolNotFoundError{Tool: name}
}

// RunCmd executes a command and returns stdout, stderr, and any error.
func RunCmd(name string, args ...string) (stdout, stderr string, err error) {
	cmd := exec.Command(name, args...)
	var outBuf, errBuf strings.Builder
	cmd.Stdout = &outBuf
	cmd.Stderr = &errBuf
	runErr := cmd.Run()
	stdout = strings.TrimSpace(outBuf.String())
	stderr = strings.TrimSpace(errBuf.String())
	if runErr != nil {
		status := "unknown"
		if exitErr, ok := runErr.(*exec.ExitError); ok {
			status = exitErr.Error()
		} else {
			status = runErr.Error()
		}
		err = &CommandFailedError{
			Cmd:    strings.Join(append([]string{name}, args...), " "),
			Stdout: stdout,
			Stderr: stderr,
			Status: status,
		}
	}
	return stdout, stderr, err
}
