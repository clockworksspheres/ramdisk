#include "MacRamDisk.hpp"
#include "ramdisk/Logger.hpp"
#include "ramdisk/Process.hpp"
#include "ramdisk/Utils.hpp"

#include <regex>
#include <sstream>

namespace ramdisk {

MacRamDisk::MacRamDisk(const RamDiskOptions& opts)
    : sizeMb_(opts.sizeMb)
    , disableJournal_(opts.disableJournal)
{
    if (!isMemoryAvailable(sizeMb_)) {
        throw MemoryNotAvailableError(
            "Not enough free memory for " + std::to_string(sizeMb_) + " MB ramdisk");
    }

    if (opts.mountPoint.empty()) {
        mountPoint_ = makeTempDir("ramdisk-");
    } else {
        mountPoint_ = opts.mountPoint;
        ensureDirectory(mountPoint_);
    }

    success_ = createAndMount();
    ownsMount_ = success_;
    getNlogData();
}

MacRamDisk::~MacRamDisk() {
    if (ownsMount_ && success_) {
        umount();
    }
}

namespace {

std::string trim(std::string s) {
    while (!s.empty() && (s.back() == '\n' || s.back() == '\r' ||
                          s.back() == ' ' || s.back() == '\t')) {
        s.pop_back();
    }
    while (!s.empty() && (s.front() == ' ' || s.front() == '\t')) {
        s.erase(s.begin());
    }
    return s;
}

/** Extract first /dev/diskN[sN...] path from text. */
std::string extractDevPath(const std::string& text) {
    static const std::regex re(R"(/dev/disk\d+(?:s\d+)*)");
    std::smatch m;
    if (std::regex_search(text, m, re)) {
        return m.str();
    }
    return {};
}

/**
 * After eraseVolume, the volume is mounted at /Volumes/<name>.
 * Find the device node that is currently mounted there via `mount`.
 */
std::string deviceMountedAt(const std::string& mountPath) {
    auto res = runCommand({"/sbin/mount"});
    // Lines look like: /dev/disk4s1s1 on /Volumes/RAMDisk (apfs, local, ...)
    std::istringstream iss(res.stdoutStr);
    std::string line;
    const std::string needle = " on " + mountPath + " ";
    while (std::getline(iss, line)) {
        auto pos = line.find(needle);
        if (pos != std::string::npos) {
            return extractDevPath(line.substr(0, pos));
        }
        // Also accept end-of-line without trailing space in options
        const std::string needle2 = " on " + mountPath;
        pos = line.find(needle2);
        if (pos != std::string::npos) {
            return extractDevPath(line.substr(0, pos));
        }
    }
    return {};
}

} // namespace

bool MacRamDisk::createAndMount() {
    // ------------------------------------------------------------------
    // Reliable modern macOS flow:
    //   1. hdiutil attach -nomount ram://<sectors>
    //   2. diskutil eraseVolume APFS <name> <device>
    //      → formats and mounts at /Volumes/<name>
    //   3. Discover the real volume device from `mount`
    //   4. unmount, then remount at the caller-requested path
    // ------------------------------------------------------------------

    // 1. Create RAM-backed device (1 MB = 2048 × 512-byte sectors)
    const std::uint64_t sectors = sizeMb_ * 2048;
    auto attach = runCommand({
        "/usr/bin/hdiutil", "attach", "-nomount",
        "ram://" + std::to_string(sectors)
    });
    if (!attach.ok()) {
        RD_LOG_ERROR("hdiutil attach failed: " + attach.stderrStr);
        return false;
    }

    device_ = extractDevPath(attach.stdoutStr);
    if (device_.empty()) {
        // hdiutil sometimes prints just "disk4"
        auto raw = trim(attach.stdoutStr);
        if (raw.find("disk") == 0) {
            device_ = "/dev/" + raw;
        }
    }
    if (device_.empty() || device_.find("/dev/disk") != 0) {
        RD_LOG_ERROR("Could not parse device from hdiutil output: [" +
                     attach.stdoutStr + "]");
        return false;
    }
    RD_LOG_INFO("Attached device: " + device_);

    // 2. Format as APFS (auto-mounts under /Volumes/RAMDisk)
    const std::string volName = "RAMDisk";
    const std::string defaultMount = "/Volumes/" + volName;

    auto erase = runCommand({
        "/usr/sbin/diskutil", "eraseVolume", "APFS", volName, device_
    });
    if (!erase.ok()) {
        RD_LOG_ERROR("diskutil eraseVolume failed: " + erase.stderrStr +
                     "\n" + erase.stdoutStr);
        runCommand({"/usr/bin/hdiutil", "detach", device_, "-force"});
        return false;
    }
    RD_LOG_INFO("Formatted APFS volume on " + device_);

    // 3. Discover the actual *volume* device (not the raw attach node).
    //    eraseVolume / APFS often creates a second disk (e.g. disk4 → disk5)
    //    or a slice (disk4s1 / disk4s1s1). Prefer whatever `mount` reports.
    partition_ = deviceMountedAt(defaultMount);
    if (partition_.empty()) {
        auto list = runCommand({"/usr/sbin/diskutil", "list"});
        RD_LOG_DEBUG("diskutil list:\n" + list.stdoutStr);

        // Collect /dev/diskN paths and prefer a *different* whole disk
        // that appears after our attach device (second consecutive disk).
        static const std::regex wholeRe(R"(/dev/disk(\d+)\b)");
        int baseNum = -1;
        {
            std::smatch m;
            if (std::regex_search(device_, m, wholeRe)) {
                baseNum = std::stoi(m[1].str());
            }
        }
        std::string secondDisk;
        for (auto it = std::sregex_iterator(list.stdoutStr.begin(),
                                            list.stdoutStr.end(), wholeRe);
             it != std::sregex_iterator(); ++it) {
            const int n = std::stoi((*it)[1].str());
            if (baseNum >= 0 && n == baseNum + 1) {
                secondDisk = "/dev/disk" + std::to_string(n);
                break;
            }
        }

        // Longest path under our device family (volume slice)
        static const std::regex pathRe(R"(/dev/disk\d+(?:s\d+)*)");
        std::string longest;
        for (auto it = std::sregex_iterator(list.stdoutStr.begin(),
                                            list.stdoutStr.end(), pathRe);
             it != std::sregex_iterator(); ++it) {
            const auto& s = it->str();
            if (s.find(device_) == 0 && s.size() > longest.size()) {
                longest = s;
            }
        }

        if (!secondDisk.empty()) {
            partition_ = secondDisk;
        } else if (!longest.empty() && longest != device_) {
            partition_ = longest;
        } else {
            partition_ = device_;
        }
    }
    RD_LOG_INFO("Raw attach device: " + device_);
    RD_LOG_INFO("Volume device (for GUI/eject): " + partition_);

    // If the caller wants the default /Volumes location, we're done.
    if (mountPoint_ == defaultMount) {
        RD_LOG_INFO("Mounted " + partition_ + " at " + mountPoint_);
        return true;
    }

    // 4. Move the mount to the requested path
    runCommand({"/usr/sbin/diskutil", "unmount", "force", defaultMount});
    runCommand({"/usr/sbin/diskutil", "unmount", "force", partition_});

    ensureDirectory(mountPoint_);

    auto mnt = runCommand({
        "/usr/sbin/diskutil", "mount", "-mountPoint",
        mountPoint_, partition_
    });
    if (!mnt.ok()) {
        RD_LOG_WARN("mount volume failed (" + trim(mnt.stderrStr) +
                    "), trying whole device...");
        mnt = runCommand({
            "/usr/sbin/diskutil", "mount", "-mountPoint",
            mountPoint_, device_
        });
    }
    if (!mnt.ok()) {
        RD_LOG_WARN("diskutil mount failed (" + trim(mnt.stderrStr) +
                    "), trying mount_apfs...");
        mnt = runCommand({"/sbin/mount_apfs", partition_, mountPoint_});
    }
    if (!mnt.ok()) {
        RD_LOG_ERROR("Failed to mount at " + mountPoint_ + ": " +
                     mnt.stderrStr + "\n" + mnt.stdoutStr);
        runCommand({"/usr/bin/hdiutil", "detach", device_, "-force"});
        return false;
    }

    // Refresh volume device from the final mount point (source of truth)
    auto mounted = deviceMountedAt(mountPoint_);
    if (!mounted.empty()) {
        partition_ = mounted;
    }

    RD_LOG_INFO("Mounted " + partition_ + " at " + mountPoint_);
    return true;
}

bool MacRamDisk::umount() {
    if (!success_) return false;

    // Eject the volume device first; fall back to the raw attach node
    const std::string vol = getDevice();
    RD_LOG_INFO("Unmounting / detaching volume " + vol +
                " (attach node " + device_ + ")");
    auto res = runCommand({"/usr/sbin/diskutil", "eject", vol});
    if (!res.ok()) {
        res = runCommand({"/usr/sbin/diskutil", "eject", device_});
    }
    if (!res.ok()) {
        res = runCommand({"/usr/bin/hdiutil", "detach", device_, "-force"});
    }
    if (res.ok()) {
        ownsMount_ = false;
        success_ = false;
        return true;
    }
    RD_LOG_ERROR("eject/detach failed: " + res.stderrStr);
    return false;
}

bool MacRamDisk::umountDevice(const std::string& device) {
    // GUI may pass the volume (second) device; try that, then hdiutil detach
    auto res = runCommand({"/usr/sbin/diskutil", "eject", device});
    if (!res.ok()) {
        res = runCommand({"/usr/bin/hdiutil", "detach", device, "-force"});
    }
    return res.ok();
}

std::tuple<bool, std::string, std::string>
MacRamDisk::getData() const {
    // Report the volume device (second disk / APFS volume), not the raw attach node
    return {success_, mountPoint_, getDevice()};
}

std::tuple<bool, std::string, std::string>
MacRamDisk::getNlogData() {
    RD_LOG_INFO("Success: " + std::string(success_ ? "true" : "false"));
    RD_LOG_INFO("Mount point: " + mountPoint_);
    RD_LOG_INFO("Device: " + getDevice());
    return getData();
}

std::tuple<bool, std::string, std::string>
MacRamDisk::getNprintData() {
    std::cout << "Success: " << (success_ ? "true" : "false") << '\n'
              << "Mount point: " << mountPoint_ << '\n'
              << "Device: " << getDevice() << '\n';
    return getData();
}

} // namespace ramdisk