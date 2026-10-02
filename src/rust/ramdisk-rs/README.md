# ramdisk (Rust)

Cross-platform interface for creating and managing ramdisks.

Port of the Python library [clockworksspheres/ramdisk](https://github.com/clockworksspheres/ramdisk) to idiomatic Rust.

## Supported platforms

| OS      | Backend                          | Privileges          | Notes                                      |
|---------|----------------------------------|---------------------|--------------------------------------------|
| Linux   | `tmpfs` / `ramfs` via `mount`    | root (or CAP_SYS_ADMIN) | size limit enforced for tmpfs             |
| macOS   | `hdiutil` + `diskutil` (APFS)    | normal user         | no root required                           |
| Windows | Arsenal Image Mounter (`aim_ll`) | Administrator       | `aim_ll.exe` must be on `PATH`             |

---

## Installing Rust / Cargo and platform dependencies

### Linux

**Rust / Cargo** – official installer (recommended):

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

Or via your distro package manager (versions may lag):

```bash
# Debian / Ubuntu
sudo apt update && sudo apt install -y build-essential curl
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Fedora / RHEL / Rocky
sudo dnf install -y gcc make curl
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Arch
sudo pacman -S --needed base-devel curl
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

**System tools used by the library** (usually already present):

- `mount` / `umount` (from `util-linux`)
- A C toolchain (`gcc` or `clang`) so Cargo can link native code if needed

No extra packages beyond a normal build environment are required for the Linux backend.

---

### macOS (Homebrew)

**1. Install Homebrew** (if you don’t already have it):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**2. Install Rust / Cargo via Homebrew:**

```bash
brew install rust
```

Alternatively you can use the official installer (works fine alongside Homebrew):

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

**3. System tools**

`hdiutil` and `diskutil` ship with macOS – nothing extra to install.

Verify:

```bash
which hdiutil diskutil cargo rustc
cargo --version
```

---

### Windows (Chocolatey)

**1. Install Chocolatey** (run an elevated PowerShell / CMD):

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

**2. Install Rust / Cargo via Chocolatey:**

```powershell
choco install rust -y
# or the more complete toolchain:
choco install rustup.install -y
```

After installation open a **new** terminal so `cargo` and `rustc` are on `PATH`.

**3. Install the Arsenal Image Mounter CLI (`aim_ll`)**

The Windows backend depends on `aim_ll.exe` from the [Arsenal Image Mounter](https://github.com/ArsenalRecon/Arsenal-Image-Mounter) project.

- Download the latest release from the [Arsenal Image Mounter releases](https://github.com/ArsenalRecon/Arsenal-Image-Mounter/releases) page, or
- Place `aim_ll.exe` somewhere that is on your system `PATH` (for example `C:\Tools\aim_ll.exe` and add that folder to PATH).

Verify:

```powershell
cargo --version
aim_ll -h
```

You will also need the **Microsoft C++ Build Tools** (or a full Visual Studio installation) so the Rust MSVC toolchain can link. Chocolatey can install them:

```powershell
choco install visualstudio2022buildtools -y
# or the lighter package
choco install visualstudio2022-workload-vctools -y
```

---

## Quick start

Add the crate to your project:

```toml
[dependencies]
ramdisk = { path = "…" }   # or version from crates.io once published
```

```rust
use ramdisk::{RamDisk, RamDiskOptions};

fn main() -> ramdisk::Result<()> {
    // 512 MiB, temporary mount point
    let rd = RamDisk::with_size(512)?;

    println!("success  = {}", rd.success());
    println!("mount    = {}", rd.mount_point().display());
    println!("device   = {:?}", rd.device());
    println!("version  = {}", rd.version());

    // Use the filesystem at rd.mount_point() …

    rd.umount()?;   // or just drop the handle
    Ok(())
}
```

### Explicit options

```rust
use ramdisk::{RamDisk, RamDiskOptions, LinuxFsType};
use std::path::PathBuf;

let opts = RamDiskOptions {
    size_mb: 1024,
    mount_point: Some(PathBuf::from("/mnt/myram")),
    linux_fstype: LinuxFsType::Tmpfs,
    linux_mode: 0o755,
    ..Default::default()
};
let rd = RamDisk::new(opts)?;
```

## API surface (mirrors the original Python library)

| Python                         | Rust                                      |
|--------------------------------|-------------------------------------------|
| `RamDisk(size, mountpoint)`    | `RamDisk::new(RamDiskOptions{…})`         |
| `ramdisk.getData()`            | `rd.get_data() → MountInfo`               |
| `ramdisk.getMountPoint()`      | `rd.mount_point()`                        |
| `ramdisk.getDevice()`          | `rd.device()`                             |
| `ramdisk.umount()`             | `rd.umount()`                             |
| `getMountedDisks()`            | `ramdisk::list_mounted()`                 |
| `umount(device)`               | `ramdisk::umount_path(path)`              |

## Platform notes

### Linux
- Uses `mount -t tmpfs -o size=…m,uid=…,gid=…,mode=…`.
- Requires root (or the `CAP_SYS_ADMIN` capability). The library returns a clear `PrivilegeRequired` error when the process is not privileged.
- `ramfs` is also supported but has **no size limit** – the process can consume all RAM.

### macOS
- Creates a `ram://` device with `hdiutil attach -nomount`, partitions it as APFS, then mounts at the requested path.
- Runs as a normal user; no sudo needed.

### Windows
- Requires the [Arsenal Image Mounter](https://github.com/ArsenalRecon/Arsenal-Image-Mounter) command-line tool (`aim_ll.exe`) to be installed and on `PATH`.
- The process typically needs Administrator rights.

## Building / testing

```bash
cargo build
cargo test          # unit tests only; integration tests need privileges
```

On Linux you will need to run integration tests as root (or with appropriate capabilities) for the mount to succeed.


## Command-line tool (`ramdisk`)

Build and install the binary:

```bash
cargo build --release
# optional: install into ~/.cargo/bin
cargo install --path .
```

### Commands

```text
ramdisk create [--size <MiB>] [--mount <path>] [--keep]
ramdisk list
ramdisk umount <mount-or-device>
ramdisk info
ramdisk help
```

| Command | Description |
|---------|-------------|
| `create` / `c` | Create and mount a ramdisk |
| `list` / `ls` / `l` | List currently mounted ramdisks |
| `umount` / `unmount` / `u` | Unmount by mount point or device |
| `info` / `i` | Show version and platform backend |
| `help` | Show help |

**Create options**

| Flag | Description | Default |
|------|-------------|---------|
| `--size`, `-s` | Size in MiB | `512` |
| `--mount`, `-m` | Explicit mount path | temp directory |
| `--keep`, `-k` | Stay running until Enter; then unmount | leave mounted |

**Mount lifetime**

- **Default (`create` without `--keep`)** – the ramdisk **stays mounted** after the process exits. Use `ramdisk umount <path>` later to remove it.
- **`--keep`** – the process waits for Enter, then unmounts before exiting.
- From library code, call `rd.detach()` instead of `rd.umount()` / dropping if you want the mount to survive.


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

## License

Unlicense (same as the original Python project).
