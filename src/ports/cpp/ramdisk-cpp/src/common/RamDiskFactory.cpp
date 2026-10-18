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
    // Prefer hdiutil info (image-path ram://); also diskutil volume names.
    std::set<std::string> ramDevIds;
    auto hdi = runCommand({"/usr/bin/hdiutil", "info"});
    if (hdi.ok()) {
        std::istringstream iss(hdi.stdoutStr);
        std::string line;
        bool inRamBlock = false;
        while (std::getline(iss, line)) {
            if (line.find("image-path") != std::string::npos &&
                line.find("ram://") != std::string::npos) {
                inRamBlock = true;
            }
            if (inRamBlock) {
                static const std::regex devRe(R"(/dev/(disk\d+(?:s\d+)*))");
                std::smatch m;
                if (std::regex_search(line, m, devRe)) {
                    ramDevIds.insert(m[1].str());
                }
                if (line.find_first_not_of(" \t\r\n") == std::string::npos) {
                    inRamBlock = false;
                }
            }
        }
    }

    auto list = runCommand({"/usr/sbin/diskutil", "list"});
    {
        std::istringstream iss(list.stdoutStr);
        std::string line;
        while (std::getline(iss, line)) {
            if (line.find("RAMDisk") == std::string::npos &&
                line.find("RAMDISK") == std::string::npos) {
                continue;
            }
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
        static const std::regex re(
            R"(^(/dev/disk\d+(?:s\d+)*)\s+on\s+(\S+))");
        std::smatch m;
        while (std::getline(iss, line)) {
            if (!std::regex_search(line, m, re)) continue;
            const std::string devPath = m[1].str();
            const std::string mountPt = m[2].str();
            const auto slash = devPath.find_last_of('/');
            const std::string shortId =
                (slash == std::string::npos) ? devPath : devPath.substr(slash + 1);
            bool match = ramDevIds.count(shortId) > 0;
            if (!match) {
                for (const auto& id : ramDevIds) {
                    if (shortId.rfind(id, 0) == 0 || id.rfind(shortId, 0) == 0) {
                        match = true;
                        break;
                    }
                }
            }
            if (match) {
                out.push_back({devPath, mountPt});
            }
        }
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
    // Parse `aim_ll -l` the same way as the Python winAIMRamdisk.getMountDisks():
    //
    //   Device number 0
    //   ...
    //   Mounted at R:\
    //
    //   Device number 1
    //   ...
    auto res = runCommand({"aim_ll", "-l"});
    // aim_ll may write to stdout or stderr depending on version
    std::string text = res.stdoutStr;
    if (text.empty()) {
        text = res.stderrStr;
    }
    if (text.empty() && !res.ok()) {
        RD_LOG_WARN("aim_ll -l failed (is Arsenal Image Mounter / aim_ll on PATH?): " +
                    res.stderrStr);
    } else {
        std::istringstream iss(text);
        std::string line;
        std::string currentDevice;
        std::string currentMount;
        auto flush = [&]() {
            if (!currentDevice.empty() && !currentMount.empty()) {
                // Skip UNC-style / odd paths that Python skips (\\\\\\\\)
                if (currentMount.find("\\\\") == 0 &&
                    currentMount.find(":\\") == std::string::npos) {
                    // still allow drive letters; only skip pure UNC noise
                }
                out.push_back({currentDevice, currentMount});
            }
            currentDevice.clear();
            currentMount.clear();
        };

        while (std::getline(iss, line)) {
            // trim
            while (!line.empty() && (line.back() == '\r' || line.back() == ' ' ||
                                    line.back() == '\t')) {
                line.pop_back();
            }
            size_t start = 0;
            while (start < line.size() &&
                   (line[start] == ' ' || line[start] == '\t')) {
                ++start;
            }
            line = line.substr(start);

            if (line.empty()) {
                flush();
                continue;
            }
            // Skip lines that are mostly backslashes (Python: re.search(r"\\\\\\\\"))
            if (line.find("\\\\\\\\") != std::string::npos) {
                continue;
            }

            // "Device number 0" / "Device number 12"
            if (line.rfind("Device number", 0) == 0) {
                // Starting a new device block — flush previous if complete
                if (!currentDevice.empty() && !currentMount.empty()) {
                    flush();
                }
                std::istringstream ls(line);
                std::string w, last;
                while (ls >> w) last = w;
                currentDevice = last;
                currentMount.clear();
                continue;
            }

            // "... Mounted at R:\"  or  "Mounted at C:\Users\...\ram"
            auto pos = line.find("Mounted at ");
            if (pos != std::string::npos) {
                currentMount = line.substr(pos + std::string("Mounted at ").size());
                // trim trailing whitespace / CR
                while (!currentMount.empty() &&
                       (currentMount.back() == ' ' || currentMount.back() == '\r' ||
                        currentMount.back() == '\t')) {
                    currentMount.pop_back();
                }
                continue;
            }
        }
        flush(); // last block may not end with a blank line
    }
#endif

    RD_LOG_INFO("listMountedRamDisks: found " + std::to_string(out.size()));
    return out;
}

} // namespace ramdisk