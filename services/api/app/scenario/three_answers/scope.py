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
- Every assumed input the engine USES is disclosed - not just the corner
  conditions (D-090-R119, per the owner's reviewer audit). One
  ``assumptions[]`` row is emitted per assumed input in the fixed order of
  :data:`_ASSUMPTION_SPECS` (zoning facts, lot facts, corner condition,
  housing/building default). Each row's VALUE and UNIT come from the real
  generator inputs; its BASIS and STATEMENT come from the caller-supplied
  :class:`ScopeInputs`. The engine NEVER invents a basis - every basis is a
  required field of ``ScopeInputs``, so a caller cannot silently omit one.
- The one input that is NOT an assumption is ``lot_area_sq_ft``: it is a sourced
  site fact (it carries ``lot_area_fact_id`` and travels in
  ``depends_on_fact_ids``), so it belongs with the governing inputs, never here.
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
    from collections.abc import Callable

    from .inputs import ThreeAnswerInputs

__all__ = ["ASSUMPTION_KEYS", "DisclosedAssumption", "ScopeInputs", "build_scope"]

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
    Every OTHER field is the caller's :class:`DisclosedAssumption` (basis +
    statement) for one assumed engine input, named exactly as the key it emits in
    :data:`_ASSUMPTION_SPECS`. ALL fields are REQUIRED (no defaults): omitting any
    one raises ``TypeError`` at construction, so a caller cannot silently leave an
    assumed input undisclosed (D-090-R119), and the engine never fabricates a
    basis or a statement. ``lot_area_sq_ft`` is deliberately absent - it is a
    sourced site fact, not an assumption."""

    bbl: str
    # zoning facts
    zoning_district: DisclosedAssumption
    overlay_present: DisclosedAssumption
    special_district_present: DisclosedAssumption
    special_density_area: DisclosedAssumption
    # lot facts (the recorded lot AREA is a sourced fact, so it is not here)
    lot_type: DisclosedAssumption
    lot_front_ft: DisclosedAssumption
    lot_depth_ft: DisclosedAssumption
    site_measurement_rank: DisclosedAssumption
    # corner condition
    within_100_ft_of_street_line_intersection: DisclosedAssumption
    street_line_intersection_angle_degrees: DisclosedAssumption
    # housing / building default
    housing_program: DisclosedAssumption
    floor_to_floor_ft: DisclosedAssumption


# The fixed, documented order in which assumed inputs are disclosed in
# scope.assumptions (D-090-R119, per the owner's reviewer audit: EVERY assumed
# input the engine actually uses is disclosed). Each tuple is
# (key, value_reader, unit): the key names the row AND the matching required
# DisclosedAssumption field of ScopeInputs (same name); the reader pulls the real
# value from the generator inputs; the unit is the value's unit in plain words, or
# None for a dimensionless flag/type/string. Grouped zoning -> lot -> corner
# condition -> building. lot_area_sq_ft is NOT here: it is the one sourced site
# fact (lot_area_fact_id / depends_on_fact_ids), so it travels with the governing
# inputs, never as an assumption.
_ASSUMPTION_SPECS: tuple[
    tuple[str, Callable[[ThreeAnswerInputs], object], str | None], ...
] = (
    ("zoning_district", lambda i: i.zoning_district, None),
    ("overlay_present", lambda i: i.overlay_present, None),
    ("special_district_present", lambda i: i.special_district_present, None),
    ("special_density_area", lambda i: i.special_density_area, None),
    ("lot_type", lambda i: i.lot_type, None),
    ("lot_front_ft", lambda i: i.lot_front_ft, "feet"),
    ("lot_depth_ft", lambda i: i.lot_depth_ft, "feet"),
    ("site_measurement_rank", lambda i: i.site_measurement_rank, None),
    (
        "within_100_ft_of_street_line_intersection",
        lambda i: i.within_100_ft_of_street_line_intersection,
        None,
    ),
    (
        "street_line_intersection_angle_degrees",
        lambda i: i.street_line_intersection_angle_degrees,
        "degrees",
    ),
    ("housing_program", lambda i: i.housing_program, None),
    ("floor_to_floor_ft", lambda i: i.building_defaults.floor_to_floor_ft, "feet"),
)

# The disclosed assumed-input keys, in emission order. Equals the ScopeInputs
# DisclosedAssumption field names; exported so callers and tests derive the set
# from this single source of truth, never a hand-maintained list.
ASSUMPTION_KEYS: tuple[str, ...] = tuple(key for key, _reader, _unit in _ASSUMPTION_SPECS)

# The JSON scalar types the results.schema.json scope_assumption `value` allows
# (string | number | boolean). bool is a subclass of int, so it is covered.
_SCOPE_VALUE_TYPES = (str, int, float)


def _require_disclosure(scope_inputs: ScopeInputs, key: str) -> DisclosedAssumption:
    """Return the caller's disclosure for one assumed input, failing closed if it
    is missing. ScopeInputs makes every disclosure a required field, so a missing
    one already raises at construction; this is the second, explicit guard against
    a caller that passes None in its place (D-090-R119: never silently omit one)."""
    disclosure = getattr(scope_inputs, key)
    if not isinstance(disclosure, DisclosedAssumption):
        raise ValueError(
            f"scope_inputs is missing the required disclosure for assumed input {key!r}"
        )
    return disclosure


def _assumption(
    key: str, value: object, unit: str | None, disclosure: DisclosedAssumption
) -> dict:
    """One scope-assumption row: the key and value/unit come from the real input,
    the basis and statement are passed through from the caller's disclosure. The
    value must be a JSON scalar (string/number/boolean) the schema admits; a None
    or other value fails closed rather than emitting an invalid row."""
    if not isinstance(value, _SCOPE_VALUE_TYPES):
        raise ValueError(
            f"assumed input {key!r} has no disclosable value (got {value!r}); "
            "the scope contract allows only a string, number or boolean"
        )
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

    # One row per assumed engine input, in the fixed _ASSUMPTION_SPECS order:
    # value/unit from the real inputs, basis/statement from the required disclosure
    # of the same name (D-090-R119).
    assumptions = [
        _assumption(key, reader(inputs), unit, _require_disclosure(scope_inputs, key))
        for key, reader, unit in _ASSUMPTION_SPECS
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
