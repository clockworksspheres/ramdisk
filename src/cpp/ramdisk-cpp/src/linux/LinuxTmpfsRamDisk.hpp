#pragma once

#include "ramdisk/RamDisk.hpp"
#include <string>

namespace ramdisk {

class LinuxTmpfsRamDisk : public IRamDisk {
public:
    explicit LinuxTmpfsRamDisk(const RamDiskOptions& opts);
    ~LinuxTmpfsRamDisk() override;

    bool umount() override;
    std::string getDevice() const override { return device_; }
    std::string getMountPoint() const override { return mountPoint_; }
    bool success() const override { return success_; }
    std::tuple<bool, std::string, std::string> getData() const override;
    std::tuple<bool, std::string, std::string> getNlogData() override;
    std::tuple<bool, std::string, std::string> getNprintData() override;
    std::string getVersion() const override { return "2.0.0-cpp-linux"; }
    void releaseOwnership() override { ownsMount_ = false; }

    static bool umountDevice(const std::string& mountPoint);

private:
    bool mount();
    std::string buildMountCommand() const;

    std::uint64_t sizeMb_;
    std::string   mountPoint_;
    std::string   device_     = "tmpfs";
    std::string   fsType_;
    int           mode_;
    int           uid_;
    int           gid_;
    bool          success_    = false;
    bool          ownsMount_  = false;
};

} // namespace ramdisk