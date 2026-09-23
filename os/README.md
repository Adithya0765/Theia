# Homestead OS tree — `os/`

Ground-up build: upstream kernel (driver HAL) + Buildroot-built custom
rootfs + `homestead-init`. Produces a VirtualBox-bootable ISO, then a
disk installer later. All build steps run on a **Linux host** (your Kali
VM works for stage 0; a Debian/Ubuntu VM is cleaner long-term).

```
os/
  README.md            <- you are here (build order)
  build.sh             <- one-shot: fetch Buildroot LTS, build, emit ISO
  buildroot/
    external.desc      <- Buildroot external tree identity
    Config.in          <- our packages (homestead-session, daemons)
    board/homestead/virtualbox/
      defconfig        <- minimal VBox target (x86-64, EFI+BISO, gfx+net)
      grub.cfg         <- boot entries (live + debug shell)
      kernel.config.fragment  <- VIRTIO/VBOX/MESA essentials, no fork
  overlay/             <- rootfs overlay (etc/hostname, fstab, profile)
  init/
    homestead-init     <- stage-0/1 PID 1 (POSIX sh, then C rewrite)
    homestead-session  <- starts daemons -> compositor -> shell
  iso/
    VBOX-TEST.md       <- VirtualBox bring-up checklist
```

## Build order (Linux host)

```bash
# 0. prereqs (Debian/Kali host)
sudo apt update && sudo apt install -y git make gcc g++ bc bison flex \
  libncurses-dev libssl-dev cpio unzip rsync wget cdrkit xorriso \
  qemu-utils grub-pc-bin grub-efi-amd64-bin mtools dosfstools

# 1. build (fetches Buildroot 2024.02 LTS, ~20-60 min first run)
./os/build.sh virtualbox

# 2. artefacts
ls output/images/   # bzImage, rootfs.squashfs, homestead.iso

# 3. boot in VirtualBox (or qemu for smoke test)
qemu-system-x86_64 -m 2048 -cdrom output/images/homestead.iso -boot d
```

Stage 0 success = shell prompt on tty1 + `lspci` shows VBox VGA/net +
`homestead-init` as PID 1. Then iterate toward stages 1-3 per
`docs/architecture-v2.md`.
