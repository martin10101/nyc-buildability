"""The Lane B flag in front of multi-lot site math (B-07; lane rule "new behavior goes
behind your lane flag, OFF in production").

``LANE_B_ENABLED`` is read through ``app.config.lane_enabled``: only an explicit true token
turns it on; absent, empty or anything else is off. While it is off the gated entry returns
None and computes nothing. A caller (a later Lane C wiring task) uses this entry, never
``derive.derive_multi_lot_site`` directly.
"""

from __future__ import annotations

from collections.abc import Mapping

from app.config import lane_enabled

from .derive import derive_multi_lot_site
from .results import MultiLotSite

__all__ = ["LANE", "derive_multi_lot_site_if_enabled", "multi_lot_site_enabled"]

LANE = "B"


def multi_lot_site_enabled(env: Mapping[str, str] | None = None) -> bool:
    return lane_enabled(LANE, env)


def derive_multi_lot_site_if_enabled(
    *args: object, env: Mapping[str, str] | None = None, **kwargs: object
) -> MultiLotSite | None:
    """:func:`~.derive.derive_multi_lot_site` when the Lane B flag is on, else None."""
    if not multi_lot_site_enabled(env):
        return None
    return derive_multi_lot_site(*args, **kwargs)
