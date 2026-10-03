cmake_minimum_required(VERSION 3.16)
project(ramdisk VERSION 2.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

option(RAMDISK_BUILD_EXAMPLES "Build example programs" ON)
option(RAMDISK_BUILD_SHARED   "Build shared library"   OFF)
option(RAMDISK_BUILD_GUI      "Build Qt 6 GUI (ramdisk_gui)" ON)

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
# Qt 6 GUI (port of Python PySide6 ramdisk-setup / ui/main.py)
# -----------------------------------------------------------------------------
if(RAMDISK_BUILD_GUI)
    set(CMAKE_AUTOMOC ON)
    set(CMAKE_AUTOUIC ON)
    set(CMAKE_AUTORCC ON)
    set(CMAKE_AUTOUIC_SEARCH_PATHS ${CMAKE_CURRENT_SOURCE_DIR}/ui)

    find_package(Qt6 QUIET COMPONENTS Widgets)
    if(Qt6_FOUND)
        add_executable(ramdisk_gui
            src/gui/main_gui.cpp
            src/gui/CreateRamdiskWindow.cpp
            src/gui/CreateRamdiskWindow.hpp
            ui/mainwindow.ui
        )
        target_include_directories(ramdisk_gui PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/src/gui
            ${CMAKE_CURRENT_BINARY_DIR}   # for ui_mainwindow.h
        )
        target_link_libraries(ramdisk_gui PRIVATE ramdisk Qt6::Widgets)
        message(STATUS "Qt6 found — building ramdisk_gui")
    else()
        message(WARNING "Qt6 Widgets not found — skipping ramdisk_gui. "
                        "Install qt6-base-dev (Linux) or brew install qt (macOS). "
                        "Or configure with -DRAMDISK_BUILD_GUI=OFF")
    endif()
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