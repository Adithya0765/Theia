"""Adaptive layout / workflow memory (PRD 5.4).

Remembers window arrangements per context (monitor fingerprint + mode)
and restores them, with confidence increasing over observations.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Layout:
    context: str  # e.g. monitor fingerprint + mode: "2x1440p|focus"
    windows: List[str]  # ordered app/window identifiers
    observations: int = 1


class LayoutMemory:
    def __init__(self) -> None:
        self._layouts: Dict[str, Layout] = {}

    def remember(self, context: str, windows: List[str]) -> Layout:
        """Record an arrangement; repeated identical recalls raise confidence."""
        existing = self._layouts.get(context)
        if existing is not None and existing.windows == windows:
            existing.observations += 1
            return existing
        layout = Layout(context=context, windows=list(windows),
                        observations=(existing.observations + 1) if existing else 1)
        self._layouts[context] = layout
        return layout

    def recall(self, context: str) -> Optional[Layout]:
        return self._layouts.get(context)

    def confidence(self, context: str) -> float:
        """0..1, saturating: 1 obs -> 0.33, 3 -> 0.75, 5+ -> ~0.9+."""
        layout = self._layouts.get(context)
        if layout is None:
            return 0.0
        n = layout.observations
        return round(n / (n + 2.0), 3)

    def export(self) -> dict:
        return {ctx: {"windows": l.windows, "observations": l.observations}
                for ctx, l in self._layouts.items()}

    def import_data(self, data: dict) -> None:
        for ctx, v in data.items():
            self._layouts[ctx] = Layout(context=ctx, windows=list(v["windows"]),
                                        observations=int(v.get("observations", 1)))
