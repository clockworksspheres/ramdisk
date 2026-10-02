#pragma once

#include "ramdisk/RamDisk.hpp"
#include <string>

namespace ramdisk {

/**
 * Windows implementation using Arsenal Image Mounter (aim_ll.exe).
 * The binary must be present on PATH.
 *
 * Download from:
 *   https://github.com/ArsenalRecon/Arsenal-Image-Mounter
 */
class WinAIMRamDisk : public IRamDisk {
public:
    explicit WinAIMRamDisk(const RamDiskOptions& opts);
    ~WinAIMRamDisk() override;

    bool umount() override;
    std::string getDevice() const override { return device_; }
    std::string getMountPoint() const override { return mountPoint_; }
    bool success() const override { return success_; }
    std::tuple<bool, std::string, std::string> getData() const override;
    std::tuple<bool, std::string, std::string> getNlogData() override;
    std::tuple<bool, std::string, std::string> getNprintData() override;
    std::string getVersion() const override { return "2.0.0-cpp-windows"; }
    void releaseOwnership() override { ownsMount_ = false; }

    static bool umountDevice(const std::string& device);

private:
    bool create();

    std::uint64_t sizeMb_;
    std::string   mountPoint_;   // drive letter or path, e.g. "R:"
    std::string   device_;       // AIM device id
    bool          success_   = false;
    bool          ownsMount_ = false;
};

} // namespace ramdisk