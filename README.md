# Homestead OS — userspace prototype

PRD thesis: **an OS that becomes yours through use** — compounding
personalization (A), ruthless consistency (B), opinionated defaults with
total malleability (C). See `PRD.md` and `docs/`.

## What is built (running code)

`src/homestead/` — local-first, stdlib-only Python:

- `shortcuts/` — unified shortcut/intent daemon (PRD §5.3, M2)
- `index/` — The Index unified search: apps+settings+files+windows+automations (M2)
- `notifications/` — unified notification + focus/DND model (M2)
- `automation/engine.py` — explicit user-authored rules (M3)
- `automation/suggest.py` — suggested automations via local pattern detection (M4)
- `layout/` — adaptive layout memory per monitor context (M3)
- `profile/` — portable versioned personalization profile (M3/M5)
- `transparency/` — visible, undoable timeline for automated actions (§5.5)

## Run tests

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## What is NOT built here (needs a Linux host)

- M0 throwaway base-distro spikes → decision recorded in
  `docs/milestone-0-base-eval.md` (recommendation: Fedora atomic/OSTree-style).
- M1 bootable image, wlroots session, installer → see
  `docs/milestone-0-compositor-eval.md`, `docs/hardware-shortlist.md`.
- First-party app toolkit + 3–5 apps (M2), onboarding import flow, M5 ecosystem.

## Roadmap mapping

| Milestone | Status |
|---|---|
| M0 intent schema + evals | Done (prototype + docs) |
| M1 bootable base | Blocked on Linux build host |
| M2 consistency MVP | Prototype done, needs compositor wiring |
| M3 personalization MVP | Prototype done, needs shell/UI |
| M4 suggested automation | Detector done, needs dogfood tuning |
| M5 polish/ecosystem/alpha | Profile export certifies readiness |
