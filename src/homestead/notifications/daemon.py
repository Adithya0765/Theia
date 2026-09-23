"""Unified notification + focus model (PRD 5.3).

One daemon, one interruption policy, one system-wide focus/DND state.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal
import time

Priority = Literal["urgent", "normal", "silent"]


@dataclass
class Notification:
    app: str
    title: str
    body: str = ""
    priority: Priority = "normal"
    timestamp: float = field(default_factory=time.time)
    delivered: bool = False  # False => logged silently due to focus/DND
    id: int = 0


class NotificationDaemon:
    def __init__(self) -> None:
        self.dnd: bool = False
        self.focus_mode: str = "normal"  # normal | focus | meeting | idle
        self._log: List[Notification] = []
        self._next_id = 1

    def set_focus(self, mode: str, dnd: bool) -> None:
        if mode not in ("normal", "focus", "meeting", "idle"):
            raise ValueError(f"unknown focus mode: {mode}")
        self.focus_mode = mode
        self.dnd = dnd

    def notify(self, app: str, title: str, body: str = "",
               priority: Priority = "normal") -> Notification:
        n = Notification(app=app, title=title, body=body, priority=priority,
                         id=self._next_id)
        self._next_id += 1
        # Interruption policy: urgent always breaks through; silent never
        # interrupts; normal is suppressed under DND/focus/meeting.
        if priority == "urgent":
            n.delivered = True
        elif priority == "silent":
            n.delivered = False
        else:
            n.delivered = not (self.dnd or self.focus_mode in ("focus", "meeting"))
        self._log.append(n)
        return n

    def history(self, delivered_only: bool = False) -> List[Notification]:
        if delivered_only:
            return [n for n in self._log if n.delivered]
        return list(self._log)

    def badge_count(self) -> int:
        """Silent/logged items awaiting review."""
        return sum(1 for n in self._log if not n.delivered)
