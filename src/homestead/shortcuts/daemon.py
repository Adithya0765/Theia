"""Unified shortcut / intent daemon (PRD 5.3).

Apps declare intents against a standard schema; the daemon owns the
physical-key -> intent mapping, centrally remappable in one place.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Intent:
    """A semantic action an app or the system can perform.

    Apps never bind raw keys; they declare `intent_name` and the daemon
    resolves the physical binding. This is the M0 foundational API.
    """

    name: str  # e.g. "window.close"
    description: str
    category: str  # window | app | search | workspace | system
    default_binding: str  # e.g. "Super+Q"


# M2 initial intent set (PRD: window mgmt, app switching, search).
BUILTIN_INTENTS: List[Intent] = [
    Intent("window.close", "Close focused window", "window", "Super+Q"),
    Intent("window.focus-next", "Focus next window", "window", "Super+J"),
    Intent("window.focus-prev", "Focus previous window", "window", "Super+K"),
    Intent("window.toggle-tile", "Toggle tiling/floating", "window", "Super+T"),
    Intent("app.switch", "Switch to app by name", "app", "Super+Tab"),
    Intent("app.launch", "Launch app by name", "app", "Super+Space"),
    Intent("search.invoke", "Open The Index (unified search)", "search", "Super+/"),
    Intent("workspace.next", "Next workspace", "workspace", "Super+L"),
    Intent("workspace.prev", "Previous workspace", "workspace", "Super+H"),
    Intent("system.dnd-toggle", "Toggle focus / do-not-disturb", "system", "Super+D"),
]


class IntentConflictError(ValueError):
    pass


class ShortcutDaemon:
    """Central owner of keybinding registration (PRD 5.3)."""

    def __init__(self, intents: Optional[List[Intent]] = None) -> None:
        self._intents: Dict[str, Intent] = {}
        self._bindings: Dict[str, str] = {}  # binding -> intent name
        for intent in intents if intents is not None else BUILTIN_INTENTS:
            self.register_intent(intent)

    def register_intent(self, intent: Intent) -> None:
        if intent.name in self._intents:
            raise IntentConflictError(f"intent already registered: {intent.name}")
        if intent.default_binding in self._bindings:
            raise IntentConflictError(
                f"binding {intent.default_binding!r} already taken by "
                f"{self._bindings[intent.default_binding]!r}"
            )
        self._intents[intent.name] = intent
        self._bindings[intent.default_binding] = intent.name

    def resolve(self, binding: str) -> Optional[Intent]:
        """Map a physical key combo to its intent (None if unbound)."""
        name = self._bindings.get(binding)
        return self._intents.get(name) if name else None

    def binding_for(self, intent_name: str) -> Optional[str]:
        for binding, name in self._bindings.items():
            if name == intent_name:
                return binding
        return None

    def remap(self, intent_name: str, new_binding: str) -> None:
        """Remap in one place; conflicts raise instead of silently shadowing."""
        if intent_name not in self._intents:
            raise KeyError(f"unknown intent: {intent_name}")
        owner = self._bindings.get(new_binding)
        if owner is not None and owner != intent_name:
            raise IntentConflictError(
                f"binding {new_binding!r} already owned by {owner!r}"
            )
        old = self.binding_for(intent_name)
        if old is not None:
            del self._bindings[old]
        self._bindings[new_binding] = intent_name

    def unbind(self, intent_name: str) -> None:
        old = self.binding_for(intent_name)
        if old is not None:
            del self._bindings[old]

    def list_intents(self) -> List[Intent]:
        return sorted(self._intents.values(), key=lambda i: i.name)

    def export(self) -> dict:
        """Part of the portable personalization profile (PRD 5.4)."""
        return {
            "bindings": dict(self._bindings),
            "intents": [asdict(i) for i in self.list_intents()],
        }

    def import_bindings(self, bindings: Dict[str, str]) -> None:
        # Validate all intent names exist before mutating.
        for name in bindings.values():
            if name not in self._intents:
                raise KeyError(f"unknown intent in import: {name}")
        if len(set(bindings.values())) != len(bindings.values()):
            raise IntentConflictError("import maps two bindings to one intent")
        self._bindings = dict(bindings)
