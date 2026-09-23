"""Cross-module tests for the Homestead userspace prototype.

Covers PRD M2 (shortcuts, index, notifications), M3 (automation, layout,
profile, transparency), M4 (suggestions).
"""
import unittest

from homestead.shortcuts.daemon import ShortcutDaemon, Intent, IntentConflictError
from homestead.index.index import Index, IndexEntry
from homestead.notifications.daemon import NotificationDaemon
from homestead.automation.engine import AutomationEngine, Rule, Event
from homestead.automation.suggest import PatternDetector
from homestead.layout.memory import LayoutMemory
from homestead.profile.store import export_profile, serialize, deserialize
from homestead.transparency.log import TransparencyLog


class TestShortcuts(unittest.TestCase):
    def test_resolve_builtin(self):
        d = ShortcutDaemon()
        self.assertEqual(d.resolve("Super+/").name, "search.invoke")

    def test_remap_and_conflict(self):
        d = ShortcutDaemon()
        d.remap("search.invoke", "Ctrl+K")
        self.assertIsNone(d.resolve("Super+/"))
        self.assertEqual(d.resolve("Ctrl+K").name, "search.invoke")
        with self.assertRaises(IntentConflictError):
            d.remap("app.launch", "Ctrl+K")

    def test_export_import_roundtrip(self):
        d = ShortcutDaemon()
        d.remap("window.close", "Ctrl+Q")
        data = d.export()
        d2 = ShortcutDaemon()
        d2.import_bindings(data["bindings"])
        self.assertEqual(d2.resolve("Ctrl+Q").name, "window.close")

    def test_unknown_intent_rejected(self):
        d = ShortcutDaemon()
        with self.assertRaises(KeyError):
            d.remap("nope.nope", "Ctrl+X")
        with self.assertRaises(KeyError):
            d2 = ShortcutDaemon()
            d2.import_bindings({"Ctrl+X": "nope.nope"})


class TestIndex(unittest.TestCase):
    def test_apps_settings_files_single_surface(self):
        idx = Index()
        idx.add_many([
            IndexEntry("app", "Terminal", "launch terminal"),
            IndexEntry("setting", "Display settings", "resolution scaling"),
            IndexEntry("file", "report.pdf", "quarterly report"),
        ])
        self.assertEqual(idx.search("term")[0].entry.title, "Terminal")
        self.assertEqual(idx.search("display")[0].entry.kind, "setting")
        self.assertEqual(idx.search("report")[0].entry.kind, "file")

    def test_usage_boost_compounds(self):
        idx = Index()
        idx.add_many([IndexEntry("app", "Terminal Pro", ""), IndexEntry("app", "Terminal", "")])
        idx.record_launch("Terminal")
        idx.record_launch("Terminal")
        self.assertEqual(idx.search("terminal")[0].entry.title, "Terminal")


class TestNotifications(unittest.TestCase):
    def test_dnd_suppresses_normal_not_urgent(self):
        n = NotificationDaemon()
        n.set_focus("focus", dnd=True)
        quiet = n.notify("chat", "hi", priority="normal")
        loud = n.notify("battery", "critical", priority="urgent")
        self.assertFalse(quiet.delivered)
        self.assertTrue(loud.delivered)
        self.assertEqual(n.badge_count(), 1)

    def test_silent_never_interrupts(self):
        n = NotificationDaemon()
        s = n.notify("sync", "done", priority="silent")
        self.assertFalse(s.delivered)


class TestAutomation(unittest.TestCase):
    def test_explicit_rule_fires(self):
        eng = AutomationEngine()
        eng.register_action("tile-left", lambda p: f"tiled {p['app']}")
        eng.add_rule(Rule("dock-setup", "monitor.connected", "tile-left",
                          condition=lambda e: e.payload.get("outputs") == 2))
        fired = eng.dispatch(Event("monitor.connected", {"outputs": 2, "app": "editor"}))
        self.assertEqual(fired, [("dock-setup", "tiled editor")])
        self.assertEqual(eng.dispatch(Event("monitor.connected", {"outputs": 1})), [])

    def test_unknown_action_rejected(self):
        eng = AutomationEngine()
        with self.assertRaises(KeyError):
            eng.add_rule(Rule("bad", "x", "missing-action"))


class TestSuggestions(unittest.TestCase):
    def test_repeated_sequence_suggested(self):
        p = PatternDetector(min_count=3, sequence_len=2)
        for _ in range(3):
            p.observe("open-editor")
            p.observe("tile-right")
        sugs = p.suggestions()
        self.assertTrue(any(s.sequence == ("open-editor", "tile-right") for s in sugs))

    def test_no_noise_below_threshold_and_dismiss(self):
        p = PatternDetector(min_count=3, sequence_len=2)
        p.observe("a")
        p.observe("b")
        self.assertEqual(p.suggestions(), [])
        for _ in range(3):
            p.observe("x")
            p.observe("y")
        seq = ("x", "y")
        self.assertTrue(any(s.sequence == seq for s in p.suggestions()))
        p.dismiss(seq)
        self.assertFalse(any(s.sequence == seq for s in p.suggestions()))


class TestLayoutMemory(unittest.TestCase):
    def test_remember_recall_confidence_grows(self):
        m = LayoutMemory()
        ctx = "2x1440p|focus"
        m.remember(ctx, ["editor", "terminal"])
        c1 = m.confidence(ctx)
        m.remember(ctx, ["editor", "terminal"])
        c2 = m.confidence(ctx)
        self.assertGreater(c2, c1)
        self.assertEqual(m.recall(ctx).windows, ["editor", "terminal"])
        self.assertEqual(m.confidence("unknown"), 0.0)


class TestProfile(unittest.TestCase):
    def test_portable_roundtrip(self):
        d = ShortcutDaemon()
        m = LayoutMemory()
        m.remember("dock", ["editor"])
        profile = export_profile(d.export()["bindings"], [], m.export(), {"x": "always"})
        restored = deserialize(serialize(profile))
        self.assertEqual(restored["shortcuts"], profile["shortcuts"])
        self.assertEqual(restored["layouts"], profile["layouts"])

    def test_version_checked(self):
        with self.assertRaises(ValueError):
            deserialize('{"version": 999}')


class TestTransparency(unittest.TestCase):
    def test_record_undo_prefs(self):
        t = TransparencyLog()
        state = {"tiled": True}
        e = t.record("dock-setup", "tiled editor left", "monitor connected",
                     undo=lambda: state.update(tiled=False))
        self.assertTrue(t.undo(e.id))
        self.assertFalse(state["tiled"])
        self.assertTrue(e.undone)
        t.set_preference("dock-setup", "always")
        self.assertEqual(t.preference("dock-setup"), "always")
        with self.assertRaises(ValueError):
            t.set_preference("dock-setup", "sometimes")


if __name__ == "__main__":
    unittest.main()
