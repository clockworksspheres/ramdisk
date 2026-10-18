# Cross-platform convenience Makefile for the ramdisk C++ project.
# Works with GNU Make on Linux, macOS, and Windows (MinGW / Chocolatey make).
# All real work is done by CMake inside $(BUILDDIR).

BUILDDIR  ?= build
CMAKE     ?= cmake
BUILDTYPE ?= Release
# Set GUI=OFF to skip Qt GUI:  make GUI=OFF
GUI       ?= ON

.PHONY: all configure build clean distclean rebuild examples install help check-deps

all: build

# ---------------------------------------------------------------------------
# Dependency check (cmd.exe-safe on Windows; sh-safe on Unix)
# ---------------------------------------------------------------------------
check-deps:
	@$(CMAKE) -E echo "Checking for cmake..."
	@$(CMAKE) --version >$(BUILDDIR)_cmake_check.tmp 2>&1 || ( \
		$(CMAKE) -E echo "" && \
		$(CMAKE) -E echo "ERROR: '$(CMAKE)' not found." && \
		$(CMAKE) -E echo "" && \
		$(CMAKE) -E echo "Install build dependencies:" && \
		$(CMAKE) -E echo "  Windows:  winget install Kitware.CMake  OR  choco install cmake" && \
		$(CMAKE) -E echo "            Install Visual Studio Build Tools with C++ workload" && \
		$(CMAKE) -E echo "  Debian/Ubuntu:  sudo apt install -y build-essential cmake" && \
		$(CMAKE) -E echo "  macOS:          xcode-select --install && brew install cmake" && \
		$(CMAKE) -E echo "" && \
		exit 1 \
	)
	@$(CMAKE) -E rm -f $(BUILDDIR)_cmake_check.tmp
	@$(CMAKE) -E echo "cmake OK"

configure: check-deps
	@$(CMAKE) -E make_directory $(BUILDDIR)
	$(CMAKE) -S . -B $(BUILDDIR) \
		-DCMAKE_BUILD_TYPE=$(BUILDTYPE) \
		-DRAMDISK_BUILD_EXAMPLES=ON \
		-DRAMDISK_BUILD_GUI=$(GUI)

build: configure
	$(CMAKE) --build $(BUILDDIR) --config $(BUILDTYPE)

examples: build

clean:
	@$(CMAKE) -E echo "Cleaning $(BUILDDIR)..."
	-@$(CMAKE) --build $(BUILDDIR) --config $(BUILDTYPE) --target clean

distclean:
	@$(CMAKE) -E echo "Removing $(BUILDDIR)/"
	@$(CMAKE) -E rm -rf $(BUILDDIR)

rebuild: distclean build

install: build
	$(CMAKE) --install $(BUILDDIR) --config $(BUILDTYPE)

help:
	@$(CMAKE) -E echo "Targets:"
	@$(CMAKE) -E echo "  make / make all   - configure (if needed) and build"
	@$(CMAKE) -E echo "  make configure    - run CMake only"
	@$(CMAKE) -E echo "  make build        - build in $(BUILDDIR)/"
	@$(CMAKE) -E echo "  make clean        - remove object files / binaries (keep CMake cache)"
	@$(CMAKE) -E echo "  make distclean    - delete entire $(BUILDDIR)/ directory"
	@$(CMAKE) -E echo "  make rebuild      - distclean + build"
	@$(CMAKE) -E echo "  make install      - install library and headers"
	@$(CMAKE) -E echo ""
	@$(CMAKE) -E echo "Variables: BUILDDIR=$(BUILDDIR) BUILDTYPE=$(BUILDTYPE) GUI=$(GUI)"
	@$(CMAKE) -E echo ""
	@$(CMAKE) -E echo "Windows notes:"
	@$(CMAKE) -E echo "  Prefer:  .\build.ps1"
	@$(CMAKE) -E echo "  Or:      cmake -S . -B build && cmake --build build --config Release"
	@$(CMAKE) -E echo "  Install: winget install Kitware.CMake"
	@$(CMAKE) -E echo ""
	@$(CMAKE) -E echo "Dependencies:"
	@$(CMAKE) -E echo "  Windows:  Visual Studio 2019+ (C++) and CMake"
	@$(CMAKE) -E echo "  Debian:   sudo apt install -y build-essential cmake qt6-base-dev"
	@$(CMAKE) -E echo "  macOS:    xcode-select --install && brew install cmake qt"
