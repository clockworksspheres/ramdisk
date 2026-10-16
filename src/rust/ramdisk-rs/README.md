# ramdisk (Rust)

Cross-platform library, CLI, and optional Qt/QML GUI for creating and managing
in-memory disks (ramdisks).

Ported from [clockworksspheres/ramdisk](https://github.com/clockworksspheres/ramdisk).

| Platform | Backend |
|----------|---------|
| **Linux** | `tmpfs` / `ramfs` via `mount` (sudo when not root) |
| **macOS** | `hdiutil` + APFS (detach/eject on umount) |
| **Windows** | Arsenal Image Mounter (AIM) toolkit |

## Workspace layout

```text
ramdisk-rs/                 workspace root
├── ramdisk/                library + `ramdisk` CLI
└── ramdisk-gui/            CXX-Qt / QML GUI binary
```

| Crate | Role |
|-------|------|
| `ramdisk` | Library + CLI (`cargo run -p ramdisk -- …`) |
| `ramdisk-gui` | GUI (`cargo run -p ramdisk-gui`) — separate package so CXX-Qt links correctly |

## Install Rust (Cargo)

### macOS (Homebrew)

```bash
brew install rust
# or: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### Windows (Chocolatey)

```powershell
choco install rust
# or use https://rustup.rs
```

### Linux (Debian / Ubuntu)

```bash
sudo apt install -y cargo rustc
# For a newer toolchain: https://rustup.rs
# GUI needs rustc ≥ 1.85; pin cxx to 1.0.186 (see Cargo.toml).
```

## CLI

```bash
cargo build -p ramdisk
cargo run -p ramdisk -- help

# Create 512 MiB ramdisk (stays mounted after exit)
cargo run -p ramdisk -- create --size 512 --mount /tmp/ram0

# List / unmount
cargo run -p ramdisk -- list
cargo run -p ramdisk -- umount /tmp/ram0
```

On **Linux**, create/umount as a non-root user may require sudo (password prompt or run as root).

On **macOS**, `umount` fully **ejects** the disk (`diskutil unmountDisk` + `hdiutil detach -force`).

## Library example

```rust
use ramdisk::{RamDisk, RamDiskOptions};

fn main() -> ramdisk::Result<()> {
    let rd = RamDisk::new(RamDiskOptions {
        size_mb: 512,
        mount_point: None, // temporary path
        ..Default::default()
    })?;

    println!("mounted at {}", rd.mount_point().display());

    // Keep the mount after the process exits:
    let info = rd.detach();
    println!("left mounted at {}", info.mount_point.display());

    // Or unmount before exit:
    // rd.umount()?;
    Ok(())
}
```

`detach()` leaves the OS mount active. `umount()` / `Drop` unmounts (and on macOS, ejects).

## Graphical UI (CXX-Qt + QML)

Requires **Qt 6** and a working `qmake` / `qmake6`.

### Debian 13 (trixie)

```bash
sudo apt update
sudo apt install -y \
  build-essential cmake pkg-config \
  qt6-base-dev qt6-declarative-dev qt6-tools-dev \
  qml6-module-qtquick qml6-module-qtquick-controls \
  qml6-module-qtquick-layouts qml6-module-qtqml \
  qml6-module-qtquick-window

export QMAKE=$(command -v qmake6)
cargo run -p ramdisk-gui
```

If you see `cxxbridge1$NNN$…` undefined references, pin the cxx ABI:

```bash
cargo update -p cxx --precise 1.0.186
cargo update -p cxx-gen --precise 0.7.186
# or: ./fix-cxx-abi.sh
```

### macOS (Homebrew)

```bash
brew install rust qt
export QMAKE="$(brew --prefix qt)/bin/qmake"
# or: export QMAKE=$(command -v qmake6)

cargo run -p ramdisk-gui
```

macOS links against **libc++** (not libstdc++).

### Windows

```powershell
# Install Qt 6 (e.g. via aqtinstall or the Qt online installer)
# Ensure qmake is on PATH, then:
$env:QMAKE = "C:\path\to\qmake.exe"
cargo run -p ramdisk-gui
```

### GUI behaviour

- **Create** / **Eject** on Linux as non-root opens a **Local Authentication** dialog (sudo password), matching the Python `local_auth_widget`.
- Table lists mounted ramdisks (including under `/tmp` on Linux).
- Default selection for eject is the **first** row.
- After create, the mount remains active (same as CLI `detach`).

## Repo files

| Path | Keep? |
|------|--------|
| `Cargo.lock` | **Yes** for this workspace (reproducible binary builds). |
| `.cargo/config.toml` | Optional. Forces the BFD linker on Linux; **safe to delete on macOS/Windows**. |

## Features / versions

- Rust **1.85+**
- GUI: `cxx` **1.0.186**, `cxx-qt` / `cxx-qt-lib` / `cxx-qt-build` **0.7.3** (pinned for ABI stability)

## License

Unlicense (public domain), consistent with the original project intent.
