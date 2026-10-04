// Command-line tool for the ramdisk library.
//
// Usage:
//
//	ramdisk create [--size <MiB>] [--mount <path>] [--keep]
//	ramdisk list
//	ramdisk umount <mount-or-device>
//	ramdisk info
package main

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"runtime"

	"github.com/clockworksspheres/ramdisk-go"
)

func main() {
	if len(os.Args) < 2 {
		printHelp()
		os.Exit(1)
	}

	switch os.Args[1] {
	case "create", "c":
		cmdCreate(os.Args[2:])
	case "list", "ls", "l":
		cmdList()
	case "umount", "unmount", "u":
		cmdUmount(os.Args[2:])
	case "info", "i":
		cmdInfo()
	case "help", "-h", "--help":
		printHelp()
	default:
		fmt.Fprintf(os.Stderr, "unknown command: %s\n\n", os.Args[1])
		printHelp()
		os.Exit(1)
	}
}

func printHelp() {
	fmt.Print(`ramdisk – cross-platform in-memory disk tool

Commands:
  create, c   Create and mount a ramdisk (exits immediately; mount stays)
  list, ls, l List currently mounted ramdisks
  umount, u   Unmount by mount point or device
  info, i     Show version and platform backend
  help        Show this help

Create options:
  --size, -s <MiB>   Size in mebibytes (default 512)
  --mount, -m <path> Explicit mount path (default: temp directory)
  --keep, -k         Wait for Enter, then unmount and exit

Default behaviour (no --keep):
  The process prints the mount path and exits right away.
  The ramdisk STAYS mounted until you run:  ramdisk umount <path>

Examples:
  sudo ramdisk create --size 1024
  sudo ramdisk create -s 256 -m /mnt/buildcache
  sudo ramdisk create -s 256 --keep
  ramdisk list
  sudo ramdisk umount /mnt/buildcache
`)
}

func cmdCreate(args []string) {
	fs := flag.NewFlagSet("create", flag.ExitOnError)
	size := fs.Uint64("size", 512, "size in MiB")
	fs.Uint64Var(size, "s", 512, "size in MiB (shorthand)")
	mount := fs.String("mount", "", "explicit mount path")
	fs.StringVar(mount, "m", "", "explicit mount path (shorthand)")
	keep := fs.Bool("keep", false, "wait for Enter then unmount")
	fs.BoolVar(keep, "k", false, "wait for Enter then unmount (shorthand)")
	_ = fs.Parse(args)

	opts := ramdisk.Options{
		SizeMB:     *size,
		MountPoint: *mount,
	}

	rd, err := ramdisk.New(opts)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error creating ramdisk: %v\n", err)
		if _, ok := err.(*ramdisk.PrivilegeRequiredError); ok {
			fmt.Fprintln(os.Stderr, "hint: on Linux run with sudo (or CAP_SYS_ADMIN)")
		}
		os.Exit(1)
	}

	mp := rd.MountPoint()
	if abs, err := filepath.Abs(mp); err == nil {
		mp = abs
	}

	fmt.Printf("success   = %v\n", rd.Success())
	fmt.Printf("mount     = %s\n", mp)
	fmt.Printf("device    = %s\n", rd.Device())
	fmt.Printf("version   = %s\n", rd.Version())

	if *keep {
		fmt.Println("\nPress Enter to unmount…")
		_, _ = fmt.Scanln()
		if err := rd.Umount(); err != nil {
			fmt.Fprintf(os.Stderr, "error unmounting: %v\n", err)
			os.Exit(1)
		}
		fmt.Println("unmounted")
		os.Exit(0)
	}

	// Default path: drop the Go handle WITHOUT unmounting, then exit.
	// os.Exit skips deferred functions, so any accidental defer Umount
	// would also be skipped — the OS mount remains.
	_ = rd.Detach()
	fmt.Printf("\nMounted and still active at:\n  %s\n", mp)
	fmt.Printf("Process exiting now. Unmount later with:\n  ramdisk umount %s\n", mp)
	os.Exit(0)
}

func cmdList() {
	list, err := ramdisk.ListMounted()
	if err != nil {
		fmt.Fprintf(os.Stderr, "error listing: %v\n", err)
		os.Exit(1)
	}
	if len(list) == 0 {
		fmt.Println("(no ramdisks found)")
		return
	}
	for i, m := range list {
		fmt.Printf("[%d] mount=%s  device=%s\n", i, m.MountPoint, m.Device)
	}
}

func cmdUmount(args []string) {
	if len(args) < 1 {
		fmt.Fprintln(os.Stderr, "usage: ramdisk umount <mount-or-device>")
		os.Exit(1)
	}
	path := args[0]
	if err := ramdisk.UmountPath(path); err != nil {
		fmt.Fprintf(os.Stderr, "error unmounting %s: %v\n", path, err)
		os.Exit(1)
	}
	fmt.Printf("unmounted %s\n", path)
}

func cmdInfo() {
	fmt.Printf("ramdisk-go (Go port of clockworksspheres/ramdisk)\n")
	fmt.Printf("go version : %s\n", runtime.Version())
	fmt.Printf("os/arch    : %s/%s\n", runtime.GOOS, runtime.GOARCH)

	// Report backend version without creating a lasting mount.
	// On Linux this needs root; if it fails we still print what we can.
	rd, err := ramdisk.WithSize(1)
	if err != nil {
		fmt.Printf("backend    : (unable to probe – %v)\n", err)
		return
	}
	fmt.Printf("backend    : %s\n", rd.Version())
	_ = rd.Umount()
}
