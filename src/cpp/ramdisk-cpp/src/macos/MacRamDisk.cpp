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

    // 3. Discover the actual volume node (often diskNs1s1 for APFS)
    partition_ = deviceMountedAt(defaultMount);
    if (partition_.empty()) {
        auto list = runCommand({"/usr/sbin/diskutil", "list", device_});
        RD_LOG_DEBUG("diskutil list:\n" + list.stdoutStr);

        // Prefer the longest matching /dev/diskN... path (volume > container)
        static const std::regex re(R"(/dev/disk\d+(?:s\d+)*)");
        std::string best;
        for (auto it = std::sregex_iterator(list.stdoutStr.begin(),
                                            list.stdoutStr.end(), re);
             it != std::sregex_iterator(); ++it) {
            if (it->str().size() > best.size()) {
                best = it->str();
            }
        }
        partition_ = !best.empty() ? best : device_;
    }
    RD_LOG_INFO("Volume device: " + partition_);

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

    RD_LOG_INFO("Mounted " + partition_ + " at " + mountPoint_);
    return true;
}

bool MacRamDisk::umount() {
    if (!success_) return false;

    RD_LOG_INFO("Unmounting / detaching " + device_);
    // Prefer diskutil eject / hdiutil detach
    auto res = runCommand({"/usr/sbin/diskutil", "eject", device_});
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
    auto res = runCommand({"/usr/sbin/diskutil", "eject", device});
    if (!res.ok()) {
        res = runCommand({"/usr/bin/hdiutil", "detach", device, "-force"});
    }
    return res.ok();
}

std::tuple<bool, std::string, std::string>
MacRamDisk::getData() const {
    return {success_, mountPoint_, device_};
}

std::tuple<bool, std::string, std::string>
MacRamDisk::getNlogData() {
    RD_LOG_INFO("Success: " + std::string(success_ ? "true" : "false"));
    RD_LOG_INFO("Mount point: " + mountPoint_);
    RD_LOG_INFO("Device: " + device_);
    return getData();
}

std::tuple<bool, std::string, std::string>
MacRamDisk::getNprintData() {
    std::cout << "Success: " << (success_ ? "true" : "false") << '\n'
              << "Mount point: " << mountPoint_ << '\n'
              << "Device: " << device_ << '\n';
    return getData();
}

} // namespace ramdisk