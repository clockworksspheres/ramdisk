# Top-level convenience Makefile for the ramdisk C++ project.
# All real work is done by CMake inside $(BUILDDIR).

BUILDDIR  ?= build
CMAKE     ?= cmake
BUILDTYPE ?= Release

.PHONY: all configure build clean distclean rebuild examples install help check-deps

all: build

check-deps:
	@command -v $(CMAKE) >/dev/null 2>&1 || { \
		echo ""; \
		echo "ERROR: '$(CMAKE)' not found."; \
		echo ""; \
		echo "Install build dependencies:"; \
		echo "  Debian/Ubuntu:  sudo apt update && sudo apt install -y build-essential cmake"; \
		echo "  Fedora:         sudo dnf install -y gcc-c++ cmake make"; \
		echo "  macOS:          xcode-select --install"; \
		echo "                  brew install cmake   # if needed"; \
		echo ""; \
		exit 127; \
	}
	@command -v c++ >/dev/null 2>&1 || command -v g++ >/dev/null 2>&1 || command -v clang++ >/dev/null 2>&1 || { \
		echo "ERROR: No C++ compiler found (c++/g++/clang++)."; \
		echo "  Debian/Ubuntu:  sudo apt install -y build-essential"; \
		echo "  macOS:          xcode-select --install"; \
		exit 127; \
	}

# Set GUI=OFF to skip Qt GUI:  make GUI=OFF
GUI ?= ON

configure: check-deps
	@mkdir -p $(BUILDDIR)
	$(CMAKE) -S . -B $(BUILDDIR) \
		-DCMAKE_BUILD_TYPE=$(BUILDTYPE) \
		-DRAMDISK_BUILD_EXAMPLES=ON \
		-DRAMDISK_BUILD_GUI=$(GUI)

build: configure
	$(CMAKE) --build $(BUILDDIR)

examples: build

clean:
	@if [ -d $(BUILDDIR) ]; then \
		$(CMAKE) --build $(BUILDDIR) --target clean; \
	else \
		echo "Nothing to clean (no $(BUILDDIR)/ directory)."; \
	fi

distclean:
	rm -rf $(BUILDDIR)
	@echo "Removed $(BUILDDIR)/"

rebuild: distclean build

install: build
	$(CMAKE) --install $(BUILDDIR)

help:
	@echo "Targets:"
	@echo "  make / make all   - configure (if needed) and build"
	@echo "  make configure    - run CMake only"
	@echo "  make build        - build in $(BUILDDIR)/"
	@echo "  make clean        - remove object files / binaries (keep CMake cache)"
	@echo "  make distclean    - delete entire $(BUILDDIR)/ directory"
	@echo "  make rebuild      - distclean + build"
	@echo "  make install      - install library and headers"
	@echo "  make check-deps   - verify cmake and a C++ compiler are installed"
	@echo ""
	@echo "Variables: BUILDDIR=$(BUILDDIR) BUILDTYPE=$(BUILDTYPE) GUI=$(GUI)"
	@echo ""
	@echo "Dependencies:"
	@echo "  Debian/Ubuntu:  sudo apt install -y build-essential cmake qt6-base-dev"
	@echo "  macOS:          xcode-select --install && brew install cmake qt"
