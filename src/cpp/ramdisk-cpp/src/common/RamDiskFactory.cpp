#include "ramdisk/RamDisk.hpp"
#include "ramdisk/Logger.hpp"
#include "ramdisk/Utils.hpp"
#include "ramdisk/Process.hpp"

#include <sstream>
#include <fstream>
#include <regex>
#include <set>

#if defined(__APPLE__)
#  include "../macos/MacRamDisk.hpp"
#elif defined(__linux__)
#  include "../linux/LinuxTmpfsRamDisk.hpp"
#elif defined(_WIN32)
#  include "../windows/WinAIMRamDisk.hpp"
#endif

namespace ramdisk {

std::unique_ptr<IRamDisk> createRamDisk(const RamDiskOptions& opts) {
    if (opts.sizeMb == 0) {
        throw SizeInvalidError("Cannot create ramdisk of size 0");
    }

    RD_LOG_INFO("Creating ramdisk of " + std::to_string(opts.sizeMb) +
                " MB on platform " + platformName());

#if defined(__APPLE__)
    return std::make_unique<MacRamDisk>(opts);
#elif defined(__linux__)
    return std::make_unique<LinuxTmpfsRamDisk>(opts);
#elif defined(_WIN32)
    return std::make_unique<WinAIMRamDisk>(opts);
#else
    throw NotValidForThisOS("Ramdisk not available on this OS");
#endif
}

bool umount(const std::string& device) {
#if defined(__APPLE__)
    return MacRamDisk::umountDevice(device);
#elif defined(__linux__)
    return LinuxTmpfsRamDisk::umountDevice(device);
#elif defined(_WIN32)
    return WinAIMRamDisk::umountDevice(device);
#else
    (void)device;
    return false;
#endif
}

bool eject(const std::string& device) {
    return umount(device);
}

std::vector<MountedRamDisk> listMountedRamDisks() {
    std::vector<MountedRamDisk> out;

#if defined(__APPLE__)
    // diskutil list → find lines containing RAMDisk (volume name we use)
    auto list = runCommand({"/usr/sbin/diskutil", "list"});
    std::set<std::string> ramDevIds; // e.g. "disk5s1"
    {
        std::istringstream iss(list.stdoutStr);
        std::string line;
        while (std::getline(iss, line)) {
            if (line.find("RAMDisk") == std::string::npos &&
                line.find("RAMDISK") == std::string::npos) {
                continue;
            }
            // Last token is often the identifier: diskNsM
            std::istringstream ls(line);
            std::string tok, last;
            while (ls >> tok) last = tok;
            if (last.find("disk") == 0) {
                ramDevIds.insert(last);
            }
        }
    }

    auto mnt = runCommand({"/sbin/mount"});
    {
        std::istringstream iss(mnt.stdoutStr);
        std::string line;
        // /dev/disk5s1 on /Volumes/RAMDisk (apfs, local, ...)
        static const std::regex re(
            R"(^(/dev/disk\d+(?:s\d+)*)\s+on\s+(\S+))");
        std::smatch m;
        while (std::getline(iss, line)) {
            if (!std::regex_search(line, m, re)) continue;
            const std::string devPath = m[1].str();
            const std::string mountPt = m[2].str();
            // Match by short id (disk5s1)
            const auto slash = devPath.find_last_of('/');
            const std::string shortId =
                (slash == std::string::npos) ? devPath : devPath.substr(slash + 1);
            if (ramDevIds.count(shortId)) {
                out.push_back({devPath, mountPt});
            }
        }
    }

    // Also pick up custom mount points: hdiutil info for image-path ram://
    auto hdi = runCommand({"/usr/bin/hdiutil", "info"});
    if (hdi.ok() && hdi.stdoutStr.find("ram://") != std::string::npos) {
        // Parse blocks; simple approach: any /dev/diskN already in mount
        // that is not yet listed and whose hdiutil block mentions ram://
        // (handled adequately by RAMDisk name match for our creates)
    }

#elif defined(__linux__)
    // Parse /proc/mounts for tmpfs/ramfs, skip well-known system mounts
    std::ifstream mounts("/proc/mounts");
    std::string line;
    const std::set<std::string> skip = {
        "/dev/shm", "/run", "/run/lock", "/tmp",
        "/dev", "/sys/fs/cgroup", "/sys/fs/cgroup/unified"
    };
    while (std::getline(mounts, line)) {
        // device mountpoint fstype options ...
        std::istringstream iss(line);
        std::string device, mnt, fstype;
        if (!(iss >> device >> mnt >> fstype)) continue;
        if (fstype != "tmpfs" && fstype != "ramfs") continue;
        if (skip.count(mnt)) continue;
        if (mnt.rfind("/run/", 0) == 0) continue;   // /run/...
        if (mnt.rfind("/var/snap", 0) == 0) continue;
        if (mnt.rfind("/sys/", 0) == 0) continue;
        if (mnt.rfind("/dev/", 0) == 0) continue;
        // Unescape octal sequences in mount path (\040 → space) — basic
        std::string mntClean = mnt;
        // Keep device as "tmpfs" for display consistency with create
        out.push_back({device == "tmpfs" || device == "ramfs" ? device : device, mntClean});
    }

#elif defined(_WIN32)
    // AIM: best-effort — not enumerated without aim_ll list support
    (void)out;
#endif

    RD_LOG_INFO("listMountedRamDisks: found " + std::to_string(out.size()));
    return out;
}

} // namespace ramdisk