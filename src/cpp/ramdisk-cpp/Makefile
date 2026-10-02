# Top-level convenience Makefile for the ramdisk C++ project.
# All real work is done by CMake inside $(BUILDDIR).

BUILDDIR  ?= build
CMAKE     ?= cmake
BUILDTYPE ?= Release

.PHONY: all configure build clean distclean rebuild examples install help

all: build

configure:
	@mkdir -p $(BUILDDIR)
	$(CMAKE) -S . -B $(BUILDDIR) \
		-DCMAKE_BUILD_TYPE=$(BUILDTYPE) \
		-DRAMDISK_BUILD_EXAMPLES=ON

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
	@echo ""
	@echo "Variables: BUILDDIR=$(BUILDDIR) BUILDTYPE=$(BUILDTYPE)"
