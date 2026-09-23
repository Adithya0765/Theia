# Intent schema — M0 foundational API decision (PRD §§5.3, 6/M0)

Status: **decided for prototype, to validate on Linux compositor.**

## Contract

```python
Intent(name, description, category, default_binding)
# name: "<domain>.<verb>" e.g. "window.close"
# category: window | app | search | workspace | system
```

- Apps declare `intent_name` in their manifest; they **never** register raw keys.
- `ShortcutDaemon` owns `binding -> intent`. One remap surface, conflicts raise
  (`IntentConflictError`) instead of shadowing.
- `export()` / `import_bindings()` feed the portable profile (PRD §5.4).

## M2 initial set

Implemented in `src/homestead/shortcuts/daemon.py` (`BUILTIN_INTENTS`):

window.close, window.focus-next/prev, window.toggle-tile, app.switch,
app.launch, search.invoke (The Index), workspace.next/prev, system.dnd-toggle.

## Rules for extending

1. New intents need `category` + default binding + description; no ad-hoc strings.
2. Defaults must not collide; daemon enforces at registration.
3. Renaming an intent is a breaking change — version it (`window.close.v2`),
   keep the old as alias for one release.
4. Third-party apps (M5) may propose intents but the system reserves
   `window.*`, `workspace.*`, `system.*`.

## Open validation (needs wlroots session)

- Multi-key chords / sequences beyond `Super+X` (prototype stores opaque strings).
- Per-app intent scoping vs. global-only (prototype is global-only).
- Wayland keygrab mechanics in the compositor layer.
