
# Fixing Build Setup Problems on Windows

# Error not able to find Qt installer -

The error means the exact filename `qt-online-installer-windows-x64-online.exe` does **not** exist in your Downloads folder.

Please run this command to see the real name of the installer:

```powershell
dir *qt*.exe
```

or more specifically:

```powershell
Get-ChildItem *qt* | Select-Object Name, Length, LastWriteTime
```

Copy and paste the output here (especially the exact `.exe` name).

Once we see the real filename, we can run the correct command, for example:

```powershell
.\actual-filename-here.exe -platform windows:dpiawareness=0
```

Go ahead and run the `dir` / `Get-ChildItem` command and share what it shows.

---

# CMAKE can't find your installation:

**CMake cannot find your Qt6 installation.**  
Even though Qt is in `C:\Qt`, the build script doesn’t know which kit (MSVC / MinGW version + exact Qt version) to use.

### 1. Find the exact path of your Qt kit

Run these commands in PowerShell:

```powershell
dir C:\Qt
```

Then look inside the version folders, e.g.:

```powershell
dir C:\Qt\6.*
```

You should see something like:

```
C:\Qt\6.8.0\msvc2022_64
C:\Qt\6.8.0\mingw_64
...
```

The important folder is the one that contains `lib\cmake\Qt6\Qt6Config.cmake`.  
Typical full path:

```
C:\Qt\6.8.0\msvc2022_64
```

(or `msvc2019_64`, `mingw_64`, etc.)

### 2. Tell CMake where Qt is

You have three easy options. Choose one.

#### Option A – One-time fix when running your build script (recommended for now)

Edit your `build.ps1` (or the CMake call inside it) and add the path.  
Look for the `cmake` line and change it to something like this:

```powershell
cmake -B build -S . `
  -DCMAKE_PREFIX_PATH="C:/Qt/6.8.0/msvc2022_64" `
  -DRAMDISK_BUILD_GUI=ON `
  ...
```

(Replace `6.8.0\msvc2022_64` with the real folder you found.)

Then delete the old build folder and re-run:

```powershell
Remove-Item -Recurse -Force build
.\build.ps1
```

#### Option B – Set it for the current PowerShell session

```powershell
$env:CMAKE_PREFIX_PATH = "C:\Qt\6.8.0\msvc2022_64"
.\build.ps1
```

#### Option C – Use Qt’s own helper (cleanest long-term)

```powershell
& "C:\Qt\6.8.0\msvc2022_64\bin\qt-cmake.bat" -B build -S . -DRAMDISK_BUILD_GUI=ON
```

(Again, adjust the version/kit path.)

### 3. Quick verification

After setting the path, you can test with:

```powershell
cmake -DCMAKE_PREFIX_PATH="C:/Qt/6.8.0/msvc2022_64" -P - <<EOF
find_package(Qt6 REQUIRED COMPONENTS Widgets)
message(STATUS "Qt6 found: ${Qt6_DIR}")
EOF
```

### Next step

Please run:

```powershell
dir C:\Qt
dir C:\Qt\6.*
```

and paste the output (especially the kit folders).  
I’ll give you the exact command to put into your `build.ps1`.

---

# Make sure you have the right path:

**Two problems are happening at once:**

1. You pointed CMake at the **MinGW** Qt kit (`C:/Qt/6.12.0/mingw_64`).
2. CMake is generating a **Visual Studio / MSVC** project (see “Building for: Visual Studio 18 2026” and the `cl.exe` compiler).

You cannot mix a MinGW-built Qt with the MSVC compiler. That is why you get the C++17 / `__cplusplus` error.

### Correct fix (recommended)

Use the **MSVC** version of Qt that matches your Visual Studio.

1. Check which MSVC kits you actually have:

```powershell
dir C:\Qt\6.12.0
```

Look for something like:

- `msvc2022_64`
- `msvc2019_64`
- `msvc2022_arm64` (unlikely)

2. Re-configure with the MSVC kit (example assuming `msvc2022_64`):

```powershell
# Clean the previous build
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue

# Configure with the correct Qt kit
cmake -B build -S . `
  -DCMAKE_PREFIX_PATH="C:/Qt/6.12.0/msvc2022_64" `
  -DRAMDISK_BUILD_GUI=ON
```

3. Then build again:

```powershell
.\build.ps1
```

(or just `cmake --build build --config Release`)

### If you really want to keep the MinGW Qt

You must also switch the generator to MinGW:

```powershell
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue

cmake -B build -S . `
  -G "MinGW Makefiles" `
  -DCMAKE_PREFIX_PATH="C:/Qt/6.12.0/mingw_64" `
  -DRAMDISK_BUILD_GUI=ON `
  -DCMAKE_CXX_COMPILER="C:/Qt/Tools/mingw1310_64/bin/g++.exe"   # adjust path if needed
```

Most people on Windows prefer the MSVC route, so the first option is usually better.

---

**Quick check** – paste the output of:

```powershell
dir C:\Qt\6.12.0
```

I’ll give you the exact one-liner to use.

---

# It's building now, but won't launch when I execute ramdisk_gui.exe

**Most common reason a Qt GUI app builds but won’t start on Windows:**  
missing Qt DLLs + the `platforms\qwindows.dll` plugin.

### Quick diagnosis

1. Open a **new PowerShell** window and go to the folder that contains `ramdisk_gui.exe` (usually `build\Release`):

```powershell
cd C:\Users\royni\Documents\src\github\clockworksspheres\ramdisk\src\cpp\ramdisk-cpp\build\Release
```

2. Run it and capture the error:

```powershell
.\ramdisk_gui.exe
```

or with more debug info:

```powershell
$env:QT_DEBUG_PLUGINS = "1"
.\ramdisk_gui.exe
```

You will almost certainly see something like:

- “This application failed to start because no Qt platform plugin could be initialized”
- or a missing `Qt6Core.dll` / `Qt6Gui.dll` / `Qt6Widgets.dll`

### Fix – run `windeployqt` (the official way)

Assuming you used the **MSVC** kit (e.g. `msvc2022_64`):

```powershell
# Adjust the path if your kit is different
& "C:\Qt\6.12.0\msvc2022_64\bin\windeployqt.exe" --release .\ramdisk_gui.exe
```

If you are still on the MinGW kit:

```powershell
& "C:\Qt\6.12.0\mingw_64\bin\windeployqt.exe" --release .\ramdisk_gui.exe
```

`windeployqt` will copy all required Qt DLLs and create the `platforms` folder next to the `.exe`.

After it finishes, try launching again:

```powershell
.\ramdisk_gui.exe
```

### Temporary workaround (for development only)

Add the Qt `bin` directory to your PATH for the current session:

```powershell
$env:PATH = "C:\Qt\6.12.0\msvc2022_64\bin;" + $env:PATH
.\ramdisk_gui.exe
```

(This works while developing but is not a proper deployment.)

---

Please run the `.\ramdisk_gui.exe` command (or the `QT_DEBUG_PLUGINS=1` version) and paste the exact error message you get. That will confirm whether it’s the platform plugin or something else.

