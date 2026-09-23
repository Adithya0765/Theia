# Milestone 0 — base distro evaluation (PRD §§5.1, 6/M0)

Recommendation (to validate with throwaway builds on a Linux host):
**image-based/atomic, Fedora-derived (OSTree / rpm-ostree or equivalent).**

| Option | Atomic update/rollback | Package ecosystem | Build tooling | Fit for Pillars A/C |
|---|---|---|---|---|
| Arch base (archiso) | No (add Snapper/btrfs manually) | Excellent (pacman+AUR) | Good, but QA burden on us | Weak — mutable base fights the immutable-core/mutable-overlay split |
| Debian base (debootstrap/live-build) | No (same caveat) | Excellent, stable | Mature, well-understood | Weak — same as Arch |
| **Fedora atomic / OSTree-style** | **Yes, out of the box** | Good (rpm-ostree + Flatpak) | Good (osbuild/bootc maturing) | **Strong — base image + user overlay is exactly the Pillar A/C split** |

Why atomic wins for this thesis:

- "Opinionated core, malleable layer" (Pillar C) maps onto immutable base +
  user overlay directly.
- Reliable rollback is a safety net that encourages experimentation, which
  feeds Pillar A (users try automations/layouts without fear).
- System/app split falls out naturally: base image via atomic updates,
  apps via Flatpak, CLI tools via a thin native layer (PRD §5.1).

Risks (PRD §7): the atomic ecosystem is still maturing — validate before
committing. Throwaway spikes on a Linux host:

1. Build minimal OSTree image, daily-drive 1 week, exercise rollback.
2. Confirm Flatpak covers the 3–5 first-party-adjacent apps (files, terminal,
   editor, viewer) + settings surface needs.
3. Confirm DKMS/out-of-tree story for the hardware shortlist (no kernel fork).

Cannot run these spikes here (Windows host) — tracked as next action on Linux.
