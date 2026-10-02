#pragma once

#include <string>
#include <cstdint>
#include <optional>

namespace ramdisk {

/** Create a unique temporary directory (like Python's tempfile.mkdtemp). */
std::string makeTempDir(const std::string& prefix = "ramdisk-");

/** Check whether enough free physical memory exists for sizeMb. */
bool isMemoryAvailable(std::uint64_t sizeMb);

/** Return free physical memory in megabytes. */
std::uint64_t freeMemoryMb();

/** Ensure a directory exists (creates parents if needed). */
bool ensureDirectory(const std::string& path);

/** Current effective user id (POSIX) or 0 on Windows. */
int currentUid();

/** Current effective group id (POSIX) or 0 on Windows. */
int currentGid();

/** Platform name helper. */
std::string platformName();

} // namespace ramdisk