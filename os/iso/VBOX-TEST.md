# VirtualBox bring-up checklist — stage 0

Target: `homestead.iso` boots to a shell with homestead-init as PID 1.

## VM settings (create once)

- Type Linux, Version 2.6/3.x/4.x (64-bit); 2048MB+ RAM; 8GB+ VDI (stage 3+)
- System → EFI: **enable** (we ship hybrid BIOS+EFI; test EFI first)
- Display → VMSVGA, 64MB+, 3D acceleration on
- Storage → IDE/SATA optical with `homestead.iso`
- Network → NAT (stage 0 only needs it for smoke tests)

## Smoke test (qemu, before slow VBox boot)

```bash
qemu-system-x86_64 -m 2048 -cdrom output/homestead.iso -boot d
```

## Pass criteria — stage 0

1. GRUB menu shows "Homestead (live)" + "Homestead (debug shell)"
2. Boots to `Homestead OS (stage 0)` banner, no kernel panic
3. `ps 1` (or `cat /proc/1/cmdline`) → homestead-init
4. `lspci` shows VGA + network; `ip link` shows an interface
5. `homestead-session` runs without error

## Triage

| Symptom | Likely cause |
|---|---|
| Black screen / no GRUB | EFI off + BIOS-only image, or bad hybrid ISO — check `build.sh` grub2 vars |
| Kernel panic: can't mount root | `root=/dev/sr0` wrong for your controller — try `root=/dev/sda`; check fragment has ISO9660+SQUASHFS |
| No network/video | Missing VIRTIO/VBOX fragment options — recheck `kernel.config.fragment` |
| Boots but no banner | `/sbin/init` symlink missing → ensure overlay/init installs to `/sbin/init` (stage-1 packaging task) |
