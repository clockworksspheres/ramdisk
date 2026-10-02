#include "ramdisk/RamDisk.hpp"
#include "ramdisk/Logger.hpp"
#include "ramdisk/Utils.hpp"

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

} // namespace ramdisk