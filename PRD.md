# Product Requirements Document
## [Working Name: "Homestead OS"] — A Linux-Based Desktop OS Built for Attachment

**Status:** Draft v0.2 (ground-up direction — supersedes v0.1 base-distro plan)
**Owner:** [You]
**Last updated:** 2026-09-23

> v0.2 direction change: no Debian/Fedora base, no systemd. Upstream LTS
> kernel is borrowed as the driver HAL; everything above it (rootfs via
> Buildroot, `homestead-init`, session, toolkit) is Homestead-owned.
> See `docs/architecture-v2.md` and `os/`. VirtualBox ISO first, then disk
> installer, then bare metal.

> Naming note: "Homestead" is a placeholder capturing the thesis (you build a home in it, it's yours). Replace freely — see Open Questions.

---

## 1. Problem Statement

Linux desktop distributions are technically capable but fail to create lasting user attachment. The typical lifecycle looks like this:

1. A user distro-hops, excited by a new DE (desktop environment) or aesthetic.
2. Within hours or days, they hit friction: inconsistent app behavior, scattered settings, notification chaos, fragile window management, search that doesn't search everything.
3. They either (a) sink days into manual configuration (dotfiles, WM configs, theming) to make it tolerable, or (b) give up and hop to the next distro — or back to macOS/Windows.
4. Even users who *do* configure it deeply are attached to **their own dotfiles**, not to the distro itself — the distro is a disposable substrate.

Meanwhile, the OSes people *do* stay attached to (a heavily customized vim/Emacs setup, a tiling WM config perfected over years, an Anki deck, a Roam/Obsidian vault) share a pattern: **the system compounds in value the longer you use it, in a way that isn't trivially portable, and the investment was low-friction to make.**

No mainstream desktop OS — Linux, macOS, or Windows — is designed around this compounding-investment principle. They're designed around out-of-box polish (macOS), raw configurability with no guardrails (Linux), or legacy inertia (Windows).

**The opportunity:** build a Linux-based desktop OS whose core design principle is *user attachment through compounding personalization*, wrapped in enough out-of-box coherence that day one doesn't feel like homework.

---

## 2. Vision & Thesis

> **An OS that becomes yours — not through raw configurability, but through use.**

Three pillars, in priority order:

### Pillar A — Compounding Personalization
The system should get measurably better *for this specific user* the longer they use it, through low-friction mechanisms (not "edit a config file"). This creates switching cost that is a *feature*, not a dark pattern — the user isn't locked in by DRM, they're invested because they built something.

### Pillar B — Ruthless Consistency
One interaction model, one settings surface, one search surface, one notification model — enforced across first-party apps and strongly encouraged (via toolkit/guidelines) for third-party apps. The single biggest unfixed complaint about Linux desktops is inconsistency between GTK/Qt/Electron apps. We fix this at the platform level, not by asking app developers nicely.

### Pillar C — Opinionated Defaults, Total Malleability
Day one should feel considered and complete — not a blank tiling WM with no config. Day 100 should feel hand-built. The system ships with strong defaults but every default is a starting point the personalization layer can override, gradually, based on real usage — not a wall the user has to climb to start customizing.

**Explicit non-goals for v1:**
- Not a phone OS (desktop/laptop only, per scope decision)
- Not chasing raw distro-hopper feature parity (gaming performance tuning, exotic hardware support) — those come later if at all
- Not a fork-and-theme of an existing DE (GNOME/KDE) — the consistency and personalization layers require deeper integration than theming allows
- Not initially targeting enterprise/IT-managed fleets (no MDM, no domain join, etc. in v1)

---

## 3. Target User

**Primary persona: "The Configurer"** — technically comfortable (can use a terminal, has opinions about their tools), currently on Linux, macOS, or a Linux distro-hopper, who has spent real hours customizing past systems and been frustrated that the investment didn't compound or didn't survive a reinstall/distro-hop.

**Secondary persona: "The Refugee"** — coming from macOS/Windows, technically capable but not necessarily a tinkerer, drawn by the promise of an OS that adapts to them without demanding config-file archaeology.

Not targeting (v1): non-technical mainstream users who need Windows-level app/driver compatibility out of the gate; enterprise IT.

---

## 4. Success Metrics

Since "attachment" is the core thesis, standard OS metrics (install count) are secondary to retention/engagement metrics:

| Metric | Why it matters |
|---|---|
| **D30/D90 retention** (still primary OS, not dual-boot abandoned) | Direct measure of attachment vs. novelty |
| **Personalization depth over time** (# of learned/adapted behaviors, automations created, per user, tracked over weeks) | Proxy for "compounding investment" actually happening |
| **Time-to-first-friction** (how long until a user hits an unresolved inconsistency/bug) | Proxy for Pillar B success |
| **Backup/restore of personalization state used** | Signals users treat their personalization as valuable, worth preserving |
| **Qualitative: would-recommend / "I'd be annoyed to lose this" survey** | Direct attachment signal |

Explicitly **not** optimizing for in v1: raw install base, hardware compatibility breadth, app store size.

---

## 5. System Architecture

### 5.1 Base Layer

- **Kernel:** Upstream Linux (LTS releases), unmodified except for a small, upstreamable-where-possible patch set (see 5.6). Do not fork the kernel. Reinventing the kernel is a multi-decade tarpit and contributes nothing to the thesis.
- **Base distro:** Build on an existing minimal, well-maintained base rather than from scratch. Realistic options, to evaluate in Milestone 0:
  - **Arch base** (via archiso-style tooling) — rolling release, huge package availability via AUR/pacman, but stability/QA burden falls on you.
  - **Debian base** — stability, huge package ecosystem, slower-moving, well-understood image-building tooling (debootstrap, live-build).
  - **Fedora Silverblue/atomic-style base (OSTree)** — image-based, atomic updates/rollback out of the box, immutable root — appealing given Pillar C (opinionated core, malleable layer) maps naturally onto **immutable base OS + mutable overlay**.
  - **Recommendation to validate in Milestone 0:** an **image-based/atomic (OSTree-style) approach**, likely Fedora-derived, because "immutable, reliable base + user overlay that compounds" is architecturally exactly the Pillar A/C split. This also gives reliable rollback (safety net encourages experimentation, which feeds Pillar A).
- **Init system:** systemd (de facto standard; not worth fighting).
- **Package management:** Two-tier —
  - System/base packages: managed via the atomic image update mechanism (rpm-ostree or equivalent), not mutated live.
  - User/app packages: Flatpak as primary app distribution format (sandboxing, desktop-agnostic, already solves a lot of the "every app looks/behaves differently" problem at the packaging level) + a thin native package layer for CLI tools/dev tooling.

### 5.2 Display & Windowing

- **Display protocol:** Wayland only. X11 is legacy; building new consistency guarantees on top of X11's permissive model works against Pillar B. Accept the compatibility cost (XWayland for legacy apps).
- **Compositor:** Custom compositor, likely built on **wlroots** (used by Sway, Hyprland, etc.) rather than from scratch. wlroots gives a mature Wayland protocol implementation; your differentiation is in the shell/session layer built on top, not in re-implementing Wayland internals.
- **Window management model:** This needs real product decision-making (see Open Questions) — options range from a refined tiling model (opinionated, fast, but a learning curve that cuts against "Refugee" persona) to a hybrid floating+tiling model with adaptive layout suggestions (fits Pillar A — the system learns your window arrangement patterns per-app/per-workspace and suggests/automates them).

### 5.3 The Consistency Layer (Pillar B)

This is the most architecturally distinctive part of the system and needs to exist **below** individual apps, not as a theming convention:

- **Unified input/shortcut daemon:** A system-level service that owns global keybinding registration. Apps declare intents ("open command palette", "close window", "next tab") against a standard schema; the daemon maps physical keys to intents, centrally, user-remappable in one place — not per-app config files.
- **Unified settings & search surface ("The Index"):** One searchable, spotlight-like surface that indexes: installed apps, system settings, files (via a background indexer), running processes/windows, user-defined automations, and shortcut bindings. Every "where is this setting" question is answered by one interface, not five.
- **Unified notification & focus model:** One notification daemon, one set of rules for interruption vs. silent logging, integrated with a system-wide focus/DND state that apps can query.
- **Design system requirement:** A first-party toolkit (likely GTK4/libadwaita-based, given Flatpak/GNOME ecosystem maturity, or a custom thin toolkit) that first-party apps use, plus published guidelines + a "certified consistent" badge/incentive for third-party apps that adopt the shortcut/notification/settings conventions.

### 5.4 The Personalization & Automation Layer (Pillar A)

This is the core differentiator and the riskiest/most novel part of the system:

- **System-wide automation engine:** A native equivalent of macOS Shortcuts + Hazel + AppleScript, but designed to be *unobtrusively learnable* rather than requiring users to seek it out:
  - **Explicit automations:** user-authored rules ("when I connect this monitor, arrange these apps this way"; "when I open this file type from Downloads, move it here").
  - **Suggested automations:** the system observes repeated manual patterns (same 3 actions done together repeatedly) and *proposes* turning them into a one-click automation — this is the actual compounding mechanism, and it must be low-friction (a subtle suggestion, not a nag) or it undermines trust.
- **Adaptive layout/workflow memory:** window arrangements, workspace setups, and app placements are remembered per context (per monitor config, per time of day, per detected "mode" like focus/meeting/idle) and restored automatically, with the system's confidence in the pattern increasing over time.
- **Personalization state as a first-class, portable object:** critically, this state must be exportable/syncable/versionable — the antithesis of dotfile fragility. A "personalization profile" (automations, learned patterns, shortcut remaps, layout memory) should survive reinstalls and ideally be diffable/shareable (this also creates a natural community/sharing loop later — "install someone's workflow profile").
- **Privacy/local-first requirement:** all learning/adaptation happens on-device by default. No behavioral data leaves the machine without explicit, granular opt-in. This is both an ethical requirement and a trust requirement — Pillar A only works if users trust the system enough to let it observe them.

### 5.5 Transparency Layer

Even though this wasn't in the original three pillars explicitly, it was in your "things other OSes get wrong" framing and directly supports trust in Pillar A (users need to trust the system enough to let it learn from them):

- Human-readable system activity view: what's running, what's using resources, what has network access and when, presented in plain language with drill-down to raw data — not a wall of `journalctl` output.
- Every background automation/adaptation the system makes is logged in a visible, undoable timeline ("the system rearranged these windows because X — undo / always / never").

### 5.6 Kernel/Driver Considerations

- No kernel forking. Any hardware-specific needs (e.g., better power management tuning, specific laptop quirks) should go through DKMS-style out-of-tree modules or, ideally, upstream contribution — not a maintained fork.
- Hardware support scope for v1 should be deliberately narrow: target a short list of known-good laptops (e.g., a couple of ThinkPad/Framework models with excellent existing Linux support) rather than promising broad compatibility. This is a scope decision that trades reach for quality — consistent with not chasing install-count metrics in v1.

---

## 6. Key Features by Milestone

### Milestone 0 — Foundation & Validation (Pre-build)
**Goal:** De-risk architecture decisions before writing product code.
- Evaluate base distro choice (Arch vs. Debian vs. Fedora/OSTree) — build throwaway prototypes of each, evaluate atomic update story, package ecosystem, build tooling maturity.
- Evaluate wlroots vs. other compositor bases.
- Define target hardware shortlist for v1.
- Define the "intent schema" for the shortcut daemon (the contract apps will build against) — this is a foundational API decision that's expensive to change later.
- Prototype: does an OSTree-style immutable base + overlay actually work smoothly for daily driving? (Spike, not product.)

### Milestone 1 — Bootable Base
**Goal:** A minimal but bootable, daily-driveable system with the architectural bones in place, even if personalization features are stubbed.
- Bootable image with chosen base + Wayland/wlroots compositor
- Basic session (login, single workspace, floating window management)
- Flatpak app installation working
- Basic system settings app (not yet unified — just functional)
- Installer (even if rough)

### Milestone 2 — Consistency Layer MVP
**Goal:** Pillar B becomes real.
- Shortcut daemon live, with a first set of system-wide intents (window management, app switching, search invocation)
- "The Index" unified search MVP: apps + settings + files (basic indexing)
- Unified notification daemon
- First-party app toolkit finalized; 3–5 first-party apps (files, settings, terminal, text editor, image viewer) built consistently on it

### Milestone 3 — Personalization Layer MVP
**Goal:** Pillar A becomes real — the core bet of the product.
- Explicit automation engine (user-authored rules) with a genuinely approachable UI — this is make-or-break; if authoring an automation feels like programming, it fails the "Refugee" persona
- Layout memory: window/workspace state remembered and restored per monitor configuration
- Personalization profile export/import (portable, versioned)
- Transparency timeline for automated actions (visible, undoable)

### Milestone 4 — Suggested Automation (The Differentiator)
**Goal:** The system starts proactively compounding value without being asked.
- Usage pattern detection (local, privacy-preserving) for repeated action sequences
- Low-friction suggestion UI ("I noticed you do X — want to automate it?")
- Confidence/frequency tuning so suggestions don't become noise
- This is the feature most likely to need real iteration based on dogfooding — plan for multiple internal rounds before it's user-facing

### Milestone 5 — Polish, Third-Party Ecosystem, Public Alpha
- Third-party app consistency guidelines published + incentive/certification program
- Broader hardware testing beyond the initial shortlist
- Backup/restore hardened (this needs to be bulletproof — it's core to the "your investment isn't lost" promise)
- Public alpha release to a small cohort matching the target persona (likely: existing distro-hoppers, found via Linux-enthusiast communities)

*(Timeline estimates intentionally omitted — depends entirely on team size, which isn't yet defined. Recommend scoping Milestone 0 and 1 first, then estimating forward once real velocity is known.)*

---

## 7. Risks

| Risk | Notes |
|---|---|
| **Personalization engine feels creepy or untrustworthy** | If users don't trust the system to observe them, Pillar A dies. Mitigate with radical transparency (Section 5.5) and local-first defaults from day one, not bolted on later. |
| **"Suggested automation" becomes noisy/annoying** | The single feature most likely to actively repel users if done wrong (notification fatigue, wrong suggestions). Needs heavy dogfooding before any external user sees it. |
| **Third-party app inconsistency undermines Pillar B** | You control first-party apps; you don't control the broader app ecosystem. Flatpak + guidelines + certification helps but doesn't force compliance. Realistic expectation: consistency is strong for a curated set of apps, weaker at the edges — messaging should reflect this honestly. |
| **Scope creep toward "just another distro"** | Every milestone should be checked against: does this serve Pillar A, B, or C? If a feature is just "nice to have" parity with existing DEs, deprioritize it. |
| **Small hardware support matrix limits early adoption** | Deliberate tradeoff (Section 5.6) — needs to be a stated, confident decision, not an apology. |
| **Base distro choice ages poorly** | OSTree/Fedora-style atomic base is still maturing as an ecosystem pattern; validate thoroughly in Milestone 0 rather than assuming. |
| **Team/maintainer bus factor** | Not addressed in this PRD — worth a separate doc once you know if this is solo, small team, or aiming for open-source contributors. |

---

## 8. Open Questions

These need real decisions (from you, or from early dogfooding) before or during Milestone 0/1:

1. **Window management model:** refined tiling (opinionated, power-user-first) vs. hybrid floating+adaptive (broader appeal, fits "Refugee" persona better, but harder to make feel intentional rather than mushy)?
2. **Name/branding** — "Homestead" is a placeholder.
3. **Open source from day one, or build privately then release?** Affects contributor strategy, and whether Milestone 5's "third-party ecosystem" goal is realistic on your timeline.
4. **Team size/structure** — solo project, small founding team, or open-source-from-the-start with outside contributors? This changes milestone pacing significantly.
5. **How opinionated should defaults be on first boot?** A short onboarding flow that front-loads some personalization signal (e.g., "import your dotfiles/keybindings from X") could jumpstart Pillar A instead of starting from zero — worth prototyping.
6. **Monetization / sustainability model**, if any (fully open-source/donation-supported vs. some other model) — not required for v1 but affects long-term planning.

---

## 9. Appendix — Why Not Just Fork/Theme an Existing DE?

Worth stating explicitly since it's the most likely pushback: GNOME and KDE are both mature, and a theme/extension pack could ship faster. The reason not to:

- The consistency layer (5.3) requires a **shared shortcut/intent contract** and **unified notification/search daemons** that sit below the DE, not as GNOME extensions/KDE widgets bolted on top — extensions are exactly the kind of fragile, update-breaking layer this project is trying to avoid.
- The personalization engine (5.4) needs deep hooks into window management, app launching, and file system events that aren't cleanly exposed by existing DEs' extension APIs.
- Building on wlroots directly (rather than GNOME's Mutter or KDE's KWin) keeps the compositor minimal and avoids inheriting those projects' own architectural opinions and legacy constraints.

This is a real cost (more to build, slower to first release) taken deliberately because the thesis requires platform-level control, not desk-environment-level control.