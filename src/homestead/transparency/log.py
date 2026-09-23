"""Transparency timeline (PRD 5.5).

Every automated action is logged visibly with its reason, and is
undoable. Supports always/never preferences per automation source.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
import time


@dataclass
class TimelineEntry:
    id: int
    source: str  # rule name or "layout-memory" / "suggestion-applied"
    description: str
    reason: str
    timestamp: float = field(default_factory=time.time)
    undone: bool = False


class TransparencyLog:
    def __init__(self) -> None:
        self._entries: List[TimelineEntry] = []
        self._next_id = 1
        self._prefs: Dict[str, str] = {}  # source -> "ask" | "always" | "never"
        self._undo_handlers: Dict[int, Callable[[], None]] = {}

    def preference(self, source: str) -> str:
        return self._prefs.get(source, "ask")

    def set_preference(self, source: str, pref: str) -> None:
        if pref not in ("ask", "always", "never"):
            raise ValueError(f"bad preference: {pref}")
        self._prefs[source] = pref

    def record(self, source: str, description: str, reason: str,
               undo: Optional[Callable[[], None]] = None) -> TimelineEntry:
        entry = TimelineEntry(id=self._next_id, source=source,
                              description=description, reason=reason)
        self._next_id += 1
        self._entries.append(entry)
        if undo is not None:
            self._undo_handlers[entry.id] = undo
        return entry

    def undo(self, entry_id: int) -> bool:
        for e in self._entries:
            if e.id == entry_id and not e.undone:
                handler = self._undo_handlers.get(entry_id)
                if handler is not None:
                    handler()
                e.undone = True
                return True
        return False

    def timeline(self) -> List[TimelineEntry]:
        return list(self._entries)
