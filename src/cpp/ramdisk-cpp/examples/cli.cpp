/**
 * Simple command-line interface.
 *
 *   ramdisk_cli create [--size N] [--mount PATH] [--keep]
 *   ramdisk_cli list
 *   ramdisk_cli umount <device|mountpoint>
 */

#include "ramdisk/RamDisk.hpp"
#include "ramdisk/Logger.hpp"
#include <iostream>
#include <iomanip>
#include <string>
#include <cstring>

static void usage(const char* prog) {
    std::cerr
        << "Usage:\n"
        << "  " << prog << " create [--size MB] [--mount PATH] [--keep]\n"
        << "  " << prog << " list\n"
        << "  " << prog << " umount  <device|mountpoint>\n"
        << "\n"
        << "Options:\n"
        << "  --size MB     Ramdisk size in megabytes (default: 512)\n"
        << "  --mount PATH  Mount point (default: temporary directory)\n"
        << "  --keep, -k    Leave ramdisk mounted after exit\n"
        << "\n"
        << "Examples:\n"
        << "  " << prog << " create --size 512 --keep\n"
        << "  " << prog << " create --size 1024 --mount /tmp/ram0 --keep\n"
        << "  " << prog << " list\n"
        << "  " << prog << " umount /dev/disk4\n"
        << "  " << prog << " umount /tmp/ram0\n";
}

int main(int argc, char* argv[]) {
    using namespace ramdisk;

    if (argc < 2) {
        usage(argv[0]);
        return 1;
    }

    std::string cmd = argv[1];

    if (cmd == "create") {
        RamDiskOptions opts;
        opts.sizeMb = 512;
        bool keep = false;

        for (int i = 2; i < argc; ++i) {
            if (std::strcmp(argv[i], "--size") == 0 && i + 1 < argc) {
                opts.sizeMb = std::stoull(argv[++i]);
            } else if (std::strcmp(argv[i], "--mount") == 0 && i + 1 < argc) {
                opts.mountPoint = argv[++i];
            } else if (std::strcmp(argv[i], "--keep") == 0 ||
                       std::strcmp(argv[i], "-k") == 0) {
                keep = true;
            } else {
                std::cerr << "Unknown option: " << argv[i] << '\n';
                usage(argv[0]);
                return 1;
            }
        }

        try {
            auto disk = createRamDisk(opts);
            if (!disk->success()) {
                std::cerr << "Creation failed\n";
                return 1;
            }
            auto [ok, mnt, dev] = disk->getNprintData();

            const std::string target = !dev.empty() ? dev : mnt;

            if (keep) {
                // Do not unmount when the unique_ptr is destroyed
                disk->releaseOwnership();
                std::cout << "\nRamdisk left mounted.\n"
                          << "To unmount later:\n"
                          << "  " << argv[0] << " umount " << target << "\n"
                          << "  # or:  diskutil eject " << target << "\n"
                          << "  # or:  hdiutil detach " << target << "\n";
            } else {
                std::cout << "\nPress Enter to unmount and exit...\n";
                std::cin.get();
                disk->umount();
            }
        } catch (const std::exception& e) {
            std::cerr << "Error: " << e.what() << '\n';
            return 1;
        }
    } else if (cmd == "list" || cmd == "ls") {
        try {
            const auto disks = listMountedRamDisks();
            if (disks.empty()) {
                std::cout << "No ramdisks found.\n";
                return 0;
            }
            std::cout << std::left
                      << std::setw(24) << "DEVICE"
                      << "MOUNT POINT\n";
            std::cout << std::string(24, '-') << ' '
                      << std::string(40, '-') << '\n';
            for (const auto& d : disks) {
                std::cout << std::left
                          << std::setw(24) << d.device
                          << d.mountPoint << '\n';
            }
            std::cout << "\n" << disks.size() << " ramdisk(s)\n";
        } catch (const std::exception& e) {
            std::cerr << "Error: " << e.what() << '\n';
            return 1;
        }
    } else if (cmd == "umount" || cmd == "eject") {
        if (argc < 3) {
            usage(argv[0]);
            return 1;
        }
        if (umount(argv[2])) {
            std::cout << "Unmounted " << argv[2] << '\n';
        } else {
            std::cerr << "Failed to unmount " << argv[2] << '\n';
            return 1;
        }
    } else {
        usage(argv[0]);
        return 1;
    }

    return 0;
}
