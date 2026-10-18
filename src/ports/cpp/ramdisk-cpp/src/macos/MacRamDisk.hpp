#pragma once

#include "ramdisk/RamDisk.hpp"
#include <string>

namespace ramdisk {

class MacRamDisk : public IRamDisk {
public:
    explicit MacRamDisk(const RamDiskOptions& opts);
    ~MacRamDisk() override;

    bool umount() override;
    /** Volume device shown to users / GUI (APFS volume), not the raw attach node. */
    std::string getDevice() const override {
        return !partition_.empty() ? partition_ : device_;
    }
    std::string getMountPoint() const override { return mountPoint_; }
    bool success() const override { return success_; }
    std::tuple<bool, std::string, std::string> getData() const override;
    std::tuple<bool, std::string, std::string> getNlogData() override;
    std::tuple<bool, std::string, std::string> getNprintData() override;
    std::string getVersion() const override { return "2.0.0-cpp-macos"; }
    void releaseOwnership() override { ownsMount_ = false; }

    static bool umountDevice(const std::string& device);

private:
    bool createAndMount();

    std::uint64_t sizeMb_;
    std::string   mountPoint_;
    std::string   device_;          // e.g. /dev/disk4
    std::string   partition_;       // e.g. /dev/disk4s1
    bool          success_   = false;
    bool          ownsMount_ = false;
    bool          disableJournal_;
};

} // namespace ramdisk