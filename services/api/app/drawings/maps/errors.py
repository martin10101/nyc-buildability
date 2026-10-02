"""Typed refusals of the location/zoning map builder (task E-07, plan section 5c).

Like the drawing kit, the map builder fails CLOSED: a map context that is
malformed, carries an unsupported CRS, or whose geometry cannot be drawn
truthfully (an open ring, a self-crossing outline, a coordinate outside the
supported extent) raises :class:`MapInputError` instead of drawing a map.
"""

from __future__ import annotations

__all__ = ["MapInputError"]


class MapInputError(ValueError):
    """The map context cannot be drawn; nothing is emitted.

    ``code`` is a stable machine-readable reason (e.g. ``unsupported_crs``,
    ``ring_not_closed``, ``too_many_features``); ``location`` is the JSON
    pointer into the map-context document where the defect was found.
    """

    def __init__(self, code: str, message: str, *, location: str = "") -> None:
        super().__init__(f"{code}: {message}" + (f" (at {location})" if location else ""))
        self.code = code
        self.location = location
