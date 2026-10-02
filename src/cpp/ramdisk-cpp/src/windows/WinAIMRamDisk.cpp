#include "WinAIMRamDisk.hpp"
#include "ramdisk/Logger.hpp"
#include "ramdisk/Process.hpp"
#include "ramdisk/Utils.hpp"

#include <regex>
#include <sstream>

namespace ramdisk {

WinAIMRamDisk::WinAIMRamDisk(const RamDiskOptions& opts)
    : sizeMb_(opts.sizeMb)
{
    if (!isMemoryAvailable(sizeMb_)) {
        throw MemoryNotAvailableError(
            "Not enough free memory for " + std::to_string(sizeMb_) + " MB ramdisk");
    }

    if (opts.mountPoint.empty()) {
        // Prefer a free drive letter; fall back to a temp path
        mountPoint_ = "R:";
    } else {
        mountPoint_ = opts.mountPoint;
        // Normalise trailing slashes
        while (!mountPoint_.empty() &&
               (mountPoint_.back() == '\\' || mountPoint_.back() == '/')) {
            mountPoint_.pop_back();
        }
    }

    success_ = create();
    ownsMount_ = success_;
    getNlogData();
}

WinAIMRamDisk::~WinAIMRamDisk() {
    if (ownsMount_ && success_) {
        umount();
    }
}

bool WinAIMRamDisk::create() {
    // aim_ll -a -s <size>M -m <mount> -p "/fs:ntfs /q /y"
    std::ostringstream cmd;
    cmd << "aim_ll -a -s " << sizeMb_ << "M"
        << " -m \"" << mountPoint_ << "\""
        << " -p \"/fs:ntfs /q /y\"";

    RD_LOG_INFO("Running: " + cmd.str());
    auto res = runShell(cmd.str());

    if (!res.ok() && res.stdoutStr.find("Created device") == std::string::npos) {
        RD_LOG_ERROR("aim_ll failed. Is Arsenal Image Mounter installed and on PATH?\n"
                     + res.stderrStr + "\n" + res.stdoutStr);
        return false;
    }

    // Parse "Created device X" from output
    std::regex re(R"(Created device\s+(\S+))", std::regex::icase);
    std::smatch m;
    if (std::regex_search(res.stdoutStr, m, re)) {
        device_ = m[1].str();
    } else {
        // Fallback: try stderr or whole output
        if (std::regex_search(res.stderrStr, m, re)) {
            device_ = m[1].str();
        } else {
            device_ = "unknown";
        }
    }

    RD_LOG_INFO("Created AIM device: " + device_ + " mounted at " + mountPoint_);
    return true;
}

bool WinAIMRamDisk::umount() {
    if (!success_) return false;
    RD_LOG_INFO("Removing AIM device " + device_);
    // aim_ll -R -u <device>
    auto res = runCommand({"aim_ll", "-R", "-u", device_});
    if (!res.ok()) {
        // try by mount point
        res = runShell("aim_ll -R -m \"" + mountPoint_ + "\"");
    }
    if (res.ok()) {
        ownsMount_ = false;
        success_ = false;
        return true;
    }
    RD_LOG_ERROR("aim_ll remove failed: " + res.stderrStr);
    return false;
}

bool WinAIMRamDisk::umountDevice(const std::string& device) {
    auto res = runCommand({"aim_ll", "-R", "-u", device});
    return res.ok();
}

std::tuple<bool, std::string, std::string>
WinAIMRamDisk::getData() const {
    return {success_, mountPoint_, device_};
}

std::tuple<bool, std::string, std::string>
WinAIMRamDisk::getNlogData() {
    RD_LOG_INFO("Success: " + std::string(success_ ? "true" : "false"));
    RD_LOG_INFO("Mount point: " + mountPoint_);
    RD_LOG_INFO("Device: " + device_);
    return getData();
}

std::tuple<bool, std::string, std::string>
WinAIMRamDisk::getNprintData() {
    std::cout << "Success: " << (success_ ? "true" : "false") << '\n'
              << "Mount point: " << mountPoint_ << '\n'
              << "Device: " << device_ << '\n';
    return getData();
}

} // namespace ramdisk