# Hardware shortlist v1 (PRD §§5.6, 6/M0)

Deliberately narrow: trade reach for quality (not chasing install-count in v1).

Criteria: excellent upstream Linux support, no kernel fork, DKMS-able quirks
only, good power-management story, readily available for dogfooders.

| Device | Why |
|---|---|
| Framework Laptop 13 (AMD or Intel 13th-gen+) | Open firmware posture, first-class Linux support, easy to image/test |
| ThinkPad T14 / X1 Carbon Gen 11+ | Existing gold-standard Linux support, common dev-dogfood machine |
| (VM target) QEMU/KVM + virtio | CI + contributor onboarding without hardware |

Out of scope v1: NVIDIA-dGPU-only machines, exotic ARM, SecureBoot-strict
enterprise fleets (no MDM/domain join per PRD non-goals).

To confirm on Linux host: power tuning (PPD/TLP), Wi-Fi/BT firmware in
initramfs, fractional-scaling behavior under the wlroots session, Flatpak +
portal file access on each device.
