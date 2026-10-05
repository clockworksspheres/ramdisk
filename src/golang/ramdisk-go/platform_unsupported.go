//go:build !linux && !darwin && !windows

package ramdisk

func platformCreate(opts Options) (platformRamDisk, error) {
	return nil, &UnsupportedPlatformError{}
}

func platformListMounted() ([]MountInfo, error) {
	return nil, &UnsupportedPlatformError{}
}

func platformUmountPath(path string) error {
	return &UnsupportedPlatformError{}
}

// platformUmountPathWithPassword ignores password on non-Linux.
func platformUmountPathWithPassword(path, password string) error { return platformUmountPath(path) }
