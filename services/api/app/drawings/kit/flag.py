"""Lane E feature flag for the drawing kit (default OFF, fail safe).

Reads ``LANE_E_ENABLED`` through :func:`app.config.lane_enabled` (read-only use
of the shared lane-flag helper): only an explicit true token turns the kit on;
absent, empty or unknown values leave it off.
"""

from __future__ import annotations

from collections.abc import Mapping

from app.config import lane_enabled

__all__ = ["DrawingKitDisabled", "drawing_kit_enabled"]


class DrawingKitDisabled(RuntimeError):
    """The drawing kit was called while the Lane E flag is off."""


def drawing_kit_enabled(env: Mapping[str, str] | None = None) -> bool:
    return lane_enabled("E", env)
