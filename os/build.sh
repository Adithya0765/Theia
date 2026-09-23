#!/bin/bash
# Homestead OS image builder — stage 0 (VirtualBox ISO).
# Runs on a LINUX host (Kali/Debian/Ubuntu). Not on Windows.
# Usage: ./os/build.sh [virtualbox]
set -euo pipefail

BOARD="${1:-virtualbox}"
OS_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$OS_DIR/.." && pwd)"
BR_VERSION="2024.02.9"
BR_DIR="$ROOT/.cache/buildroot-$BR_VERSION"
DEFCONFIG="$OS_DIR/buildroot/board/homestead/$BOARD/defconfig"
OVERLAY="$OS_DIR/overlay"
OUT="$ROOT/output"

if [ ! -f "$DEFCONFIG" ]; then
  echo "unknown board: $BOARD (missing $DEFCONFIG)" >&2
  exit 1
fi

mkdir -p "$ROOT/.cache" "$OUT"
if [ ! -d "$BR_DIR" ]; then
  echo "[homestead] fetching Buildroot $BR_VERSION..."
  wget -qO- "https://buildroot.org/downloads/buildroot-$BR_VERSION.tar.gz" \
    | tar -xz -C "$ROOT/.cache"
fi

echo "[homestead] configuring for $BOARD..."
make -C "$BR_DIR" \
  BR2_EXTERNAL="$OS_DIR/buildroot" \
  "homestead_${BOARD}_defconfig"

echo "[homestead] building (grab coffee, first run is long)..."
make -C "$BR_DIR" -j"$(nproc)"

echo "[homestead] collecting artefacts..."
cp -v "$BR_DIR/output/images/bzImage" "$OUT/" 2>/dev/null || true
cp -v "$BR_DIR/output/images/rootfs.squashfs" "$OUT/" 2>/dev/null || true
cp -v "$BR_DIR/output/images/rootfs.iso9660" "$OUT/homestead.iso" 2>/dev/null || true
ls -lh "$OUT/"
echo "[homestead] done. Boot homestead.iso in VirtualBox (see os/iso/VBOX-TEST.md)."
