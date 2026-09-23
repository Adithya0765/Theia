"""The Index: one searchable surface (PRD 5.3).

Indexes apps, settings, files, windows, automations, shortcut bindings.
Single query entry point; providers are pluggable.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List


@dataclass
class IndexEntry:
    kind: str  # app | setting | file | window | automation | shortcut
    title: str
    detail: str = ""
    score_boost: float = 0.0


def _score(query: str, entry: IndexEntry) -> float:
    """Simple substring-rank: title prefix > title substring > detail match."""
    q = query.strip().lower()
    if not q:
        return 0.0
    title = entry.title.lower()
    detail = entry.detail.lower()
    base = 0.0
    if title.startswith(q):
        base = 100.0
    elif q in title:
        base = 60.0
    elif q in detail:
        base = 20.0
    else:
        # token-wise partial: all query tokens appear somewhere
        tokens = q.split()
        hay = f"{title} {detail}"
        if tokens and all(t in hay for t in tokens):
            base = 10.0
    # shorter titles rank slightly higher on ties; boost is usage-based (Pillar A).
    return base + entry.score_boost - min(len(title) * 0.05, 5.0)


@dataclass
class ScoredEntry:
    entry: IndexEntry
    score: float


class Index:
    def __init__(self) -> None:
        self._entries: List[IndexEntry] = []
        self._usage: Dict[str, int] = {}  # title -> launch count (compounding signal)

    def add(self, entry: IndexEntry) -> None:
        self._entries.append(entry)

    def add_many(self, entries: List[IndexEntry]) -> None:
        self._entries.extend(entries)

    def record_launch(self, title: str) -> None:
        """Usage signal feeds ranking (Pillar A) and stays on-device."""
        self._usage[title] = self._usage.get(title, 0) + 1

    def search(self, query: str, limit: int = 8) -> List[ScoredEntry]:
        scored = []
        for e in self._entries:
            boost = min(self._usage.get(e.title, 0) * 2.0, 20.0)
            eff = IndexEntry(e.kind, e.title, e.detail, boost)
            s = _score(query, eff)
            if s > 0:
                scored.append(ScoredEntry(entry=e, score=s))
        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:limit]

    def remove_by_title(self, title: str) -> int:
        before = len(self._entries)
        self._entries = [e for e in self._entries if e.title != title]
        return before - len(self._entries)
