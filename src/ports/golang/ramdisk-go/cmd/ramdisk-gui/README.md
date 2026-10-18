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

These are the full steps to build and run `ramdisk-gui.exe` on Windows.

**Requirements**

- Windows 10/11 x64
- **MSYS2 UCRT64** (MinGW + Qt 6). MSVC cannot build this GUI (CGO is incompatible).
- **Arsenal Image Mounter** driver + `aim_ll.exe` for create/eject
- Administrator rights when creating or ejecting ramdisks

**What runs where**

- **Build** only inside the MSYS2 **UCRT64** shell.
- **Run** from normal Windows (Explorer, CMD, or PowerShell). You do not need UCRT64 to run the finished `.exe`.
- UCRT64 is a separate environment: its `PATH` is not the same as Windows PowerShell.

---

### Step 1 — Install MSYS2

**Option A — Chocolatey** (elevated PowerShell):

```powershell
choco install msys2 -y
```

Optional install directory:

```powershell
choco install msys2 -y --params "/InstallDir:C:\msys64 /NoUpdate"
```

**Option B — Official installer**

1. Download from https://www.msys2.org/
2. Run the installer (default path `C:\msys64` is fine).

**Note:** `pacman` is the package manager **inside** MSYS2. It is not a separate Windows install. Do not expect `pacman` to work in PowerShell or CMD.

---

### Step 2 — Open the UCRT64 shell

1. Open the Start menu.
2. Launch **MSYS2 UCRT64** (not “MSYS2 MSYS” and not “MSYS2 MINGW64”).
3. Confirm:

```bash
which pacman
pacman --version
uname -a
```

You should see a UCRT64 / mingw environment, not a plain MSYS path-only shell.

---

### Step 3 — Install build packages (inside UCRT64)

Update the system first (you may need to close and reopen UCRT64 if `pacman` says so):

```bash
pacman -Syu
```

Install Go, the C/C++ toolchain, pkg-config, and Qt 6:

```bash
pacman -S mingw-w64-ucrt-x86_64-go \
          mingw-w64-ucrt-x86_64-gcc \
          mingw-w64-ucrt-x86_64-pkg-config \
          mingw-w64-ucrt-x86_64-qt6-base
```

Confirm:

```bash
which go
which gcc
which pkg-config
pkg-config --modversion Qt6Widgets
pkg-config --modversion Qt6Core
```

---

### Step 4 — Set Go environment (inside UCRT64)

If `go` prints:

```text
go: cannot find GOROOT directory: 'go' binary is trimmed and GOROOT is not set
```

run:

```bash
export GOROOT=/ucrt64/lib/go
export PATH="/ucrt64/bin:$PATH"
export CGO_ENABLED=1
```

Verify:

```bash
go env GOROOT
go env CGO_ENABLED
go version
```

To make this permanent for UCRT64 sessions, append the same `export` lines to `~/.bashrc`, then `source ~/.bashrc`.

Use MSYS2’s Go under `/ucrt64/bin/go` for this build. A separate Go from go.dev or Chocolatey on the Windows PATH can conflict.

---

### Step 5 — Build ramdisk-gui (inside UCRT64)

Change to the GUI source directory. Windows paths map as `/c/...` in MSYS2:

```bash
# Example path — replace with your real location
cd /c/Users/amrobot/Documents/src/github/clockworksspheres/ramdisk/src/golang/ramdisk-go/cmd/ramdisk-gui

ls main.go
```

Fetch MIQT and build:

```bash
export CGO_ENABLED=1
export GOROOT=/ucrt64/lib/go
export PATH="/ucrt64/bin:$PATH"

go get github.com/mappu/miqt/qt6@latest

# Console build (recommended while debugging — errors stay visible):
go build -tags qt -ldflags="-s -w" -o ramdisk-gui.exe .

# Optional: no console window (use after the app runs cleanly):
# go build -tags qt -ldflags="-s -w -H windowsgui" -o ramdisk-gui.exe .
```

The first MIQT compile can take a long time (often 10–30+ minutes on Windows). Later builds are faster.

If you still see `undefined: MouseButton` / `WindowType` / `gen_qnamespace_64bit.go`, CGO is not using MinGW/Qt. Re-check Step 3–4 (`which gcc`, `pkg-config --modversion Qt6Widgets`, `CGO_ENABLED=1`).

---

### Step 6 — Deploy DLLs next to the executable

A dynamic MinGW + Qt build is **not** a single self-contained `.exe`. If required DLLs are missing, Windows exits immediately with:

| Code | Meaning |
|------|---------|
| `0xC0000135` | `STATUS_DLL_NOT_FOUND` |
| `-1073741515` | Same value as a signed 32-bit exit code in PowerShell |

From **UCRT64**, in the folder that contains `ramdisk-gui.exe`:

```bash
cd /c/Users/amrobot/Documents/src/github/clockworksspheres/ramdisk/src/golang/ramdisk-go/cmd/ramdisk-gui

# Qt libraries
cp /ucrt64/bin/Qt6Core.dll .
cp /ucrt64/bin/Qt6Gui.dll .
cp /ucrt64/bin/Qt6Widgets.dll .
cp /ucrt64/bin/Qt6*.dll . 2>/dev/null

# MinGW runtime
cp /ucrt64/bin/libgcc_s_seh-1.dll .
cp /ucrt64/bin/libstdc++-6.dll .
cp /ucrt64/bin/libwinpthread-1.dll .

# Other common dependencies (copy all matching libs; extras are harmless)
cp /ucrt64/bin/lib*.dll . 2>/dev/null

# Qt platform plugin (required — without this the app often exits at startup)
mkdir -p platforms
cp /ucrt64/share/qt6/plugins/platforms/qwindows.dll platforms/
```

List anything still unresolved:

```bash
ldd ramdisk-gui.exe
ldd ramdisk-gui.exe | grep -i "not found"
```

Copy every DLL reported as **not found** from `/ucrt64/bin` into the same folder as `ramdisk-gui.exe`.

**Target layout**

```text
cmd\ramdisk-gui\
  ramdisk-gui.exe
  aim_ll.exe                 (see Step 7)
  Qt6Core.dll
  Qt6Gui.dll
  Qt6Widgets.dll
  libgcc_s_seh-1.dll
  libstdc++-6.dll
  libwinpthread-1.dll
  (other Qt/MinGW DLLs as needed)
  platforms\
    qwindows.dll
```

---

### Step 7 — Install Arsenal Image Mounter and place aim_ll.exe

1. Install **Arsenal Image Mounter** (driver + tools) from  
   https://arsenalrecon.com/downloads  
   The CLI alone is not enough; the **driver** must be installed.

2. Put `aim_ll.exe` where the program can find it. Search order used by the library:

   1. Windows `PATH` (`aim_ll` and `aim_ll.exe`)
   2. Directory of the running executable (e.g. next to `ramdisk-gui.exe`)
   3. Current working directory

   Recommended: copy `aim_ll.exe` into the same folder as `ramdisk-gui.exe`.

3. Confirm from **elevated** PowerShell:

```powershell
cd C:\Users\amrobot\Documents\src\github\clockworksspheres\ramdisk\src\golang\ramdisk-go\cmd\ramdisk-gui
.\aim_ll.exe -l
```

---

### Step 8 — PATH test (optional, for DLL debugging)

If the app still exits with `0xC0000135` / `-1073741515`, try loading UCRT64 binaries from PowerShell without copying every DLL:

```powershell
cd C:\Users\amrobot\Documents\src\github\clockworksspheres\ramdisk\src\golang\ramdisk-go\cmd\ramdisk-gui

# Adjust if MSYS2 is not under C:\msys64 (e.g. C:\tools\msys64)
$env:PATH = "C:\msys64\ucrt64\bin;" + $env:PATH
$env:QT_PLUGIN_PATH = "C:\msys64\ucrt64\share\qt6\plugins"

.\ramdisk-gui.exe
echo $LASTEXITCODE
```

- If this **works**, the binary is fine and you only need to finish the DLL deploy in Step 6.
- If this **still fails**, run `ldd` again in UCRT64 and fix remaining missing libraries.

You still need `platforms\qwindows.dll` next to the exe **or** a correct `QT_PLUGIN_PATH`.

---

### Step 9 — Run the GUI (and elevate for Create/Eject)

UCRT64 is **not** required to run the finished program. Use Explorer, CMD, or PowerShell.

**Launch as Administrator** when you need Create or Eject. Without elevation you typically get:

```text
Error controlling the Arsenal Image Mounter driver: Access is denied.
```

and `aim_ll` often exits with **code 6**.

The Windows GUI does **not** show a password dialog (Linux does). Elevation is a Windows process property.

**Run elevated**

1. Close any non-elevated instance of the GUI.
2. Right-click **PowerShell** or **Windows Terminal** → **Run as administrator**.
3. Then:

```powershell
cd C:\Users\amrobot\Documents\src\github\clockworksspheres\ramdisk\src\golang\ramdisk-go\cmd\ramdisk-gui
.\ramdisk-gui.exe
echo $LASTEXITCODE
```

Or right-click `ramdisk-gui.exe` → **Run as administrator**.

Success path: window opens → set size → **Create Ramdisk** → row appears in the table → select row → **Eject**.

---

### Step 10 — How the table is filled (`aim_ll -l`)

After create, the GUI adds the new device/mount to the table and can refresh via `aim_ll -l`. Parsing follows the Python Windows logic:

1. Read `aim_ll -l` output.
2. Start a record on lines beginning with `Device number …` (device id is the following token).
3. Treat the device as an in-memory ramdisk if the block mentions `memory`, `ram`, or `Virtual Memory`.
4. Read the mount path from `Mounted at …`.
5. A blank line ends the current record.

Only in-memory AIM devices are listed so normal fixed disks are not shown.

---

### Step 11 — Optional cross-build with miqt-docker

From Linux or macOS (Docker required), without a local Windows Qt toolchain:

```bash
go install github.com/mappu/miqt/cmd/miqt-docker@latest
cd /path/to/ramdisk-go/cmd/ramdisk-gui
miqt-docker win64-qt6-static -windows-build --tags=qt,windowsqtstatic
```

Documentation: https://github.com/mappu/miqt/blob/master/cmd/miqt-docker/README.md

Static builds reduce runtime DLL copying but still need `aim_ll.exe` and elevation for AIM.

---

### Windows checklist

- [ ] MSYS2 installed
- [ ] Building in **MSYS2 UCRT64** (not MSYS, not plain PowerShell with MSVC)
- [ ] Packages installed: `mingw-w64-ucrt-x86_64-go`, `-gcc`, `-pkg-config`, `-qt6-base`
- [ ] `export GOROOT=/ucrt64/lib/go` and `PATH="/ucrt64/bin:$PATH"` if Go reports a trimmed binary
- [ ] `CGO_ENABLED=1` and `pkg-config --modversion Qt6Widgets` succeeds
- [ ] `go build -tags qt ... -o ramdisk-gui.exe .` completes
- [ ] Qt6*.dll, MinGW runtime DLLs, and `platforms\qwindows.dll` sit next to the exe
- [ ] `ldd ramdisk-gui.exe` shows no “not found” entries (or PATH test in Step 8 works)
- [ ] Launch does **not** exit with `0xC0000135` / `-1073741515`
- [ ] `aim_ll.exe` is on PATH or next to `ramdisk-gui.exe`
- [ ] Arsenal Image Mounter **driver** is installed
- [ ] GUI is started **as administrator** for Create/Eject
- [ ] `.\aim_ll.exe -l` works in an elevated prompt


---

`github.com/mappu/miqt` is **not** required for the library or `cmd/ramdisk` CLI.
