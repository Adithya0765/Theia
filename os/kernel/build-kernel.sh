#!/bin/bash
# Homestead K0 builder — runs on the Kali LINUX host, not Windows.
# Usage: ./os/kernel/build-kernel.sh [--qemu]
# Output: output-homestead-kernel/homestead-kernel.iso ; --qemu boots it.
set -euo pipefail

KDIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$KDIR/../.." && pwd)"
OUT="$ROOT/output-homestead-kernel"
LIMINE_VER="7.12.0"
CACHE="$ROOT/.cache/limine-$LIMINE_VER"

mkdir -p "$OUT" "$ROOT/.cache"
if [ ! -d "$CACHE" ]; then
  echo "[k0] fetching Limine $LIMINE_VER..."
  wget -qO "$ROOT/.cache/limine.tar.gz" \
    "https://github.com/limine-bootloader/limine/releases/download/v$LIMINE_VER/limine-$LIMINE_VER.tar.gz"
  mkdir -p "$CACHE" && tar -xzf "$ROOT/.cache/limine.tar.gz" -C "$CACHE" --strip-components=1
fi

for tool in gcc nasm ld xorriso qemu-system-x86_64; do
  command -v "$tool" >/dev/null 2>&1 || {
    echo "missing: $tool — sudo apt install -y gcc nasm xorriso qemu-system-x86" >&2
    exit 1
  }
done

echo "[k0] compiling..."
LIMINE_H="$(find "$CACHE" -name 'limine.h' | head -1)"
[ -n "$LIMINE_H" ] || { echo "limine.h not found under $CACHE" >&2; exit 1; }
cp "$LIMINE_H" "$KDIR/limine.h"
cc -c "$KDIR/kernel.c" -o "$OUT/kernel.o" -std=gnu11 -ffreestanding \
  -fno-stack-protector -fno-stack-check -fno-lto -fno-pie -fno-pic \
  -m64 -march=x86-64 -mno-80387 -mno-mmx -mno-sse -mno-sse2 -mno-red-zone \
  -mcmodel=kernel -Wall -Wextra
nasm -f elf64 "$KDIR/boot.s" -o "$OUT/boot.o"
ld -T "$KDIR/linker.ld" -o "$OUT/homestead.elf" "$OUT/boot.o" "$OUT/kernel.o"

echo "[k0] building ISO..."
rm -rf "$OUT/iso" && mkdir -p "$OUT/iso/boot/limine" "$OUT/iso/boot"
cp "$OUT/homestead.elf" "$OUT/iso/boot/"
cp "$KDIR/limine.cfg" "$OUT/iso/boot/limine/"
for f in limine-bios.sys limine-bios-cd.bin limine-uefi-cd.bin; do
  src="$(find "$CACHE" -name "$f" | head -1)"
  [ -n "$src" ] || { echo "$f not found under $CACHE" >&2; exit 1; }
  cp "$src" "$OUT/iso/boot/limine/"
done
LIMINE_BIN="$(find "$CACHE" -type f -name 'limine' -executable | head -1)"
[ -n "$LIMINE_BIN" ] || LIMINE_BIN="$(find "$CACHE" -type f -name 'limine' | head -1)"
[ -n "$LIMINE_BIN" ] || { echo "limine deploy binary not found under $CACHE" >&2; exit 1; }
xorriso -as mkisofs -R -r -J -b boot/limine/limine-bios-cd.bin \
  -no-emul-boot -boot-load-size 4 -boot-info-table -hfsplus \
  --efi-boot boot/limine/limine-uefi-cd.bin -efi-boot-part \
  --efi-boot-image --protective-msdos-label \
  "$OUT/iso" -o "$OUT/homestead-kernel.iso" 2>/dev/null
chmod +x "$LIMINE_BIN"
"$LIMINE_BIN" bios-install "$OUT/homestead-kernel.iso" 2>/dev/null
ls -lh "$OUT/homestead-kernel.iso"

if [ "${1:-}" = "--qemu" ]; then
  qemu-system-x86_64 -m 512 -cdrom "$OUT/homestead-kernel.iso" -boot d
fi
