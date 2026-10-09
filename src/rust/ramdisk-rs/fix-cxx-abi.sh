#!/bin/sh
# Pin every cxx-related crate to the 1.0.186 / 0.7.186 ABI and rebuild the GUI.
set -e
cd "$(dirname "$0")"
export QMAKE="${QMAKE:-$(command -v qmake6 || command -v qmake)}"
echo "QMAKE=$QMAKE"

cargo update -p cxx --precise 1.0.186
cargo update -p cxx-gen --precise 0.7.186 2>/dev/null || true
cargo update -p cxxbridge-macro --precise 1.0.186 2>/dev/null || true
cargo update -p cxxbridge-flags --precise 1.0.186 2>/dev/null || true
cargo update -p cxxbridge-cmd --precise 1.0.186 2>/dev/null || true
cargo update -p cxx-build --precise 1.0.186 2>/dev/null || true

echo "=== cxx versions in tree ==="
cargo tree -i cxx -p ramdisk-gui 2>/dev/null || cargo tree -i cxx
echo "=== cxx-gen ==="
cargo tree -i cxx-gen -p ramdisk-gui 2>/dev/null || true

cargo clean -p ramdisk-gui
cargo run -p ramdisk-gui
