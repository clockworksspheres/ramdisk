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
| **aim_ll** | Arsenal Image Mounter CLI must be on Windows `PATH` or next to the `.exe` |

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

Confirm:

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

run:

```bash
export GOROOT=/ucrt64/lib/go
export PATH="/ucrt64/bin:$PATH"

go env GOROOT
go version
```

To make it permanent, add those two `export` lines to `~/.bashrc` in the UCRT64 environment.

Prefer `/ucrt64/bin/go` over a Chocolatey or go.dev Go on the Windows PATH when building inside UCRT64.

### 5. Build the GUI (inside UCRT64)

```bash
export CGO_ENABLED=1
export GOROOT=/ucrt64/lib/go
export PATH="/ucrt64/bin:$PATH"

# Windows path example: C:\Users\you\ramdisk-go → /c/Users/you/ramdisk-go
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

### 6. Running the .exe (outside UCRT64 is fine)

**UCRT64 is only for building.** The binary is a normal Windows program.

If you double-click or run from Admin PowerShell and the process **exits immediately**, it is almost always **missing DLLs** (Qt and/or MinGW runtime) or the Qt platform plugin.

#### 6a. Deploy DLLs next to the exe (recommended)

In **UCRT64**, from the folder that contains `ramdisk-gui.exe`:

```bash
OUT=/c/Users/you/path/to/ramdisk-go/cmd/ramdisk-gui   # adjust
cd "$OUT"

cp /ucrt64/bin/Qt6Core.dll \
   /ucrt64/bin/Qt6Gui.dll \
   /ucrt64/bin/Qt6Widgets.dll \
   /ucrt64/bin/libgcc_s_seh-1.dll \
   /ucrt64/bin/libstdc++-6.dll \
   /ucrt64/bin/libwinpthread-1.dll \
   . 2>/dev/null

# Other Qt/MinGW deps may be required; copy additional lib*.dll from /ucrt64/bin if needed

mkdir -p platforms
cp /ucrt64/share/qt6/plugins/platforms/qwindows.dll platforms/
```

Also place **`aim_ll.exe`** (Arsenal Image Mounter CLI) in the same folder, or ensure it is on the **Windows** system/user `PATH`.

Then from **PowerShell** or Explorer:

```powershell
cd C:\Users\you\path\to\ramdisk-go\cmd\ramdisk-gui
.\ramdisk-gui.exe
echo "Exit code: $LASTEXITCODE"
```

#### 6b. Or put UCRT64 on PATH for one session

```powershell
$env:PATH = "C:\msys64\ucrt64\bin;" + $env:PATH
# Chocolatey may use e.g. C:\tools\msys64\ucrt64\bin
$env:QT_PLUGIN_PATH = "C:\msys64\ucrt64\share\qt6\plugins"
.\ramdisk-gui.exe
```

You still need `platforms\qwindows.dll` next to the exe **or** a correct `QT_PLUGIN_PATH`.

#### 6c. aim_ll not found inside UCRT64

MSYS2’s `PATH` is separate from Windows’. `aim_ll` installed for Windows is often invisible inside UCRT64.

- **Preferred:** run `ramdisk-gui.exe` from normal PowerShell/CMD after step 6a, with `aim_ll.exe` on the Windows PATH or beside the exe.
- **Or** in UCRT64 for one session:

```bash
export PATH="/c/Program Files/Arsenal Image Mounter:$PATH"
# adjust to the real directory that contains aim_ll.exe
./ramdisk-gui.exe
```

Install Arsenal Image Mounter from: https://arsenalrecon.com/downloads

#### 6d. Debug an immediate exit

1. Rebuild **without** `-H windowsgui` so a console stays open.
2. Run from PowerShell and read any panic or DLL message.
3. Check for a Windows dialog: “Qt6Core.dll / libstdc++-6.dll / qwindows.dll was not found”.

```powershell
.\ramdisk-gui.exe
echo "Exit code: $LASTEXITCODE"
```

### 7. Optional: cross-build with miqt-docker

From Linux or macOS (no local Windows Qt toolchain):

```bash
go install github.com/mappu/miqt/cmd/miqt-docker@latest
cd /path/to/ramdisk-go/cmd/ramdisk-gui
miqt-docker win64-qt6-static -windows-build --tags=qt,windowsqtstatic
```

See: https://github.com/mappu/miqt/blob/master/cmd/miqt-docker/README.md

### Windows checklist

- [ ] MSYS2 installed; using **UCRT64** shell for build
- [ ] `pacman` packages: go, gcc, pkg-config, qt6-base
- [ ] `GOROOT=/ucrt64/lib/go` if Go complains about trimmed binary
- [ ] `CGO_ENABLED=1` and `pkg-config --modversion Qt6Widgets` works
- [ ] Build with `-tags qt`
- [ ] Deploy Qt + MinGW DLLs and `platforms\qwindows.dll` next to the exe
- [ ] `aim_ll.exe` on Windows PATH or next to the exe
- [ ] Run elevated if create/eject need administrator rights

---

`github.com/mappu/miqt` is **not** required for the library or `cmd/ramdisk` CLI.
