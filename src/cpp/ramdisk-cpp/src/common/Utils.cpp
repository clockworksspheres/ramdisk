#include "ramdisk/Utils.hpp"
#include "ramdisk/Logger.hpp"

#include <random>
#include <sstream>
#include <filesystem>
#include <system_error>

#ifdef _WIN32
#  define WIN32_LEAN_AND_MEAN
#  include <windows.h>
#elif defined(__APPLE__)
#  include <unistd.h>
#  include <sys/types.h>
#  include <sys/sysctl.h>
#  include <mach/mach.h>
#  include <mach/vm_statistics.h>
#  include <mach/mach_types.h>
#  include <mach/mach_init.h>
#  include <mach/mach_host.h>
#else
#  include <unistd.h>
#  include <sys/stat.h>
#  include <sys/types.h>
#  include <pwd.h>
#  include <fstream>
#endif

namespace fs = std::filesystem;

namespace ramdisk {

std::string makeTempDir(const std::string& prefix) {
    auto base = fs::temp_directory_path();
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, 15);

    for (int attempt = 0; attempt < 100; ++attempt) {
        std::ostringstream name;
        name << prefix;
        for (int i = 0; i < 8; ++i) {
            name << std::hex << dis(gen);
        }
        auto path = base / name.str();
        std::error_code ec;
        if (fs::create_directory(path, ec)) {
            return path.string();
        }
    }
    throw std::runtime_error("Unable to create temporary directory");
}

std::uint64_t freeMemoryMb() {
#ifdef _WIN32
    MEMORYSTATUSEX st{};
    st.dwLength = sizeof(st);
    if (GlobalMemoryStatusEx(&st)) {
        return st.ullAvailPhys / (1024ULL * 1024ULL);
    }
    return 0;
#elif defined(__APPLE__)
    // macOS: use host_statistics for free + inactive pages
    mach_msg_type_number_t count = HOST_VM_INFO_COUNT;
    vm_statistics_data_t vmstat{};
    if (host_statistics(mach_host_self(), HOST_VM_INFO,
                        reinterpret_cast<host_info_t>(&vmstat), &count) != KERN_SUCCESS) {
        return 0;
    }
    // free + inactive + speculative ≈ usable memory on macOS
    const std::uint64_t available_pages =
        static_cast<std::uint64_t>(vmstat.free_count) +
        static_cast<std::uint64_t>(vmstat.inactive_count) +
        static_cast<std::uint64_t>(vmstat.speculative_count);
    long pageSize = sysconf(_SC_PAGE_SIZE);
    if (pageSize <= 0) {
        pageSize = 4096;
    }
    return available_pages * static_cast<std::uint64_t>(pageSize) / (1024ULL * 1024ULL);
#else
    // Linux: prefer /proc/meminfo
    std::ifstream meminfo("/proc/meminfo");
    if (meminfo) {
        std::string key;
        std::uint64_t value = 0;
        std::string unit;
        while (meminfo >> key >> value >> unit) {
            if (key == "MemAvailable:") {
                return value / 1024; // kB → MB
            }
        }
    }
    // Fallback: sysconf (Linux)
#ifdef _SC_AVPHYS_PAGES
    long pages    = sysconf(_SC_AVPHYS_PAGES);
    long pageSize = sysconf(_SC_PAGE_SIZE);
    if (pages > 0 && pageSize > 0) {
        return static_cast<std::uint64_t>(pages) *
               static_cast<std::uint64_t>(pageSize) / (1024ULL * 1024ULL);
    }
#endif
    return 0;
#endif
}

bool isMemoryAvailable(std::uint64_t sizeMb) {
    auto free = freeMemoryMb();
    RD_LOG_DEBUG("Requested " + std::to_string(sizeMb) + " MB, free ≈ " + std::to_string(free) + " MB");
    // Leave a small safety margin
    return free > sizeMb + 64;
}

bool ensureDirectory(const std::string& path) {
    std::error_code ec;
    if (fs::exists(path, ec)) {
        return fs::is_directory(path, ec);
    }
    return fs::create_directories(path, ec);
}

int currentUid() {
#ifdef _WIN32
    return 0;
#else
    return static_cast<int>(geteuid());
#endif
}

int currentGid() {
#ifdef _WIN32
    return 0;
#else
    return static_cast<int>(getegid());
#endif
}

std::string platformName() {
#ifdef _WIN32
    return "windows";
#elif defined(__APPLE__)
    return "macos";
#elif defined(__linux__)
    return "linux";
#else
    return "unknown";
#endif
}

} // namespace ramdisk