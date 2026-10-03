#include "LinuxTmpfsRamDisk.hpp"
#include "ramdisk/Logger.hpp"
#include "ramdisk/Process.hpp"
#include "ramdisk/Utils.hpp"

#include <sstream>
#include <unistd.h>

namespace ramdisk {

LinuxTmpfsRamDisk::LinuxTmpfsRamDisk(const RamDiskOptions& opts)
    : sizeMb_(opts.sizeMb)
    , fsType_(opts.fsType.empty() ? "tmpfs" : opts.fsType)
    , mode_(opts.mode)
    , uid_(currentUid())
    , gid_(currentGid())
    , sudoPassword_(opts.sudoPassword)
{
    if (fsType_ != "tmpfs" && fsType_ != "ramfs") {
        throw RamDiskError("fsType must be 'tmpfs' or 'ramfs'");
    }

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

    success_ = mount();
    ownsMount_ = success_;
    getNlogData();
}

LinuxTmpfsRamDisk::~LinuxTmpfsRamDisk() {
    if (ownsMount_ && success_) {
        umount();
    }
}

std::string LinuxTmpfsRamDisk::buildMountCommand() const {
    // mount -t tmpfs -o size=512m,uid=...,gid=...,mode=700 tmpfs /path
    std::ostringstream opts;
    opts << "size=" << sizeMb_ << "m"
         << ",uid=" << uid_
         << ",gid=" << gid_
         << ",mode=" << std::oct << mode_;

    std::ostringstream cmd;
    cmd << "mount -t " << fsType_
        << " -o " << opts.str()
        << " " << fsType_
        << " " << mountPoint_;
    return cmd.str();
}

bool LinuxTmpfsRamDisk::mount() {
    auto cmd = buildMountCommand();
    RD_LOG_INFO("Mounting: " + cmd);

    ProcessResult res;
    if (geteuid() == 0) {
        res = runShell(cmd);
    } else if (!sudoPassword_.empty()) {
        RD_LOG_INFO("Not root — elevating with sudo -S");
        res = runShellSudo(cmd, sudoPassword_);
    } else {
        // Try without sudo first (might have CAP_SYS_ADMIN)
        res = runShell(cmd);
        if (!res.ok()) {
            RD_LOG_ERROR("mount failed (need root or sudo password): " + res.stderrStr);
            return false;
        }
        return true;
    }

    if (!res.ok()) {
        RD_LOG_ERROR("mount failed: " + res.stderrStr + "\n" + res.stdoutStr);
        return false;
    }
    return true;
}

bool LinuxTmpfsRamDisk::umount() {
    if (!success_) return false;
    RD_LOG_INFO("Unmounting " + mountPoint_);

    ProcessResult res;
    if (geteuid() == 0) {
        res = runCommand({"umount", mountPoint_});
        if (!res.ok()) {
            res = runCommand({"umount", "-l", mountPoint_});
        }
    } else if (!sudoPassword_.empty()) {
        res = runShellSudo("umount '" + mountPoint_ + "'", sudoPassword_);
        if (!res.ok()) {
            res = runShellSudo("umount -l '" + mountPoint_ + "'", sudoPassword_);
        }
    } else {
        res = runCommand({"umount", mountPoint_});
        if (!res.ok()) {
            res = runCommand({"umount", "-l", mountPoint_});
        }
    }

    if (res.ok()) {
        ownsMount_ = false;
        success_ = false;
        return true;
    }
    RD_LOG_ERROR("umount failed: " + res.stderrStr);
    return false;
}

bool LinuxTmpfsRamDisk::umountDevice(const std::string& mountPoint) {
    // No password available at free-function level; try plain umount then sudo -n
    auto res = runCommand({"umount", mountPoint});
    if (!res.ok()) {
        res = runCommand({"umount", "-l", mountPoint});
    }
    if (!res.ok() && geteuid() != 0) {
        // Non-interactive sudo (works if timestamp is still valid)
        res = runShell("sudo -n umount '" + mountPoint + "' 2>/dev/null");
        if (!res.ok()) {
            res = runShell("sudo -n umount -l '" + mountPoint + "' 2>/dev/null");
        }
    }
    return res.ok();
}

std::tuple<bool, std::string, std::string>
LinuxTmpfsRamDisk::getData() const {
    return {success_, mountPoint_, device_};
}

std::tuple<bool, std::string, std::string>
LinuxTmpfsRamDisk::getNlogData() {
    RD_LOG_INFO("Success: " + std::string(success_ ? "true" : "false"));
    RD_LOG_INFO("Mount point: " + mountPoint_);
    RD_LOG_INFO("Device: " + device_);
    return getData();
}

std::tuple<bool, std::string, std::string>
LinuxTmpfsRamDisk::getNprintData() {
    std::cout << "Success: " << (success_ ? "true" : "false") << '\n'
              << "Mount point: " << mountPoint_ << '\n'
              << "Device: " << device_ << '\n';
    return getData();
}

} // namespace ramdisk