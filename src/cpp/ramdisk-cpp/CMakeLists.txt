cmake_minimum_required(VERSION 3.16)
project(ramdisk VERSION 2.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

option(RAMDISK_BUILD_EXAMPLES "Build example programs" ON)
option(RAMDISK_BUILD_SHARED   "Build shared library"   OFF)

# -----------------------------------------------------------------------------
# Library
# -----------------------------------------------------------------------------
set(RAMDISK_SOURCES
    src/common/RamDiskFactory.cpp
    src/common/Logger.cpp
    src/common/Process.cpp
    src/common/Utils.cpp
)

if(APPLE)
    list(APPEND RAMDISK_SOURCES src/macos/MacRamDisk.cpp)
elseif(UNIX AND NOT APPLE)
    list(APPEND RAMDISK_SOURCES src/linux/LinuxTmpfsRamDisk.cpp)
elseif(WIN32)
    list(APPEND RAMDISK_SOURCES src/windows/WinAIMRamDisk.cpp)
else()
    message(FATAL_ERROR "Unsupported platform")
endif()

if(RAMDISK_BUILD_SHARED)
    add_library(ramdisk SHARED ${RAMDISK_SOURCES})
else()
    add_library(ramdisk STATIC ${RAMDISK_SOURCES})
endif()

add_library(ramdisk::ramdisk ALIAS ramdisk)

target_include_directories(ramdisk
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
)

if(UNIX AND NOT APPLE)
    # Linux may need librt / pthread in some environments
    find_package(Threads REQUIRED)
    target_link_libraries(ramdisk PUBLIC Threads::Threads)
endif()

if(WIN32)
    target_compile_definitions(ramdisk PRIVATE _WIN32_WINNT=0x0601)
endif()

# -----------------------------------------------------------------------------
# Examples
# -----------------------------------------------------------------------------
if(RAMDISK_BUILD_EXAMPLES)
    add_executable(ramdisk_example examples/basic_example.cpp)
    target_link_libraries(ramdisk_example PRIVATE ramdisk)

    add_executable(ramdisk_cli examples/cli.cpp)
    target_link_libraries(ramdisk_cli PRIVATE ramdisk)
endif()

# -----------------------------------------------------------------------------
# Install
# -----------------------------------------------------------------------------
include(GNUInstallDirs)
install(TARGETS ramdisk
    EXPORT ramdiskTargets
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
install(DIRECTORY include/ DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})
install(EXPORT ramdiskTargets
    FILE ramdiskTargets.cmake
    NAMESPACE ramdisk::
    DESTINATION ${CMAKE_INSTALL_LIBDIR}/cmake/ramdisk
)