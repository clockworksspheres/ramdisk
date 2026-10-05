# ramdisk-go

Cross-platform interface for creating and managing ramdisks.

Port of the Python library [clockworksspheres/ramdisk](https://github.com/clockworksspheres/ramdisk) to idiomatic Go.

## Supported platforms

| OS      | Backend                          | Privileges              | Notes                                      |
|---------|----------------------------------|-------------------------|--------------------------------------------|
| Linux   | tmpfs / ramfs via `mount`        | root (or CAP_SYS_ADMIN) | size limit enforced for tmpfs              |
| macOS   | hdiutil + diskutil (APFS)        | normal user             | no root required                           |
| Windows | Arsenal Image Mounter (`aim_ll`) | Administrator           | `aim_ll.exe` must be on PATH               |

## Prerequisites

You need a working Go toolchain (**Go 1.21 or later**).

### Install Go

| Platform | Recommended method |
|----------|--------------------|
| **Linux** | [Official installer](https://go.dev/dl/) or distro packages (`apt install golang-go`, `dnf install golang`, …) |
| **macOS** | `brew install go` or the [official installer](https://go.dev/dl/) |
| **Windows** | [Official installer](https://go.dev/dl/) or `choco install golang` |

Verify:

```bash
go version   # should report go1.21 or newer
```

### Platform-specific tools

| OS | Extra tools required |
|----|----------------------|
| **Linux** | `mount` / `umount` (from util-linux – almost always present). Root or `CAP_SYS_ADMIN` to create mounts. |
| **macOS** | `hdiutil` and `diskutil` (ship with macOS – nothing extra). |
| **Windows** | [Arsenal Image Mounter CLI](https://github.com/ArsenalRecon/Arsenal-Image-Mounter) (`aim_ll.exe`) on `PATH`. Administrator rights typically required. Also need the Microsoft C++ Build Tools if you compile from source on Windows. |

---

## Building

### 1. Get the source

```bash
# From the zip / clone
cd ramdisk-go
```

Or, once published:

```bash
go get github.com/clockworksspheres/ramdisk-go
```

### 2. Build the library

```bash
go build ./...
```

This compiles the library and all platform backends (build tags select the correct one for your OS). No CGO is required.

### 3. Build / install the CLI

```bash
# Produce a binary in the current directory
go build -o ramdisk ./cmd/ramdisk

# Or install into $(go env GOPATH)/bin (usually ~/go/bin)
go install ./cmd/ramdisk
```

Make sure `$(go env GOPATH)/bin` is on your `PATH` if you used `go install`.

### 4. Cross-compile (optional)

```bash
# Linux binary from any host
GOOS=linux   GOARCH=amd64 go build -o ramdisk-linux   ./cmd/ramdisk

# macOS binary
GOOS=darwin  GOARCH=amd64 go build -o ramdisk-darwin  ./cmd/ramdisk
GOOS=darwin  GOARCH=arm64 go build -o ramdisk-darwin-arm64 ./cmd/ramdisk

# Windows binary
GOOS=windows GOARCH=amd64 go build -o ramdisk.exe     ./cmd/ramdisk
```

### 5. Run tests

```bash
go test ./...          # unit tests only
# Integration tests that create real mounts need privileges:
#   Linux:  sudo go test ./...
#   macOS:  normal user is fine
#   Windows: run from an elevated shell
```

### Quick verification

```bash
./ramdisk info          # shows Go version, OS/arch, backend version
./ramdisk create -s 64 --keep   # create a 64 MiB ramdisk, wait for Enter, then unmount
```

On Linux you will normally need `sudo` for `create` / `umount`.

---

## Quick start (library)

```go
package main

import (
    "fmt"
    "log"

    "github.com/clockworksspheres/ramdisk-go"
)

func main() {
    // 512 MiB, temporary mount point
    rd, err := ramdisk.WithSize(512)
    if err != nil {
        log.Fatal(err)
    }
    defer rd.Umount()

    fmt.Println("success  =", rd.Success())
    fmt.Println("mount    =", rd.MountPoint())
    fmt.Println("device   =", rd.Device())
    fmt.Println("version  =", rd.Version())

    // Use the filesystem at rd.MountPoint() …
}
```

### Explicit options

```go
opts := ramdisk.Options{
    SizeMB:      1024,
    MountPoint:  "/mnt/myram",
    LinuxFsType: ramdisk.LinuxTmpfs,
    LinuxMode:   0755,
}
rd, err := ramdisk.New(opts)
```

## API surface (mirrors the original Python library)

| Python                        | Go                                      |
|-------------------------------|-----------------------------------------|
| `RamDisk(size, mountpoint)`   | `ramdisk.New(Options{…})`               |
| `ramdisk.getData()`           | `rd.GetData() → MountInfo`              |
| `ramdisk.getMountPoint()`     | `rd.MountPoint()`                       |
| `ramdisk.getDevice()`         | `rd.Device()`                           |
| `ramdisk.umount()`            | `rd.Umount()`                           |
| `getMountedDisks()`           | `ramdisk.ListMounted()`                 |
| `umount(device)`              | `ramdisk.UmountPath(path)`              |

## Platform notes

### Linux

* Uses `mount -t tmpfs -o size=…m,uid=…,gid=…,mode=…`.
* Requires root (or the `CAP_SYS_ADMIN` capability).
* `ramfs` is also supported but has **no size limit** – the process can consume all RAM.

### macOS

* Creates a `ram://` device with `hdiutil attach -nomount`, formats with `diskutil erasevolume` (HFS+, APFS fallback).
* Default mount is under `/Volumes/RAMDisk-<id>` (survives process exit).
* Optional `--mount` remounts at a custom path.
* Runs as a normal user; no sudo needed.
* Unmount with `ramdisk umount <path>` or `hdiutil detach <device>`.

### Windows

* Requires the [Arsenal Image Mounter](https://github.com/ArsenalRecon/Arsenal-Image-Mounter) command-line tool (`aim_ll.exe`) to be installed and on `PATH`.
* The process typically needs Administrator rights.

## Command-line tool (`ramdisk`)

```bash
go install ./cmd/ramdisk
# or
go build -o ramdisk ./cmd/ramdisk
```

### Commands

```
ramdisk create [--size <MiB>] [--mount <path>] [--keep]
ramdisk list
ramdisk umount <mount-or-device>
ramdisk info
ramdisk help
```

| Command              | Description                              |
|----------------------|------------------------------------------|
| `create` / `c`       | Create and mount a ramdisk               |
| `list` / `ls` / `l`  | List currently mounted ramdisks          |
| `umount` / `u`       | Unmount by mount point or device         |
| `info` / `i`         | Show version and platform backend        |
| `help`               | Show help                                |

**Create options**

| Flag            | Description                     | Default        |
|-----------------|---------------------------------|----------------|
| `--size`, `-s`  | Size in MiB                     | 512            |
| `--mount`, `-m` | Explicit mount path             | temp directory |
| `--keep`, `-k`  | Stay running until Enter; then unmount | leave mounted |

**Mount lifetime**

* **Default** (`create` without `--keep`) – the ramdisk **stays mounted** after the process exits. Use `ramdisk umount <path>` later to remove it.
* **`--keep`** – the process waits for Enter, then unmounts before exiting.

**Examples**

```bash
# 1 GiB ramdisk at a temp path, leave it mounted
ramdisk create --size 1024

# 256 MiB at a fixed path, wait for Enter then unmount
ramdisk create -s 256 -m /mnt/buildcache --keep

# List known ramdisks
ramdisk list

# Unmount later
ramdisk umount /mnt/buildcache
```

On Linux, `create` and `umount` generally require root (or `CAP_SYS_ADMIN`).




## Desktop GUI (Qt 6)

A Qt 6 desktop UI lives in `cmd/ramdisk-gui`, mirroring the Python PySide6 app.

It uses **[MIQT](https://github.com/mappu/miqt)** (`github.com/mappu/miqt/qt6`).

### Features

* Size slider + numeric field (MiB)
* Optional mount-point field
* **Create** / **Eject** / **Refresh** / **Quit**
* Table of mounted ramdisks
* Dark palette in evening hours

### Build (macOS)

Full details: **`cmd/ramdisk-gui/README.md`**.

```bash
xcode-select --install
brew install qt pkg-config

export QT_PREFIX="$(brew --prefix qt)"
export PATH="$QT_PREFIX/bin:$PATH"
export PKG_CONFIG_PATH="$QT_PREFIX/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
export SDKROOT="$(xcrun --sdk macosx --show-sdk-path)"
export CXX="$(xcrun --find clang++)"
export CC="$(xcrun --find clang)"
export CGO_CXXFLAGS="-std=c++17 -stdlib=libc++ -isysroot ${SDKROOT}"
export CGO_CFLAGS="-isysroot ${SDKROOT}"
export CGO_LDFLAGS="-F${QT_PREFIX}/lib -Wl,-rpath,${QT_PREFIX}/lib -isysroot ${SDKROOT}"

cd /path/to/ramdisk-go          # folder that contains cmd/
go clean -cache
cd cmd/ramdisk-gui
go get github.com/mappu/miqt/qt6@latest
CGO_ENABLED=1 go build -tags qt -ldflags="-s -w" -o ramdisk-gui .
./ramdisk-gui
```

If you are already inside `cmd/ramdisk-gui`, do **not** run `cd cmd/ramdisk-gui` again.

### Build (Linux)

```bash
sudo apt install qt6-base-dev build-essential pkg-config
export CGO_CXXFLAGS="-std=c++17"
cd cmd/ramdisk-gui
go get github.com/mappu/miqt/qt6@latest
CGO_ENABLED=1 go build -tags qt -ldflags="-s -w" -o ramdisk-gui .
sudo ./ramdisk-gui
```

The CLI does not depend on Qt:

```bash
go build -o ramdisk ./cmd/ramdisk
```

## License

Unlicense (same as the original Python project).
