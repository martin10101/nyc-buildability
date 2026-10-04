"""The optional scope-beside-the-numbers block for the three-answer generator
(results contract 1.1.0, directive D-090-R108: "put the scope beside the numbers").

The scope block lets the headline cards and the exported drawings visibly state
that the estimate is a "Tax-lot-only estimate", identify the lot (e.g. "Queens
block 7334, lot 70"), and disclose the assumed corner conditions in plain
English, while whole-site development stays unconfirmed and remaining
development capacity stays not confirmed with the owner-settled wording.

Honesty invariants held here:

- The lot identity (borough name, block, lot, display string) is DERIVED
  deterministically from the canonical BBL via the shared
  :func:`app.connectors.bbl.normalize_bbl` helper - never a second BBL parser,
  and never with leading zeros.
- Every disclosed assumption's VALUE and UNIT come from the real generator
  inputs (the lot type, the within-100-ft flag, the street-line angle in
  degrees, the housing program, the floor-to-floor height in feet); its BASIS
  and STATEMENT come from the caller-supplied :class:`ScopeInputs`. The engine
  NEVER invents a basis - every basis is a required field of ``ScopeInputs``.
- The two settled remaining-capacity strings are imported read-only from
  :mod:`app.scenario.constants` (never retyped), and the whole-site statement is
  supplied by the engine (its ``LOT_SELECTION_STATEMENT``), so the settled
  wording cannot drift in two places.

This module imports nothing from :mod:`.engine` or :mod:`.inputs` at runtime (the
``inputs`` annotation is type-checking only), so the package has no import cycle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.connectors.bbl import normalize_bbl
from app.scenario.constants import (
    UNUSED_FLOOR_AREA_NOT_AVAILABLE_REASON_TEXT,
    UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT,
)

if TYPE_CHECKING:  # pragma: no cover - typing only, avoids an inputs<->scope cycle
    from .inputs import ThreeAnswerInputs

__all__ = ["DisclosedAssumption", "ScopeInputs", "build_scope"]

# The emitter's declared scope identity, matching the closed results.schema.json
# scope $defs: basis enum value and the byte-exact label const (D-090-R108).
SCOPE_BASIS = "tax_lot_only"
SCOPE_LABEL = "Tax-lot-only estimate"

# Borough display name by BBL borough code (1-5). This is the
# common.schema.json#/$defs/borough_name enum in its documented order (Geoclient
# User Guide v2.0.4 section 2.2.1; also app/connectors/bbl.py's borough grounding
# and app/profile/builder.py): Manhattan=1, Bronx=2, Brooklyn=3, Queens=4,
# Staten Island=5. The BBL itself is parsed only by normalize_bbl; this is a
# display-name lookup over its validated 1-5 borough code, not a second parser.
_BOROUGH_NAME_BY_CODE: dict[int, str] = {
    1: "Manhattan",
    2: "Bronx",
    3: "Brooklyn",
    4: "Queens",
    5: "Staten Island",
}


@dataclass(frozen=True)
class DisclosedAssumption:
    """The caller's disclosure for ONE assumed condition: its ``basis`` (a
    results.schema.json scope-assumption basis enum value - assumed | entered |
    fixture | city_records | survey_entered | approximate_tax_map | default) and
    its plain-English ``statement``. The engine supplies neither from itself; the
    assumption's value and unit come from the real generator inputs."""

    basis: str
    statement: str


@dataclass(frozen=True)
class ScopeInputs:
    """Everything the scope block needs that is not already a generator input.

    ``bbl`` is the lot's canonical 10-digit BBL; the borough name, block, lot and
    display string are derived from it deterministically by :func:`build_scope`.
    Each remaining field is the caller's :class:`DisclosedAssumption` (basis +
    statement) for one of the five disclosed conditions. All fields are REQUIRED:
    the engine never fabricates a basis or a statement."""

    bbl: str
    lot_type: DisclosedAssumption
    within_100_ft_of_street_line_intersection: DisclosedAssumption
    street_line_intersection_angle_degrees: DisclosedAssumption
    housing_program: DisclosedAssumption
    floor_to_floor_ft: DisclosedAssumption


def _assumption(
    key: str, value: object, unit: str | None, disclosure: DisclosedAssumption
) -> dict:
    """One scope-assumption row: the key and value/unit come from the real input,
    the basis and statement are passed through from the caller's disclosure."""
    return {
        "key": key,
        "value": value,
        "unit": unit,
        "basis": disclosure.basis,
        "statement": disclosure.statement,
    }


def build_scope(inputs: ThreeAnswerInputs, *, lot_selection_statement: str) -> dict:
    """Build the results-1.1.0 ``scope`` object from ``inputs`` (which must carry a
    non-None ``scope_inputs``). The lot identity is derived from the BBL via
    :func:`normalize_bbl`; every assumption's value/unit is read from the real
    inputs and its basis/statement from ``inputs.scope_inputs``.

    ``lot_selection_statement`` is the engine's ``LOT_SELECTION_STATEMENT`` (the
    whole-site statement), passed in so this module needs no engine import."""
    scope_inputs = inputs.scope_inputs
    assert scope_inputs is not None  # caller gates on presence; see engine._assemble_document

    normalized = normalize_bbl(scope_inputs.bbl)
    borough = _BOROUGH_NAME_BY_CODE[normalized.borough]
    # str(int) drops the BBL's zero-padding deterministically (block 07334 -> "7334").
    block = str(normalized.block)
    lot = str(normalized.lot)

    assumptions = [
        _assumption("lot_type", inputs.lot_type, None, scope_inputs.lot_type),
        _assumption(
            "within_100_ft_of_street_line_intersection",
            inputs.within_100_ft_of_street_line_intersection,
            None,
            scope_inputs.within_100_ft_of_street_line_intersection,
        ),
        _assumption(
            "street_line_intersection_angle_degrees",
            inputs.street_line_intersection_angle_degrees,
            "degrees",
            scope_inputs.street_line_intersection_angle_degrees,
        ),
        _assumption(
            "housing_program",
            inputs.housing_program,
            None,
            scope_inputs.housing_program,
        ),
        _assumption(
            "floor_to_floor_ft",
            inputs.building_defaults.floor_to_floor_ft,
            "feet",
            scope_inputs.floor_to_floor_ft,
        ),
    ]

    return {
        "basis": SCOPE_BASIS,
        "label": SCOPE_LABEL,
        "lot": {
            "bbl": normalized.canonical,
            "borough": borough,
            "block": block,
            "lot": lot,
            "display": f"{borough} block {block}, lot {lot}",
        },
        "whole_site": {"status": "unconfirmed", "statement": lot_selection_statement},
        "remaining_capacity": {
            "status": "not_confirmed",
            "label": UNUSED_FLOOR_AREA_NOT_AVAILABLE_TEXT,
            "reason": UNUSED_FLOOR_AREA_NOT_AVAILABLE_REASON_TEXT,
        },
        "assumptions": assumptions,
    }
