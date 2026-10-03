#pragma once

/**
 * Cross-platform RamDisk library (C++ port of clockworksspheres/ramdisk)
 *
 * Provides a uniform interface to create / manage RAM disks on:
 *   - macOS   (hdiutil + APFS)
 *   - Linux   (tmpfs)
 *   - Windows (Arsenal Image Mounter / aim_ll)
 *
 * License: Unlicense (public domain) – same as the original Python project.
 */

#include <cstdint>
#include <memory>
#include <string>
#include <tuple>
#include <optional>
#include <stdexcept>

namespace ramdisk {

// ---------------------------------------------------------------------------
// Exceptions
// ---------------------------------------------------------------------------
class RamDiskError : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

class SizeInvalidError : public RamDiskError {
public:
    explicit SizeInvalidError(const std::string& msg) : RamDiskError(msg) {}
};

class NotValidForThisOS : public RamDiskError {
public:
    explicit NotValidForThisOS(const std::string& msg) : RamDiskError(msg) {}
};

class MemoryNotAvailableError : public RamDiskError {
public:
    explicit MemoryNotAvailableError(const std::string& msg) : RamDiskError(msg) {}
};

class SystemToolNotAvailable : public RamDiskError {
public:
    explicit SystemToolNotAvailable(const std::string& msg) : RamDiskError(msg) {}
};

// ---------------------------------------------------------------------------
// Abstract interface
// ---------------------------------------------------------------------------
class IRamDisk {
public:
    virtual ~IRamDisk() = default;

    /** Unmount / eject the ramdisk. Returns true on success. */
    virtual bool umount() = 0;

    /** Alias for umount(). */
    virtual bool unmount() { return umount(); }

    /** Device path / identifier used by the OS. */
    virtual std::string getDevice() const = 0;

    /** Filesystem mount point. */
    virtual std::string getMountPoint() const = 0;

    /** Whether creation + mount succeeded. */
    virtual bool success() const = 0;

    /**
     * Return (success, mountPoint, device)
     */
    virtual std::tuple<bool, std::string, std::string> getData() const = 0;

    /** Same as getData() but also logs the values. */
    virtual std::tuple<bool, std::string, std::string> getNlogData() = 0;

    /** Same as getData() but also prints the values. */
    virtual std::tuple<bool, std::string, std::string> getNprintData() = 0;

    virtual std::string getVersion() const = 0;

    /**
     * Release ownership of the mount.
     * After this, the destructor will NOT unmount the ramdisk —
     * useful when you want the volume to outlive the process.
     * Call umount(device) or the CLI later to clean up.
     */
    virtual void releaseOwnership() = 0;

    /** Optional: create a union / overlay mount (platform dependent). */
    virtual bool unionOver(const std::string& /*target*/) { return false; }
};

// ---------------------------------------------------------------------------
// Factory – the main entry point users should call
// ---------------------------------------------------------------------------
struct RamDiskOptions {
    std::uint64_t sizeMb          = 512;          // size in megabytes
    std::string   mountPoint;                     // empty → temporary directory
    bool          disableJournal  = false;        // macOS only
    std::string   fsType          = "tmpfs";      // Linux: "tmpfs" or "ramfs"
    int           mode            = 0700;         // Linux permission bits
    std::string   sudoPassword;                   // Linux: used with sudo -S when not root
    // Windows: aim_ll must be on PATH
};

/**
 * Create a platform-appropriate ramdisk.
 *
 * Throws on unsupported OS or invalid size.
 * The returned object owns the lifetime of the ramdisk; call umount()
 * (or let the destructor do it) when finished.
 */
std::unique_ptr<IRamDisk> createRamDisk(const RamDiskOptions& opts = {});

/** Convenience overload. */
inline std::unique_ptr<IRamDisk> createRamDisk(std::uint64_t sizeMb,
                                               const std::string& mountPoint = "") {
    RamDiskOptions opts;
    opts.sizeMb     = sizeMb;
    opts.mountPoint = mountPoint;
    return createRamDisk(opts);
}

// ---------------------------------------------------------------------------
// Free functions (mirroring the Python module-level helpers)
// ---------------------------------------------------------------------------

/** Unmount by device identifier. */
bool umount(const std::string& device);

/** Alias. */
bool eject(const std::string& device);

} // namespace ramdisk