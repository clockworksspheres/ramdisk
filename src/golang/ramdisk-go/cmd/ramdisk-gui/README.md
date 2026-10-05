# ramdisk-gui (Qt 6)

Qt 6 desktop UI for ramdisk-go — port of the Python PySide6 UI.

Uses **[MIQT](https://github.com/mappu/miqt)** v0.14+ (`github.com/mappu/miqt/qt6`).

## Layout

| Control | Role |
|---------|------|
| Size slider + line edit | Ramdisk size in MiB |
| Mount point line edit | Optional path (empty = auto) |
| Create Ramdisk | Create & mount, leave mounted |
| Eject Ramdisk | Unmount selected table row |
| Refresh | Reload mounted list |
| Quit | Exit |
| Table | device \| mount point |

---

## macOS build (Homebrew Qt 6) — current recipe

### Common errors and fixes

| Error | Fix |
|-------|-----|
| `Qt requires a C++17 compiler` | Set `CGO_CXXFLAGS=-std=c++17` |
| `'type_traits' file not found` | Add `-isysroot $SDKROOT` and `-stdlib=libc++` |
| `cd: no such file or directory: cmd/ramdisk-gui` | You are already inside `cmd/ramdisk-gui` — do not `cd` again |
| Wrong constructors (`NewQSlider`, `NewQTableWidget2`, …) | Use the latest `main.go` from this repo (MIQT v0.14 API) |

### 1. Install tools

```bash
xcode-select --install          # Apple clang + SDK
brew install qt pkg-config
```

Confirm the SDK path:

```bash
xcrun --sdk macosx --show-sdk-path
```

If that fails, install full **Xcode** from the App Store, then:

```bash
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
```

### 2. Environment (same terminal session)

```bash
export QT_PREFIX="$(brew --prefix qt)"
export PATH="$QT_PREFIX/bin:$PATH"
export PKG_CONFIG_PATH="$QT_PREFIX/lib/pkgconfig:${PKG_CONFIG_PATH:-}"

export SDKROOT="$(xcrun --sdk macosx --show-sdk-path)"
export CXX="$(xcrun --find clang++)"
export CC="$(xcrun --find clang)"

export CGO_CXXFLAGS="-std=c++17 -stdlib=libc++ -isysroot ${SDKROOT}"
export CGO_CFLAGS="-isysroot ${SDKROOT}"
export CGO_LDFLAGS="-F${QT_PREFIX}/lib -Wl,-rpath,${QT_PREFIX}/lib -isysroot ${SDKROOT}"
```

Sanity check (use a temp file — shells eat `<...>` in one-liners):

```bash
cat > /tmp/t.cpp << 'END'
#include <type_traits>
int main() { return 0; }
END
clang++ -std=c++17 -stdlib=libc++ -isysroot "$SDKROOT" -c /tmp/t.cpp -o /tmp/t.o && echo "OK: type_traits found"

pkg-config --modversion Qt6Core
```

### 3. Build

From the **project root** (the folder that contains `cmd/`):

```bash
cd /actual/path/to/ramdisk-go    # e.g. ~/Downloads/ramdisk-go
ls cmd/ramdisk-gui/main.go       # must exist

go clean -cache                  # after changing CGO_* flags

cd cmd/ramdisk-gui
go get github.com/mappu/miqt/qt6@latest

CGO_ENABLED=1 go build -tags qt -ldflags="-s -w" -o ramdisk-gui .
./ramdisk-gui
```

If your prompt already shows `.../ramdisk-gui`, **skip** `cd cmd/ramdisk-gui` and only run the `go build` line.

First MIQT compile can take **5–15 minutes**; later builds are fast.

### 4. If Go API errors appear

Confirm you have the current `main.go` (MIQT v0.14 names):

```bash
grep -E "NewQSlider2|NewQTableWidget3|QCoreApplication_ProcessEvents|AddActionWithText|ShowMessage2" main.go
```

All of those should match. Re-copy `main.go` from the latest zip if not.

---

## Linux

```bash
sudo apt install qt6-base-dev build-essential pkg-config   # or distro equivalent
export CGO_CXXFLAGS="-std=c++17"
cd /path/to/ramdisk-go/cmd/ramdisk-gui
go get github.com/mappu/miqt/qt6@latest
CGO_ENABLED=1 go build -tags qt -ldflags="-s -w" -o ramdisk-gui .
./ramdisk-gui
# Create/Eject will pop up a PolicyKit (pkexec) admin password dialog.
# Install if missing:  sudo apt install policykit-1
# Headless/no pkexec: run with sudo ./ramdisk-gui
```

---

`github.com/mappu/miqt` is **not** required for the library or `cmd/ramdisk` CLI.
