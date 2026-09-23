"""Suggested automations (PRD 5.4, Milestone 4).

Local-only pattern detector: observes repeated manual action sequences
and proposes turning them into one-click automations. Low-friction by
design: suggestions carry confidence + frequency and the caller decides
presentation (subtle suggestion, never a nag). No data leaves the device.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple
from collections import Counter


@dataclass
class Suggestion:
    sequence: Tuple[str, ...]
    count: int
    confidence: float  # 0..1
    text: str


class PatternDetector:
    """Counts N-grams of action names; suggests when count >= threshold."""

    def __init__(self, min_count: int = 3, sequence_len: int = 3) -> None:
        if min_count < 2:
            raise ValueError("min_count must be >= 2 to avoid noise")
        self.min_count = min_count
        self.sequence_len = sequence_len
        self._history: List[str] = []
        self._dismissed: set = set()

    def observe(self, action: str) -> None:
        self._history.append(action)

    def dismiss(self, sequence: Tuple[str, ...]) -> None:
        self._dismissed.add(sequence)

    def suggestions(self) -> List[Suggestion]:
        n = self.sequence_len
        if len(self._history) < n:
            return []
        grams = Counter(
            tuple(self._history[i:i + n]) for i in range(len(self._history) - n + 1)
        )
        out: List[Suggestion] = []
        total = max(len(self._history), 1)
        for seq, count in grams.most_common():
            if count < self.min_count or seq in self._dismissed:
                continue
            # Confidence: frequency tempered by history length (avoids
            # over-firing in the first hour of use).
            confidence = min(count / total + 0.5 * (count / self.min_count - 1), 1.0)
            confidence = max(0.0, min(1.0, confidence))
            out.append(Suggestion(
                sequence=seq, count=count, confidence=round(confidence, 3),
                text=f"I noticed you do {' -> '.join(seq)} ({count}x). Automate it?",
            ))
        return sorted(out, key=lambda s: (-s.confidence, -s.count))
