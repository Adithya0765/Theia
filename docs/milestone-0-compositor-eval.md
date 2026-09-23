# Milestone 0 — compositor evaluation (PRD §§5.2, 9)

Decision: **custom session/shell on wlroots, Wayland-only (XWayland for legacy).**

- Do not fork GNOME/KDE or build on Mutter/KWin: the shortcut/intent contract,
  unified notification/search daemons, and automation hooks need to sit below
  the DE, and extension APIs are exactly the fragile layer this project avoids
  (PRD §9).
- Do not re-implement Wayland: wlroots (Sway/Hyprland-proven) gives protocol
  plumbing; differentiation lives in the shell/session + consistency layers.
- Window model (PRD open question #1): prototype **hybrid floating + adaptive**
  with layout suggestions from `LayoutMemory`, not hard tiling on day one —
  fits the "Refugee" persona; tiling purists get `window.toggle-tile` intent.

Validation spikes (Linux host with real GPU):

1. Minimal wlroots shell: login, one workspace, floating windows, XWayland app.
2. Global keygrab wired to `ShortcutDaemon.resolve()` — prove the intent
   contract works at the compositor level, not just in-process.
3. Hook window open/close/move + monitor change events into `AutomationEngine`
   events and `LayoutMemory.remember()` — proves the §5.4 hooks exist.

The `ShortcutDaemon` prototype in this repo uses opaque binding strings
deliberately so the compositor spike can adopt real keycodes without changing
the intent API.
