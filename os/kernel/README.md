# Homestead kernel — own kernel, open-source drivers only

Direction v0.3: we own the kernel. Linux source is **reference**, not base:
no Linux code in-tree unless deliberately ported (a port makes this kernel
GPL-2.0 — that is the rule, know it before copying a single function).

## The scope rule that keeps this alive

"Drivers for 5 years of hardware" as stated would kill the project — Wi-Fi
(Intel `iwlwifi` + firmware + regulatory) and GPU acceleration (`i915`/Xe,
`amdgpu` command submission + power) are each multi-year projects alone.
Every hobby OS dies exactly there (see Redox, ~10 years in, still no
Wi-Fi/GPU-accel). So drivers come in phases:

| Phase | Hardware | Proves |
|---|---|---|
| K0 | Boot (Limine) + framebuffer + serial + interrupts + timer + PS/2 kbd | kernel exists, boots in QEMU/VirtualBox |
| K1 | PCI enum, AHCI/virtio-blk disk, FAT/ext2 read, rings, syscalls, scheduler | runs userspace programs from disk |
| K2 | virtio-net + lwIP port, virtio-gpu/framebuffer GUI, AHCI in VBox | self-hosted dev + graphical session in a VM |
| K3 | **ONE** physical laptop (TBD, open-friendly) — NVMe, xHCI, unaccelerated modeset, wired net | real metal, no accel, no Wi-Fi yet |
| K4+ | Wi-Fi, GPU accel, then widen the 5-year matrix | the long tail — years, honestly |

K0–K2 use only **virtual hardware with open specs** (virtio, AHCI, PS/2,
multiboot/Limine). No firmware blobs, no reverse-engineering. K3+ is where
the 5-year matrix begins, one machine at a time.

## Meanwhile (important)

The Linux-kernel Buildroot ISO (`os/`, v0.2 tree) stays alive as the
daily-drivable product surface while this kernel matures. Never strand
yourself without a bootable system: product on Linux kernel, research in
`os/kernel/`, merge the day K2 self-hosts.

## Language: C (locked)

C11 freestanding, `gcc` + `nasm`, Limine boot protocol. Rationale: Linux
driver logic ports almost line-for-line; no rewrite tax. Memory-safety
discipline via `-Wall -Wextra`, review, and small translation units —
not via language switch.

## K0 layout

```
os/kernel/
  README.md        <- you are here
  kernel.c         <- K0: framebuffer gradient proof-of-life
  boot.s           <- entry: call kmain, halt on return
  linker.ld        <- 1MB load, .requests kept for Limine
  limine.cfg       <- boot entries (normal + QEMU debug)
  build-kernel.sh  <- fetch pinned Limine, build ISO, run in QEMU (Kali host)
```

Validate in Kali: `./os/kernel/build-kernel.sh` → QEMU window with a
gradient = K0 done. Then VirtualBox boot of the same ISO.
