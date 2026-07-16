"""BBL validation and normalization shared by connectors (task M1-T002).

Grounding (never guessed):

- Canonical 10-digit BBL = borough code (1-5) + tax block zero-padded to 5
  digits + tax lot zero-padded to 4 digits: PLUTO Data Dictionary 26v1 p.38
  (docs/research/pluto-mappluto-2026-07-16.md section 4.1) and the accepted
  contract pattern ``^[1-5][0-9]{5}[0-9]{4}$`` in
  ``packages/contracts/schemas/v1/common.schema.json#/$defs/bbl``.
- Socrata serializes number-typed BBL columns with an all-zero fractional
  tail, e.g. ``"1000010100.00000000"`` (M1-T001 G1 finding C6; fixture
  ``F12_bbl_decimal_serialization.json``). Normalization strips that tail
  deterministically while the caller preserves the raw value in provenance.
- Block range 1-99999 and lot range 1-9999 follow the dictionary's zero-padded
  field widths; all-zero block/lot are rejected here (stricter than the
  contract pattern, which leaves them open-with-flag). Lot EXISTENCE is never
  decided here - that belongs to the source connectors.

This module is pure validation/normalization: no network, no logging of
values beyond the typed error payload, no legal logic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

__all__ = [
    "BBLValidationError",
    "NormalizedBBL",
    "bbl_from_components",
    "check_identifier_consistency",
    "normalize_bbl",
]

_CANONICAL_RE = re.compile(r"^[1-5][0-9]{5}[0-9]{4}$")
_NUMERIC_RE = re.compile(r"^[0-9]+(\.[0-9]+)?$")
_NEGATIVE_RE = re.compile(r"^-[0-9]+(\.[0-9]+)?$")


class BBLValidationError(ValueError):
    """Typed BBL validation failure. ``code`` names the exact defect.

    Codes: ``empty``, ``non_numeric``, ``negative``, ``non_integer_decimal``,
    ``wrong_length``, ``invalid_borough``, ``invalid_block``, ``invalid_lot``,
    ``invalid_component``.
    """

    error_type = "validation_error"

    def __init__(self, code: str, message: str, raw_value: object) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.raw_value = raw_value

    def to_payload(self) -> dict:
        """Structured error payload. Never includes a stack trace."""
        return {
            "error_type": self.error_type,
            "code": self.code,
            "message": self.message,
            "raw_value": repr(self.raw_value),
        }


@dataclass(frozen=True)
class NormalizedBBL:
    """Canonical BBL plus its verbatim raw input and parsed components."""

    canonical: str
    raw: object
    borough: int
    block: int
    lot: int


def _digits_from_input(value: object) -> str:
    """Reduce input to a plain digit string or raise a typed error."""
    if value is None:
        raise BBLValidationError("empty", "BBL input is missing (None)", value)
    if isinstance(value, bool):
        raise BBLValidationError("non_numeric", "BBL input is a boolean, not a number", value)
    if isinstance(value, int):
        if value < 0:
            raise BBLValidationError("negative", "BBL cannot be negative", value)
        return str(value)
    if isinstance(value, float):
        if value < 0:
            raise BBLValidationError("negative", "BBL cannot be negative", value)
        if not value.is_integer():
            raise BBLValidationError(
                "non_integer_decimal",
                "BBL has a non-zero fractional part; a BBL is an integer identifier",
                value,
            )
        return str(int(value))
    if isinstance(value, str):
        text = value.strip()
        if not text:
            raise BBLValidationError("empty", "BBL input is empty", value)
        if _NEGATIVE_RE.match(text):
            raise BBLValidationError("negative", "BBL cannot be negative", value)
        if not _NUMERIC_RE.match(text):
            raise BBLValidationError(
                "non_numeric", f"BBL {text!r} contains non-numeric characters", value
            )
        if "." in text:
            integer_part, fractional_part = text.split(".", 1)
            if fractional_part.strip("0"):
                raise BBLValidationError(
                    "non_integer_decimal",
                    f"BBL {text!r} has a non-zero fractional part",
                    value,
                )
            # Socrata number-type serialization, e.g. "1000010100.00000000"
            # (G1 finding C6 / fixture F12): all-zero tail is stripped.
            text = integer_part
        return text
    raise BBLValidationError(
        "non_numeric",
        f"BBL input type {type(value).__name__} is not supported",
        value,
    )


def normalize_bbl(value: object) -> NormalizedBBL:
    """Normalize any supported BBL representation to the canonical 10-digit string.

    Raises :class:`BBLValidationError` naming the exact defect for malformed
    input. Deterministic: identical input always yields identical output.
    """
    digits = _digits_from_input(value)
    if len(digits) != 10:
        raise BBLValidationError(
            "wrong_length",
            f"BBL must be exactly 10 digits; got {len(digits)} digits ({digits!r})",
            value,
        )
    borough = int(digits[0])
    if not 1 <= borough <= 5:
        raise BBLValidationError(
            "invalid_borough",
            f"BBL borough digit must be 1-5 (Manhattan..Staten Island); got {digits[0]!r}",
            value,
        )
    block = int(digits[1:6])
    if not 1 <= block <= 99999:
        raise BBLValidationError(
            "invalid_block",
            f"BBL tax block must be 1-99999; got {digits[1:6]!r}",
            value,
        )
    lot = int(digits[6:10])
    if not 1 <= lot <= 9999:
        raise BBLValidationError(
            "invalid_lot",
            f"BBL tax lot must be 1-9999; got {digits[6:10]!r}",
            value,
        )
    canonical = digits
    if not _CANONICAL_RE.match(canonical):  # defense in depth; unreachable if above holds
        raise BBLValidationError(
            "wrong_length", f"BBL {canonical!r} failed canonical pattern", value
        )
    return NormalizedBBL(canonical=canonical, raw=value, borough=borough, block=block, lot=lot)


def bbl_from_components(borough: object, block: object, lot: object) -> str:
    """Assemble the canonical BBL from borough/block/lot per dictionary p.38.

    Components may be ints or numeric strings (including Socrata decimal-zero
    tails). Zero-pads block to 5 and lot to 4.
    """
    parts = {}
    for name, raw, limit in (("borough", borough, 5), ("block", block, 99999), ("lot", lot, 9999)):
        digits = _digits_from_input(raw)
        number = int(digits)
        low = 1
        if not low <= number <= limit:
            raise BBLValidationError(
                "invalid_component",
                f"BBL {name} must be {low}-{limit}; got {raw!r}",
                raw,
            )
        parts[name] = number
    return f"{parts['borough']}{parts['block']:05d}{parts['lot']:04d}"


def check_identifier_consistency(
    canonical_bbl: str,
    *,
    borocode: object = None,
    block: object = None,
    lot: object = None,
) -> list[dict]:
    """Detect disagreement between a BBL and separate borocode/block/lot values.

    Returns a list of conflict dicts (empty when consistent). Values that
    cannot be parsed at all are reported as conflicts too - a source record
    whose components are unreadable must never be silently trusted.
    Nothing is resolved here: both values are surfaced verbatim (PRD section 9,
    conflicts stay visible).
    """
    normalized = normalize_bbl(canonical_bbl)
    expected = {
        "borocode": normalized.borough,
        "block": normalized.block,
        "lot": normalized.lot,
    }
    conflicts: list[dict] = []
    for field, provided in (("borocode", borocode), ("block", block), ("lot", lot)):
        if provided is None:
            continue
        try:
            provided_int = int(_digits_from_input(provided))
        except BBLValidationError as exc:
            conflicts.append(
                {
                    "field": field,
                    "bbl_derived_value": expected[field],
                    "component_value_raw": provided,
                    "reason": f"component unparseable: {exc.code}",
                }
            )
            continue
        if provided_int != expected[field]:
            conflicts.append(
                {
                    "field": field,
                    "bbl_derived_value": expected[field],
                    "component_value_raw": provided,
                    "component_value_parsed": provided_int,
                    "reason": "bbl and component disagree",
                }
            )
    return conflicts
