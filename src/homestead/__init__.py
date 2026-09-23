"""Homestead OS userspace prototype.

Implements PRD sections 5.3 (Consistency), 5.4 (Personalization),
and 5.5 (Transparency) as a local-first, stdlib-only Python prototype.

The OS-image work (M0 base eval, M1 bootable image, wlroots compositor)
requires a Linux build host and is tracked in docs/. This package is the
testable core of the thesis: compounding personalization + consistency.
"""

__version__ = "0.1.0"
