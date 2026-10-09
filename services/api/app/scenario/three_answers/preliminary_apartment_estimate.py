"""Preliminary apartment estimate arithmetic (the owner's preliminary assumptions).

Pure arithmetic: no file or network access, no clock, no AI. From a proposed
building's residential floor area it works a preliminary estimate of apartments - the
floor area times a share of it, divided by an apartment size - across the owner's
share range.

The share range 0.60 to 0.75 and the apartment size of 700 square feet are
PRELIMINARY ASSUMPTIONS chosen by the owner (D-090 R540, R541): they are not law, not
measured and not validated. The dividend is the proposed building's floor area (D-090
R509); the legal maximum is kept separate, and the legal dwelling-unit limit is a
separate module (dwelling_units.py), not this one. The two quotients are shown to two
decimals (round half up - a display design assumption, ruling C6) and the unrounded
quotients are kept beside them; nothing is rounded to a count of apartments.

This module imports no other part of this task and is imported by no existing engine
file; nothing it returns is reachable from a reported result yet.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from math import floor

_LABEL = (
    "Preliminary apartment estimate from a preliminary assumption share and "
    "apartment size"
)
_FORMULA = (
    "floor area x share / apartment size (the share range and the apartment size are "
    "each a preliminary assumption chosen by the owner)"
)
_REASON_AVAILABLE = (
    "The estimate divides a share of the proposed building's residential floor area by "
    "an apartment size. The share range 0.60 to 0.75 and the apartment size of 700 "
    "square feet are each a preliminary assumption chosen by the owner; the two "
    "quotients are shown to two decimals and are not a number of apartments to build."
)
_REASON_NOT_KNOWN = (
    "The preliminary apartment estimate needs the proposed building's residential "
    "floor area, which is not known for this lot; it stays a preliminary assumption-"
    "based estimate, not a number of apartments to build, until that floor area is "
    "provided."
)


@dataclass(frozen=True)
class PreliminaryApartmentEstimate:
    """The two quotients (low and high share) of a preliminary apartment estimate, or a
    not-known state. ``status`` is 'available' or 'not_known'. ``quotient_low`` and
    ``quotient_high`` are shown to two decimals; the unrounded quotients are kept
    beside them. The whole numbers just below and just above each quotient are kept as
    a range, never a single count. For a not-known state ``gap_kind`` names which kind
    of gap it is."""

    status: str
    quotient_low: float | None
    quotient_high: float | None
    quotient_low_unrounded: float | None
    quotient_high_unrounded: float | None
    whole_below_low: int | None
    whole_above_low: int | None
    whole_below_high: int | None
    whole_above_high: int | None
    floor_area_sq_ft: float | None
    share_low: float
    share_high: float
    apartment_size_sq_ft: float
    formula: str
    label: str
    reason: str
    gap_kind: str | None


def _round_half_up_2dp(value: float) -> float:
    """Round to two decimals, half up, for display only (ruling C6)."""
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def preliminary_apartment_estimate(
    floor_area_sq_ft: float | None,
    share_low: float = 0.60,
    share_high: float = 0.75,
    apartment_size_sq_ft: float = 700.0,
) -> PreliminaryApartmentEstimate:
    """Work the preliminary apartment estimate from a proposed building's floor area.

    ``floor_area_sq_ft`` is the proposed building's residential floor area (D-090
    R509). ``share_low``/``share_high`` and ``apartment_size_sq_ft`` are the owner's
    preliminary assumptions. A missing floor area (``None``) gives a not-known result
    with a plain reason, never a zero and never a default. An apartment size of zero or
    less is refused with ``ValueError``; the estimate never divides by zero.
    """
    if apartment_size_sq_ft <= 0:
        raise ValueError(
            f"apartment size must be greater than zero (got {apartment_size_sq_ft})"
        )
    if floor_area_sq_ft is None:
        return PreliminaryApartmentEstimate(
            status="not_known",
            quotient_low=None,
            quotient_high=None,
            quotient_low_unrounded=None,
            quotient_high_unrounded=None,
            whole_below_low=None,
            whole_above_low=None,
            whole_below_high=None,
            whole_above_high=None,
            floor_area_sq_ft=None,
            share_low=share_low,
            share_high=share_high,
            apartment_size_sq_ft=apartment_size_sq_ft,
            formula=_FORMULA,
            label=_LABEL,
            reason=_REASON_NOT_KNOWN,
            gap_kind="a missing fact about the property",
        )
    low_unrounded = floor_area_sq_ft * share_low / apartment_size_sq_ft
    high_unrounded = floor_area_sq_ft * share_high / apartment_size_sq_ft
    whole_below_low = floor(low_unrounded)
    whole_below_high = floor(high_unrounded)
    return PreliminaryApartmentEstimate(
        status="available",
        quotient_low=_round_half_up_2dp(low_unrounded),
        quotient_high=_round_half_up_2dp(high_unrounded),
        quotient_low_unrounded=low_unrounded,
        quotient_high_unrounded=high_unrounded,
        whole_below_low=whole_below_low,
        whole_above_low=whole_below_low + 1,
        whole_below_high=whole_below_high,
        whole_above_high=whole_below_high + 1,
        floor_area_sq_ft=floor_area_sq_ft,
        share_low=share_low,
        share_high=share_high,
        apartment_size_sq_ft=apartment_size_sq_ft,
        formula=_FORMULA,
        label=_LABEL,
        reason=_REASON_AVAILABLE,
        gap_kind=None,
    )
