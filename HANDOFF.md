# HANDOFF — Homestead OS ("Theia" repo)

**Repo:** https://github.com/Adithya0765/Theia.git — branch `main`
**Date:** 2026-09-23 · **PRD:** v0.3 (`PRD.md`) · **Kernel language:** C (locked)
**Prototype tests:** 16/16 green (`PYTHONPATH=src python -m unittest discover -s tests -v`)

## What this is

Homestead OS: an OS that becomes yours through use. Product surface is a
Linux-kernel Buildroot ISO (v0.2 tree, boots in VirtualBox); parallel
research track is our **own C kernel** (`os/kernel/`, v0.3). Never strand
yourself without a bootable system — product on Linux kernel until K2
self-hosts.

## Decision log (don't relitigate without cause)

- v0.1: Fedora-atomic base + systemd → dropped (not "ours" enough).
- v0.2: upstream LTS kernel as driver HAL + Buildroot rootfs + own init.
  Still alive as the bootable product path (`os/`).
- v0.3: own kernel in C. Linux source is reference-only (ports ⇒ GPL-2.0).
  Driver scope is **virtual-hardware first** (virtio/AHCI/PS/2/framebuffer,
  K0–K2); ONE physical laptop at K3; Wi-Fi/GPU-accel last (years, honestly).
- C over Rust: Linux driver logic ports line-for-line, no rewrite tax.
- WSL2 path is **dead on this network** (`aka.ms` → 403, even for the WSL
  kernel). Build on Kali VM; boot ISOs in VirtualBox on Windows.
- Buildroot hates spaces in paths → inside any Linux env use `~/Theia`,
  never `/mnt/c/My Files/...`.

## Repo map

```
PRD.md                    v0.3 (own kernel; v0.2 ISO stays as product surface)
src/homestead/            consistency (shortcuts/Index/notifications) +
                          personalization (automation/suggest/layout/profile) +
                          transparency log — stdlib-only Python, 16 tests
tests/test_homestead.py
docs/                     architecture.md, architecture-v2.md, intent-schema.md,
                          milestone-0-*.md, hardware-shortlist.md,
                          windows-vbox-loop.md (Win↔Kali ISO handoff)
os/README.md + os/build.sh          v0.2 Buildroot VirtualBox ISO pipeline
os/buildroot/                       defconfig, kernel fragment, grub.cfg,
                                    homestead-session package (ships PID1 + Python)
os/init/                  homestead-init (PID 1), homestead-session
os/overlay/               hostname, fstab
os/iso/VBOX-TEST.md       VirtualBox bring-up checklist
os/kernel/                K0: kernel.c, boot.s, linker.ld, limine.cfg,
                          build-kernel.sh (pinned Limine 7.12.0)
scripts/                  new-homestead-vm.ps1 (Windows), setup-wsl.sh (dead path)
```

## Current state: K0 blocked on Limine fetch

**Symptom (Kali, `~/Theia`):** `./os/kernel/build-kernel.sh --qemu` aborts
with `EXIT: 8` at `[k0] fetching Limine 7.12.0 (binary)...`; `.cache/limine-bin.tar.gz`
is 0 bytes. wget exit 8 = server error (bad asset name or blocked host).
`kernel.c` itself compiles (only a harmless RWX-segment `ld` warning).

**History:** first fetched the *source* tarball by mistake (wrong `limine.h`
stub, 8 lines, `limine_load` declaration), then switched to `-binary` asset —
name unverified.

**Next command (run on Kali, paste output):**
```bash
curl -s https://api.github.com/repos/limine-bootloader/limine/releases/tags/v7.12.0 | grep browser_download_url
```
Then pin the exact binary filename in `os/kernel/build-kernel.sh`
(`LIMINE_VER` + URL), `git pull` equivalent, rerun. If the API also fails,
release downloads are network-blocked → mirror the tarball another way
(phone hotspot, direct browser download, or vendor a known-good copy).

## Environment (Kali VM)

- `~/Theia` is a clone of the repo; apt lists are fresh (`apt update` clean).
- Installed for K0: `gcc nasm xorriso qemu-system-x86` (+ earlier repair via
  `sudo dpkg --configure -a` after an interrupted install — resolved).
- Full Buildroot prereqs (for `os/build.sh` later): see `os/README.md`.
- Shell is `zsh`; scripts are `+x` in git (commit `521a087`) — if `git pull`
  ever aborts on "local changes" to scripts, it's mode-bit noise:
  `git checkout -- <files> && git pull`.

## Cheat sheet (Kali)

```bash
cd ~/Theia && git pull
PYTHONPATH=src python3 -m unittest discover -s tests -v   # prototype, 16 OK
./os/kernel/build-kernel.sh --qemu    # K0: expect QEMU gradient window
./os/build.sh virtualbox              # v0.2 product ISO (20–60 min first run)
qemu-system-x86_64 -m 2048 -cdrom output/homestead.iso -boot d
```

## After K0 boots

1. Copy `output-homestead-kernel/homestead-kernel.iso` to Windows
   (`docs/windows-vbox-loop.md`) and boot it in VirtualBox (proves real
   firmware path, not just QEMU).
2. K1 scaffold: GDT/IDT + serial logging + timer + PS/2 keyboard.
3. Language/toolchain stays: C11 freestanding, gcc+nasm, Limine protocol.
