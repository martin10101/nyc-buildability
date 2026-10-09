"""Preliminary apartment estimate arithmetic (the owner's preliminary assumptions).

Pure arithmetic: no file or network access, no clock, no AI. From a proposed
building's residential floor area it works a preliminary estimate of apartments - the
floor area times a share of it, divided by an apartment size - across the owner's
share range.

The share range 0.60 to 0.75 and the apartment size of 700 square feet are PRELIMINARY
ASSUMPTIONS chosen by the owner (D-090 R540, R541): the share range is an unvalidated
sensitivity range the user can change; 700 square feet is a chosen starting apartment
size on the HPD measurement basis the user can change. Neither is law, measured or
validated. The dividend is the proposed building's floor area (D-090 R509); the legal
maximum is kept separate, and the legal dwelling-unit limit is a separate module
(dwelling_units.py), not this one. The two quotients are shown to two decimals (round
half up - a display design assumption, ruling C6) and the unrounded quotients are kept
beside them; nothing is rounded to a count of apartments.

The owner's label (D-090 R543) is "Not known" until the option has floors and a shape,
then "Preliminary capacity estimate"; this module uses exactly those two labels.

This module imports no other part of this task and is imported by no existing engine
file; nothing it returns is reachable from a reported result yet.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from math import ceil, floor

_LABEL_AVAILABLE = "Preliminary capacity estimate"
_LABEL_NOT_KNOWN = "Not known"
_REASON_AVAILABLE = (
    "The estimate divides a share of the proposed building's residential floor area by "
    "an apartment size; the two quotients are shown to two decimals and are not a "
    "number of apartments to build. "
)
_REASON_NOT_KNOWN = (
    "The proposed building's residential floor area is not known for this lot; the "
    "building option (PART C) supplies it. No apartment estimate is given."
)


@dataclass(frozen=True)
class PreliminaryApartmentEstimate:
    """The two quotients (low and high share) of a preliminary apartment estimate, or a
    not-known state. ``status`` is 'available' or 'not_known'. ``quotient_low`` and
    ``quotient_high`` are shown to two decimals; the unrounded quotients are kept beside
    them. ``whole_below_*`` is the floor of a quotient and ``whole_above_*`` its ceiling,
    so an exact whole quotient has the same number below and above. ``missing_inputs``
    names the inputs not known for a missing-input state (empty otherwise);
    ``gap_kind`` is None for a missing-input state (a module that takes plain numbers
    cannot know why an input is missing)."""

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
    formula: str | None
    label: str
    reason: str
    missing_inputs: tuple[str, ...]
    gap_kind: str | None


def _round_half_up_2dp(value: float) -> float:
    """Round to two decimals, half up, for display only (ruling C6)."""
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _assumption_note(share_low: float, share_high: float, apartment_size_sq_ft: float) -> str:
    """The owner's descriptions of the two preliminary assumptions, written from the
    values actually used (D-090 R540, R541)."""
    return (
        f"The share range {share_low:.2f} to {share_high:.2f} is a preliminary "
        "assumption - an unvalidated sensitivity range the user can change - and the "
        f"apartment size of {apartment_size_sq_ft:g} square feet is a preliminary "
        "assumption - a chosen starting apartment size on the HPD measurement basis the "
        "user can change."
    )


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
    that names the missing input, never a zero and never a default, and names no kind of
    gap. An apartment size of zero or less, a share outside 0 to 1, a low share above
    the high share, or a negative floor area is refused with ``ValueError``; the
    estimate never divides by zero.
    """
    if apartment_size_sq_ft <= 0:
        raise ValueError(
            f"apartment size must be greater than zero (got {apartment_size_sq_ft})"
        )
    if not 0 <= share_low <= 1 or not 0 <= share_high <= 1:
        raise ValueError(
            f"a share must be between 0 and 1: low={share_low}, high={share_high}"
        )
    if share_low > share_high:
        raise ValueError(
            f"the low share cannot be above the high share: low={share_low}, "
            f"high={share_high}"
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
            formula=None,
            label=_LABEL_NOT_KNOWN,
            reason=_REASON_NOT_KNOWN,
            missing_inputs=("floor_area_sq_ft",),
            gap_kind=None,
        )
    if floor_area_sq_ft < 0:
        raise ValueError(f"floor area cannot be negative (got {floor_area_sq_ft})")
    low_unrounded = floor_area_sq_ft * share_low / apartment_size_sq_ft
    high_unrounded = floor_area_sq_ft * share_high / apartment_size_sq_ft
    note = _assumption_note(share_low, share_high, apartment_size_sq_ft)
    return PreliminaryApartmentEstimate(
        status="available",
        quotient_low=_round_half_up_2dp(low_unrounded),
        quotient_high=_round_half_up_2dp(high_unrounded),
        quotient_low_unrounded=low_unrounded,
        quotient_high_unrounded=high_unrounded,
        whole_below_low=floor(low_unrounded),
        whole_above_low=ceil(low_unrounded),
        whole_below_high=floor(high_unrounded),
        whole_above_high=ceil(high_unrounded),
        floor_area_sq_ft=floor_area_sq_ft,
        share_low=share_low,
        share_high=share_high,
        apartment_size_sq_ft=apartment_size_sq_ft,
        formula="floor area x share / apartment size. " + note,
        label=_LABEL_AVAILABLE,
        reason=_REASON_AVAILABLE + note,
        missing_inputs=(),
        gap_kind=None,
    )
