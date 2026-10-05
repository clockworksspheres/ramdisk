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

On **Linux**, Create and Eject each open a **Local Authentication** dialog
(same layout/algorithm as Python `local_auth.ui`) and elevate via `sudo -S`.

On **macOS**, no password dialog is needed for typical use.

On **Windows**, there is no password dialog; run elevated if create/eject
require admin rights. Backend uses **Arsenal Image Mounter** (`aim_ll.exe`).

---

## macOS build (Homebrew Qt 6)

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

## Linux build

```bash
sudo apt install qt6-base-dev build-essential pkg-config   # or distro equivalent
# Local auth uses sudo -S (same idea as Python local_auth)
# PolicyKit is not required for the password dialog path

export CGO_CXXFLAGS="-std=c++17"
cd /path/to/ramdisk-go/cmd/ramdisk-gui

# If proxy.golang.org fails (DNS):
#   export GOPROXY=direct
#   # or: export GOPROXY=https://goproxy.io,direct

go get github.com/mappu/miqt/qt6@latest
CGO_ENABLED=1 go build -tags qt -ldflags="-s -w" -o ramdisk-gui .
./ramdisk-gui
# Create/Eject → Local Authentication dialog → enter password
```

---

## Windows build

MIQT on Windows requires **CGO with MinGW or Clang**. **MSVC does not work** with CGO.
If you build from plain PowerShell with only MSVC/Visual Studio, you get errors like:

```text
undefined: MouseButton
undefined: WindowType
gen_qnamespace_64bit.go: ...
```

Those mean the MinGW/Qt toolchain is missing or not on `PATH`.

### Overview

| Step | Where |
|------|--------|
| **Build** | MSYS2 **UCRT64** shell (MinGW + Qt 6 + CGO) |
| **Run** | Normal Windows (Explorer, CMD, PowerShell) — **not** required to use UCRT64 |
| **aim_ll** | Arsenal Image Mounter CLI on Windows `PATH` **or** next to the `.exe` |
| **Elevation** | **Run as administrator** for Create/Eject (AIM driver access) |

### 1. Install MSYS2

**Chocolatey** (elevated PowerShell):

```powershell
choco install msys2 -y
# optional:
# choco install msys2 -y --params "/InstallDir:C:\msys64 /NoUpdate"
```

**Or** official installer: https://www.msys2.org/

Default location is often `C:\msys64` or under Chocolatey’s tools path (e.g. `C:\tools\msys64`).

**pacman** is included with MSYS2. You do not install pacman separately. Use it only inside an MSYS2 shell (not in PowerShell).

### 2. Open MSYS2 UCRT64

Start menu → **MSYS2 UCRT64**  
(not “MSYS2 MSYS” — UCRT64 is required for this build)

```bash
which pacman
pacman --version
```

### 3. Install Go, GCC, pkg-config, Qt 6 (inside UCRT64)

```bash
pacman -Syu
# close and reopen UCRT64 if it asks, then:
pacman -S mingw-w64-ucrt-x86_64-go \
          mingw-w64-ucrt-x86_64-gcc \
          mingw-w64-ucrt-x86_64-pkg-config \
          mingw-w64-ucrt-x86_64-qt6-base
```

### 4. Fix GOROOT (common after installing MSYS2 Go)

If you see:

```text
go: cannot find GOROOT directory: 'go' binary is trimmed and GOROOT is not set
```

```bash
export GOROOT=/ucrt64/lib/go
export PATH="/ucrt64/bin:$PATH"

go env GOROOT
go version
```

Add those exports to `~/.bashrc` in UCRT64 to make them permanent. Prefer `/ucrt64/bin/go` over a Chocolatey or go.dev Go when building inside UCRT64.

### 5. Build the GUI (inside UCRT64)

```bash
export CGO_ENABLED=1
export GOROOT=/ucrt64/lib/go
export PATH="/ucrt64/bin:$PATH"

# Example: C:\Users\you\...\ramdisk-go → /c/Users/you/.../ramdisk-go
cd /c/Users/you/path/to/ramdisk-go/cmd/ramdisk-gui

go get github.com/mappu/miqt/qt6@latest

# Debug build (console) — shows errors if the app exits immediately:
go build -tags qt -ldflags="-s -w" -o ramdisk-gui.exe .

# Release-style (no console window):
# go build -tags qt -ldflags="-s -w -H windowsgui" -o ramdisk-gui.exe .
```

Sanity checks:

```bash
go env CGO_ENABLED GOOS GOARCH CC
which gcc pkg-config
pkg-config --modversion Qt6Widgets
```

### 6. Deploy DLLs (required when running outside UCRT64)

A MinGW/Qt **dynamic** build does not work as a lone `.exe`. If DLLs are missing you get:

| Symptom | Meaning |
|---------|---------|
| Exit code **`0xC0000135`** or **`-1073741515`** | `STATUS_DLL_NOT_FOUND` — a required DLL was not found |
| Process starts and exits immediately, no window | Same (missing Qt/MinGW DLL or platform plugin) |

#### 6a. Copy DLLs next to the exe (UCRT64)

```bash
cd /c/Users/you/path/to/ramdisk-go/cmd/ramdisk-gui

cp /ucrt64/bin/Qt6Core.dll \
   /ucrt64/bin/Qt6Gui.dll \
   /ucrt64/bin/Qt6Widgets.dll \
   /ucrt64/bin/libgcc_s_seh-1.dll \
   /ucrt64/bin/libstdc++-6.dll \
   /ucrt64/bin/libwinpthread-1.dll \
   .

# Broader set of Qt/MinGW deps (safe to copy extras)
cp /ucrt64/bin/Qt6*.dll /ucrt64/bin/lib*.dll . 2>/dev/null

# Qt platform plugin — required or Qt exits at startup
mkdir -p platforms
cp /ucrt64/share/qt6/plugins/platforms/qwindows.dll platforms/
```

Also place **`aim_ll.exe`** in the same folder (or on the Windows `PATH`).  
`FindBin` looks for `aim_ll` / `aim_ll.exe` on `PATH`, next to the running executable, and in the current working directory.

Expected layout:

```text
ramdisk-gui.exe
aim_ll.exe
Qt6Core.dll
Qt6Gui.dll
Qt6Widgets.dll
libgcc_s_seh-1.dll
libstdc++-6.dll
libwinpthread-1.dll
… (other Qt/MinGW DLLs as needed)
platforms\
  qwindows.dll
```

#### 6b. Find still-missing DLLs

```bash
ldd ramdisk-gui.exe
ldd ramdisk-gui.exe | grep -i "not found"
```

Copy any “not found” files from `/ucrt64/bin` into the exe folder.

#### 6c. Temporary PATH test (PowerShell)

If this starts the GUI, the problem was only DLL search path:

```powershell
cd C:\Users\you\path\to\ramdisk-go\cmd\ramdisk-gui
$env:PATH = "C:\msys64\ucrt64\bin;" + $env:PATH
# Chocolatey may use e.g. C:\tools\msys64\ucrt64\bin
$env:QT_PLUGIN_PATH = "C:\msys64\ucrt64\share\qt6\plugins"
.\ramdisk-gui.exe
echo $LASTEXITCODE
```

### 7. Run as Administrator (Create / Eject)

After DLLs load, Create may still fail with:

```text
Error controlling the Arsenal Image Mounter driver: Access is denied.
```

and a non-zero exit from `aim_ll` (often **exit code 6**).

The AIM **driver** requires elevation. The Windows GUI does **not** show a password dialog (unlike Linux Local Auth). You must:

1. Close the GUI.
2. Right-click **PowerShell** / **Terminal** → **Run as administrator**, then:

```powershell
cd C:\Users\you\path\to\ramdisk-go\cmd\ramdisk-gui
.\ramdisk-gui.exe
```

Or right-click `ramdisk-gui.exe` → **Run as administrator**.

Confirm the driver works elevated:

```powershell
.\aim_ll.exe -l
```

Install the full **Arsenal Image Mounter** package (driver + CLI): https://arsenalrecon.com/downloads

### 8. List / table (`aim_ll -l`)

Listing matches Python `getMountDisks()` / Rust parsing of `aim_ll -l`:

- Blocks starting with `Device number …`
- In-memory markers (`memory` / `ram` / `Virtual Memory`)
- `Mounted at …` for the mount path
- Blank line ends a record

After Create, the table is updated from the create result and from Refresh/`ListMounted`.

### 9. Optional: cross-build with miqt-docker

From Linux or macOS:

```bash
go install github.com/mappu/miqt/cmd/miqt-docker@latest
cd /path/to/ramdisk-go/cmd/ramdisk-gui
miqt-docker win64-qt6-static -windows-build --tags=qt,windowsqtstatic
```

See: https://github.com/mappu/miqt/blob/master/cmd/miqt-docker/README.md

### Windows checklist

- [ ] MSYS2 installed; build in **UCRT64**
- [ ] pacman packages: go, gcc, pkg-config, qt6-base
- [ ] `GOROOT=/ucrt64/lib/go` if Go reports a trimmed binary
- [ ] `CGO_ENABLED=1` and `pkg-config --modversion Qt6Widgets` works
- [ ] Build with `-tags qt`
- [ ] Qt + MinGW DLLs and `platforms\qwindows.dll` next to the exe
- [ ] No `0xC0000135` / `-1073741515` on launch
- [ ] `aim_ll.exe` on PATH or next to the exe
- [ ] **Run as administrator** for Create/Eject (avoids AIM “Access is denied”)
- [ ] Arsenal Image Mounter **driver** installed, not only the CLI


---

`github.com/mappu/miqt` is **not** required for the library or `cmd/ramdisk` CLI.
