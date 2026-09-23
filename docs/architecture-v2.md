# Architecture v0.2 — ground-up userspace, kernel as driver HAL

Supersedes `architecture.md` §base-layer for the long-haul direction.
PRD v0.1 said "build on Fedora/Debian minimal". V0.2 says: **only the
kernel is borrowed; everything above it is ours.**

```
┌──────────────────────────────────────────────────┐
│ Homestead session (compositor, Index, daemons)   │  ours
│ Homestead toolkit + first-party apps             │  ours
│ Homestead services (init, svc supervision)       │  ours  <- os/init/
├──────────────────────────────────────────────────┤
│ Rootfs built from source (Buildroot external)    │  ours  <- os/buildroot/
│  busybox/musl→glibc, eudev, Mesa, libinput,      │
│  Wayland, Python runtime for homestead daemons   │
├──────────────────────────────────────────────────┤
│ Upstream LTS kernel + linux-firmware + Mesa      │  borrowed driver HAL
│  VirtualBox guest modules (vboxguest/vboxvideo)  │  v0 only
└──────────────────────────────────────────────────┘
```

## Why this split

- "Use all Linux drivers but be completely different" is only coherent as:
  **own the rootfs + init + session, borrow the kernel.** Drivers live in
  the kernel; firmware/Mesa/libinput are the minimum userspace to light them.
- Buildroot (not LFS-hand-rolled, not Yocto-heavy) because it is
  reproducible, emits a hybrid BIOS+EFI ISO VirtualBox boots natively, and
  an external tree keeps Homestead files cleanly separated from upstream.
- systemd is **out** in v0.2. PID 1 is `homestead-init` (shell in stage 0,
  small C supervisor later). Rationale: if every default is ours, the
  service model must express Pillar A/B (automation hooks, focus state) —
  systemd's unit model fights that. We keep the option to re-adopt runit/
  s6 idioms, but the supervisor is ours.

## Boot flow (VirtualBox first)

BIOS/EFI → isolinux/grub → `bzImage` + initramfs → squashfs root →
`/sbin/init` = homestead-init → mount proc/sys/dev, eudev coldplug →
`homestead-session` → compositor + ShortcutDaemon/Index/notifications →
login shell fallback (`/bin/sh` on tty1 for debug).

## Stages

| Stage | Boots to | Proves |
|---|---|---|
| 0 | busybox shell ISO in VirtualBox | kernel+firmware+ISO pipeline, all input/video/storage drivers |
| 1 | homestead-init + service supervision, no graphics | our PID 1 + overlay layout works |
| 2 | Wayland/wlroots session + consistency daemons | Pillar B alive on our own rootfs |
| 3 | personalization engine + disk installer | Pillar A alive, VBox → bare metal path |

`src/homestead/` (Python prototype) ships inside the image unchanged —
it is the session layer while the C/Rust shell matures.
