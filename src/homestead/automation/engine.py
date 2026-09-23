"""Explicit automation engine (PRD 5.4, Milestone 3).

User-authored rules: trigger + optional condition -> action.
Actions are plain callables so the engine stays UI- and OS-agnostic;
the desktop shell wires real window/file/monitor effects in later.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class Event:
    kind: str  # e.g. "monitor.connected", "file.created", "app.launched"
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Rule:
    name: str
    trigger: str  # event kind this rule fires on
    action_name: str  # human-readable, shown in UI + transparency timeline
    condition: Optional[Callable[[Event], bool]] = None
    enabled: bool = True

    def matches(self, event: Event) -> bool:
        if not self.enabled or event.kind != self.trigger:
            return False
        if self.condition is not None:
            try:
                return bool(self.condition(event))
            except Exception:
                return False
        return True


class AutomationEngine:
    """Approachable-rule store + dispatcher.

    `register_action` maps action_name -> callable(payload) -> result string.
    `dispatch` returns the list of (rule_name, result) that fired.
    """

    def __init__(self) -> None:
        self._rules: Dict[str, Rule] = {}
        self._actions: Dict[str, Callable[[Dict[str, Any]], str]] = {}

    def register_action(self, name: str,
                        fn: Callable[[Dict[str, Any]], str]) -> None:
        self._actions[name] = fn

    def add_rule(self, rule: Rule) -> None:
        if rule.name in self._rules:
            raise ValueError(f"rule already exists: {rule.name}")
        if rule.action_name not in self._actions:
            raise KeyError(f"unknown action: {rule.action_name}")
        self._rules[rule.name] = rule

    def remove_rule(self, name: str) -> None:
        del self._rules[name]

    def rules(self) -> List[Rule]:
        return sorted(self._rules.values(), key=lambda r: r.name)

    def dispatch(self, event: Event) -> List[tuple]:
        fired = []
        for rule in self._rules.values():
            if rule.matches(event):
                result = self._actions[rule.action_name](event.payload)
                fired.append((rule.name, result))
        return fired

    def export_rules(self) -> list:
        """Serializable form for the portable profile (no lambdas)."""
        return [
            {"name": r.name, "trigger": r.trigger,
             "action_name": r.action_name, "enabled": r.enabled,
             "has_condition": r.condition is not None}
            for r in self.rules()
        ]
