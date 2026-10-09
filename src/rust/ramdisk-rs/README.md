# ramdisk (Rust)

Cross-platform ramdisk library + CLI + optional CXX-Qt GUI.

## Workspace layout

| Crate | Role |
|-------|------|
| `ramdisk` | Library + `ramdisk` CLI |
| `ramdisk-gui` | QML GUI (separate binary so cxx-qt links correctly) |

## Build CLI

```bash
cargo build -p ramdisk
cargo run -p ramdisk -- list
```

## Build GUI (needs Qt 6)

### Debian 13

```bash
sudo apt install -y build-essential cmake pkg-config \
  qt6-base-dev qt6-declarative-dev qt6-tools-dev \
  qml6-module-qtquick qml6-module-qtquick-controls \
  qml6-module-qtquick-layouts qml6-module-qtqml \
  qml6-module-qtquick-window

export QMAKE=$(command -v qmake6)
cargo run -p ramdisk-gui
```

### macOS

```bash
brew install qt
export QMAKE="$(brew --prefix qt)/bin/qmake"
cargo run -p ramdisk-gui
```

## Note on linking

The GUI is a **separate package** so the CXX-Qt bridge and generated C++ are linked
in the same binary (avoids undefined `cxxbridge` symbols when the bridge lived only in the library).
