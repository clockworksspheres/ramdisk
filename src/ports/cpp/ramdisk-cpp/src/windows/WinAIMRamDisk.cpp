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
        // Normalise: forward slashes → backslashes, strip trailing separators
        for (char& c : mountPoint_) {
            if (c == '/') c = '\\';
        }
        while (!mountPoint_.empty() &&
               (mountPoint_.back() == '\\' || mountPoint_.back() == '/')) {
            mountPoint_.pop_back();
        }
        // Drive letter only → ensure "X:" form (aim_ll accepts "R:" or "R:\")
        if (mountPoint_.size() == 1) {
            mountPoint_ += ':';
        }
        // Bare drive letter (e.g. "R:") — do not create a directory
        const bool bareDrive =
            (mountPoint_.size() == 2 && mountPoint_[1] == ':');
        if (!bareDrive) {
            // Directory mount (e.g. C:\Users\me\ram0) — create if missing
            if (!ensureDirectory(mountPoint_)) {
                throw RamDiskError(
                    "Cannot create mount directory: " + mountPoint_);
            }
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
    // Mount can be a drive letter (R:) or an empty directory path.
    std::string mntArg = mountPoint_;
    // For bare drive letters, AIM is happier with "R:" than "R:\"
    if (mntArg.size() == 2 && mntArg[1] == ':') {
        // keep as-is
    }

    std::ostringstream cmd;
    cmd << "aim_ll -a -s " << sizeMb_ << "M"
        << " -m \"" << mntArg << "\""
        << " -p \"/fs:ntfs /q /y\"";

    RD_LOG_INFO("Running: " + cmd.str());
    auto res = runShell(cmd.str());
    const std::string combined = res.stdoutStr + "\n" + res.stderrStr;

    if (!res.ok() && combined.find("Created device") == std::string::npos) {
        RD_LOG_ERROR("aim_ll failed. Is Arsenal Image Mounter installed and on PATH?\n"
                     + res.stderrStr + "\n" + res.stdoutStr);
        return false;
    }

    // Parse "Created device X" from output
    std::regex re(R"(Created device\s+(\S+))", std::regex::icase);
    std::smatch m;
    if (std::regex_search(combined, m, re)) {
        device_ = m[1].str();
    } else {
        device_ = "unknown";
    }

    // Prefer the mount path AIM reports ("Mounted at ...")
    auto pos = combined.find("Mounted at ");
    if (pos != std::string::npos) {
        std::string reported = combined.substr(pos + 11);
        // first line only
        auto nl = reported.find_first_of("\r\n");
        if (nl != std::string::npos) reported = reported.substr(0, nl);
        while (!reported.empty() &&
               (reported.back() == ' ' || reported.back() == '\t')) {
            reported.pop_back();
        }
        if (!reported.empty()) {
            mountPoint_ = reported;
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
    // Accept either AIM device number ("0") or a mount path ("R:" / "R:\...")
    ProcessResult res;
    if (!device.empty() &&
        (device.find(':') != std::string::npos || device.find('\\') != std::string::npos)) {
        // Looks like a mount point / drive letter
        res = runShell("aim_ll -R -m \"" + device + "\"");
        if (!res.ok()) {
            res = runCommand({"aim_ll", "-R", "-u", device});
        }
    } else {
        res = runCommand({"aim_ll", "-R", "-u", device});
        if (!res.ok()) {
            res = runShell("aim_ll -R -m \"" + device + "\"");
        }
    }
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