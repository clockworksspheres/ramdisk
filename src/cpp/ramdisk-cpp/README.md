# ramdisk (C++)

Cross-platform C++ library that provides a uniform interface for creating and managing RAM disks on **macOS**, **Linux**, and **Windows**.

This is a C++ port of the Python project [clockworksspheres/ramdisk](https://github.com/clockworksspheres/ramdisk).

License: **Unlicense** (public domain) – same as the original.

## Why?

- Faster builds / CI pipelines
- Avoid build-cache poisoning
- Clean, high-speed scratch space for tests
- One API for every major OS

## Supported platforms

| OS       | Backend                          | Privileges          | Notes                                      |
|----------|----------------------------------|---------------------|--------------------------------------------|
| macOS    | `hdiutil` + APFS                 | normal user         | No root required                           |
| Linux    | `tmpfs` (or `ramfs`)             | root / CAP_SYS_ADMIN| `mount` must be available                  |
| Windows  | Arsenal Image Mounter (`aim_ll`) | Administrator       | [Download AIM](https://github.com/ArsenalRecon/Arsenal-Image-Mounter) |

## Requirements

- C++17 compiler (GCC ≥ 8, Clang ≥ 7, MSVC 2019+)
- CMake ≥ 3.16
- Platform tools listed above

## Building

```bash
mkdir build && cd build
cmake .. -DRAMDISK_BUILD_EXAMPLES=ON
cmake --build .
```

## Quick start

```cpp
#include "ramdisk/RamDisk.hpp"
#include <iostream>

int main() {
    auto disk = ramdisk::createRamDisk(512);   // 512 MB, temp mount point

    if (disk->success()) {
        auto [ok, mnt, dev] = disk->getData();
        std::cout << "Mounted at " << mnt << " (device " << dev << ")\n";

        // … use the ramdisk …

        disk->umount();
    }
}
```

Or with explicit options:

```cpp
ramdisk::RamDiskOptions opts;
opts.sizeMb     = 1024;
opts.mountPoint = "/mnt/build-cache";   // Linux / macOS
// opts.mountPoint = "R:";              // Windows drive letter
opts.fsType     = "tmpfs";              // Linux only
opts.mode       = 0755;                 // Linux only

auto disk = ramdisk::createRamDisk(opts);
```

## API overview

```cpp
namespace ramdisk {

struct RamDiskOptions {
    uint64_t    sizeMb         = 512;
    std::string mountPoint;             // empty → temporary directory
    bool        disableJournal = false; // macOS
    std::string fsType         = "tmpfs"; // Linux: "tmpfs" | "ramfs"
    int         mode           = 0700;  // Linux
};

std::unique_ptr<IRamDisk> createRamDisk(const RamDiskOptions& = {});
std::unique_ptr<IRamDisk> createRamDisk(uint64_t sizeMb, const std::string& mountPoint = "");

bool umount(const std::string& device);
bool eject (const std::string& device);   // alias

class IRamDisk {
public:
    virtual bool        umount() = 0;
    virtual bool        unmount();                    // alias
    virtual std::string getDevice() const = 0;
    virtual std::string getMountPoint() const = 0;
    virtual bool        success() const = 0;
    virtual std::tuple<bool,std::string,std::string> getData() const = 0;
    virtual std::tuple<bool,std::string,std::string> getNlogData() = 0;
    virtual std::tuple<bool,std::string,std::string> getNprintData() = 0;
    virtual std::string getVersion() const = 0;
};

} // namespace ramdisk
```

## Examples

```bash
# After building
./ramdisk_example          # creates 256 MB, writes a test file, unmounts
./ramdisk_cli create --size 512
./ramdisk_cli umount /path/or/device
```

## Design notes / differences from the Python original

- Modern C++17, header + static/shared library, CMake-based.
- Minimal dependencies (only the C++ standard library + platform APIs).
- The rich custom logging / environment / fsHelper subsystems of the Python code were simplified to a lightweight logger and process runner.
- RAII: the ramdisk is automatically unmounted when the `unique_ptr` goes out of scope (unless you call `umount()` earlier).
- Windows still relies on the external `aim_ll` tool, exactly as the Python version does.

## Future work

- Optional pure-user-space backends (e.g. FUSE on Linux, WinFsp on Windows)
- Union / overlay mounts
- More comprehensive unit tests
- pkg-config / vcpkg / Conan packaging

## License

Unlicense – public domain. See the original project for the spirit of the work.
```