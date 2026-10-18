/**
 * Basic usage example – mirrors the Python library interface.
 */

#include "ramdisk/RamDisk.hpp"
#include "ramdisk/Logger.hpp"
#include <iostream>
#include <fstream>
#include <filesystem>

int main() {
    using namespace ramdisk;

    Logger::instance().setLevel(LogLevel::DEBUG);

    try {
        // Create a 256 MB ramdisk at a temporary location
        auto disk = createRamDisk(256);

        if (!disk->success()) {
            std::cerr << "Failed to create ramdisk\n";
            return 1;
        }

        auto [ok, mnt, dev] = disk->getNprintData();
        std::cout << "\nRamdisk ready.\n";

        // Write a test file
        std::filesystem::path testFile = std::filesystem::path(mnt) / "hello.txt";
        {
            std::ofstream out(testFile);
            out << "Hello from C++ ramdisk!\n";
        }
        std::cout << "Wrote " << testFile << '\n';

        // Read it back
        std::ifstream in(testFile);
        std::string line;
        std::getline(in, line);
        std::cout << "Read back: " << line << '\n';

        // Explicit unmount (also happens in destructor)
        if (disk->umount()) {
            std::cout << "Unmounted successfully\n";
        }

    } catch (const RamDiskError& e) {
        std::cerr << "RamDisk error: " << e.what() << '\n';
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << '\n';
        return 1;
    }

    return 0;
}