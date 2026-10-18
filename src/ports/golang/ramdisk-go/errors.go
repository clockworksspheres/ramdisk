package ramdisk

import (
	"fmt"
)

// Error types mirroring the original Python / Rust ports.

type SizeInvalidError struct {
	Size uint64
}

func (e *SizeInvalidError) Error() string {
	return fmt.Sprintf("invalid ramdisk size: %d (must be > 0)", e.Size)
}

type MemoryNotAvailableError struct {
	Requested uint64
	Available uint64
}

func (e *MemoryNotAvailableError) Error() string {
	return fmt.Sprintf("not enough free physical memory for a %d MiB ramdisk (only %d MiB free)",
		e.Requested, e.Available)
}

type UnsupportedPlatformError struct{}

func (e *UnsupportedPlatformError) Error() string {
	return "this platform is not supported for ramdisk creation"
}

type ToolNotFoundError struct {
	Tool string
}

func (e *ToolNotFoundError) Error() string {
	return fmt.Sprintf("required system tool not found: %s", e.Tool)
}

type PrivilegeRequiredError struct{}

func (e *PrivilegeRequiredError) Error() string {
	return "must be root (or provide credentials) to create/manage this ramdisk"
}

type CommandFailedError struct {
	Cmd    string
	Stdout string
	Stderr string
	Status string
}

func (e *CommandFailedError) Error() string {
	return fmt.Sprintf("command failed: %s\nstdout: %s\nstderr: %s\nstatus: %s",
		e.Cmd, e.Stdout, e.Stderr, e.Status)
}

type PathError struct {
	Msg string
}

func (e *PathError) Error() string {
	return e.Msg
}
