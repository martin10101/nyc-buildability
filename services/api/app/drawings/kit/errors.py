"""Typed refusals of the drawing kit (task E-01, plan section 5c).

The kit fails CLOSED: input that does not honor the results contract, or whose
geometry cannot be drawn truthfully (an open ring, a self-crossing outline, a
floor plate outside the lot, floor plates that disagree with the floor-by-floor
table), raises :class:`DrawingInputError` instead of producing a drawing.
"""

from __future__ import annotations

__all__ = ["DrawingInputError"]


class DrawingInputError(ValueError):
    """The results document cannot be drawn; nothing is emitted.

    ``code`` is a stable machine-readable reason (e.g. ``schema_invalid``,
    ``ring_not_closed``, ``plate_outside_lot``); ``location`` is the JSON
    pointer into the results document where the defect was found.
    """

    def __init__(self, code: str, message: str, *, location: str = "") -> None:
        super().__init__(f"{code}: {message}" + (f" (at {location})" if location else ""))
        self.code = code
        self.location = location
