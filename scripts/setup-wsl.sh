#!/bin/bash
# Homestead WSL setup — run INSIDE Ubuntu on WSL2, not on Windows.
# Usage: ./scripts/setup-wsl.sh
# Installs: kernel K0 toolchain + Buildroot ISO prereqs, clones repo to ~/Theia.
set -euo pipefail

sudo apt update
sudo apt install -y git make gcc g++ nasm bc bison flex libncurses-dev \
  libssl-dev cpio unzip rsync wget cdrkit xorriso qemu-system-x86 qemu-utils \
  grub-pc-bin grub-efi-amd64-bin mtools dosfstools

if [ ! -d "$HOME/Theia" ]; then
  git clone https://github.com/Adithya0765/Theia.git "$HOME/Theia"
fi

chmod +x "$HOME/Theia/os/build.sh" "$HOME/Theia/os/kernel/build-kernel.sh" 2>/dev/null || true
echo "OK. Next: cd ~/Theia && ./os/kernel/build-kernel.sh"
