# Architecture — Homestead OS (PRD §5)

Split: **immutable base + mutable personal overlay**.

```
┌─────────────────────────────────────────────┐
│ First-party apps (toolkit, intent contract) │
├─────────────────────────────────────────────┤
│ Consistency layer (§5.3)                    │
│  ShortcutDaemon │ Index │ NotificationDaemon│
├─────────────────────────────────────────────┤
│ Personalization layer (§5.4)                │
│  AutomationEngine │ PatternDetector         │
│  LayoutMemory │ Profile (portable)          │
├─────────────────────────────────────────────┤
│ Transparency layer (§5.5): TransparencyLog  │
├─────────────────────────────────────────────┤
│ Session/shell on wlroots + Wayland (§5.2)   │
├─────────────────────────────────────────────┤
│ Atomic base image (OSTree-style) + Flatpak  │
│ systemd │ LTS kernel, no fork (§5.1, §5.6)  │
└─────────────────────────────────────────────┘
```

Design rules (from PRD pillars):

1. **Pillar B before Pillar A.** Consistency daemons are platform services
   below apps, not extensions. Apps declare intents; they never own keybindings.
2. **Learning is local-first.** `PatternDetector`, `LayoutMemory`, usage boosts
   in `Index` never leave the device. Profile export is explicit user action.
3. **Every automation is visible + undoable.** Engine dispatches, but
   `TransparencyLog.record(..., reason, undo)` is the only path the shell
   uses to apply system effects.
4. **Profile is the compounding artifact.** Shortcuts + rules + layouts +
   prefs serialize to versioned JSON (`profile/store.py`), surviving reinstalls.

Prototype map (`src/homestead/`):

| PRD | Module |
|---|---|
| 5.3 shortcut daemon | `shortcuts/daemon.py` |
| 5.3 The Index | `index/index.py` |
| 5.3 notifications/focus | `notifications/daemon.py` |
| 5.4 explicit automation (M3) | `automation/engine.py` |
| 5.4 suggested automation (M4) | `automation/suggest.py` |
| 5.4 layout memory | `layout/memory.py` |
| 5.4 portable profile | `profile/store.py` |
| 5.5 transparency | `transparency/log.py` |

OS-image work (M0 base eval, M1 bootable image, wlroots session) requires a
Linux build host — see `docs/milestone-0-*.md`. This repo builds the
userspace thesis first because it is the riskiest part (PRD §7).
