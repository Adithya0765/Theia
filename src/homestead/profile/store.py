"""Portable personalization profile (PRD 5.4).

The anti-dotfile-fragility object: automations, learned layout memory,
shortcut remaps — exportable, versionable, diffable, restorable.
"""
from __future__ import annotations

import json
from typing import Any, Dict


PROFILE_VERSION = 1


def export_profile(shortcut_bindings: Dict[str, str],
                   automation_rules: list,
                   layout_data: dict,
                   prefs: Dict[str, str] | None = None) -> dict:
    return {
        "version": PROFILE_VERSION,
        "shortcuts": dict(shortcut_bindings),
        "automations": list(automation_rules),
        "layouts": dict(layout_data),
        "prefs": dict(prefs or {}),
    }


def serialize(profile: dict) -> str:
    return json.dumps(profile, indent=2, sort_keys=True)


def deserialize(text: str) -> dict:
    profile = json.loads(text)
    if profile.get("version") != PROFILE_VERSION:
        raise ValueError(
            f"unsupported profile version: {profile.get('version')!r} "
            f"(expected {PROFILE_VERSION})"
        )
    for key in ("shortcuts", "automations", "layouts"):
        if key not in profile:
            raise ValueError(f"profile missing key: {key}")
    return profile
