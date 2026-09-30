"""Real-property request guard (queue C-04, plan task M1-06a; plan section 9 "No example data in
real work").

A request is a REAL-PROPERTY request when its ``lot`` carries a ``bbl`` (any value other than
``null`` or a blank string - a malformed BBL is still a claim that the request is about a real
lot, so the guard applies; stricter is the safe side). For such a request, on
``POST /api/v1/proposal-checks`` and ``POST /api/v1/max-envelope``, this module refuses:

1. ``example`` that is present but not a boolean (``example_marker_not_boolean``).
2. The known EXAMPLE-SITE signature - the web's former ``rectangleSampleDraft``
   (``apps/web/src/lib/architect/proposal-draft.ts``): the fact triple district ``R5`` + lot area
   8,000 sq ft + street class ``wide`` all together, or its fake EPSG:2263 outline corners, or
   its fake lot line - unless the request says ``"example": true``
   (``example_site_values_on_real_property``).
3. A caller-attested value without a provenance label from the closed vocabulary of the
   site_fact contract's measurement ranks (``packages/contracts/schemas/v1/site_fact.schema.json``,
   ``$defs.measurement_*``): the lot area (``lot.area_provenance.rank``), every
   ``lot_rule_facts`` entry (``lot_rule_facts_provenance.<key>.rank``) and every street line
   (``lot.street_lines[i].attestation.rank``). Missing / blank / non-string ->
   ``provenance_rank_missing``; outside the vocabulary -> ``provenance_rank_not_in_vocabulary``;
   ``unknown`` beside a value -> ``provenance_rank_unknown_with_value`` (site_fact: an unknown has
   a null value, never a number); a provenance holder that is not an object ->
   ``provenance_not_an_object``.

Requests without a BBL are untouched, so today's clients are unchanged. The whole guard is OFF
unless ``LANE_C_ENABLED`` holds an explicit true token (:func:`real_property_guard_enabled`;
absent / unknown -> off, the lane-flag rule).

Every refusal is a :class:`RealPropertyRefusal` - a ``_FieldRefusal`` (so the routes' existing
``except`` maps it to ``(422, "validation_error")`` naming the exact ``field``) that also carries
a machine-readable ``reason`` from :data:`REAL_PROPERTY_GUARD_REASONS`. Messages never echo a
caller value. Pure and side-effect free; it reads only already-parsed, size-bounded JSON.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.api.v1._proposal_fact_domains import _FieldRefusal
from app.config import lane_enabled

__all__ = [
    "EXAMPLE_LOT_AREA_SQ_FT",
    "EXAMPLE_LOT_LINE_ENDPOINTS",
    "EXAMPLE_OUTLINE_CORNERS",
    "EXAMPLE_STREET_WIDTH_CLASS",
    "EXAMPLE_ZONING_DISTRICT",
    "KNOWN_VALUE_RANKS",
    "MEASUREMENT_RANKS",
    "REAL_PROPERTY_GUARD_REASONS",
    "REASON_EXAMPLE_MARKER_NOT_BOOLEAN",
    "REASON_EXAMPLE_VALUES",
    "REASON_PROVENANCE_NOT_AN_OBJECT",
    "REASON_RANK_MISSING",
    "REASON_RANK_NOT_IN_VOCABULARY",
    "REASON_RANK_UNKNOWN_WITH_VALUE",
    "RealPropertyRefusal",
    "guard_real_property_request",
    "is_real_property_request",
    "real_property_guard_enabled",
]

# --- machine-readable refusal reasons (closed vocabulary) --------------------------------------
REASON_EXAMPLE_MARKER_NOT_BOOLEAN = "example_marker_not_boolean"
REASON_EXAMPLE_VALUES = "example_site_values_on_real_property"
REASON_PROVENANCE_NOT_AN_OBJECT = "provenance_not_an_object"
REASON_RANK_MISSING = "provenance_rank_missing"
REASON_RANK_NOT_IN_VOCABULARY = "provenance_rank_not_in_vocabulary"
REASON_RANK_UNKNOWN_WITH_VALUE = "provenance_rank_unknown_with_value"

REAL_PROPERTY_GUARD_REASONS: frozenset[str] = frozenset(
    {
        REASON_EXAMPLE_MARKER_NOT_BOOLEAN,
        REASON_EXAMPLE_VALUES,
        REASON_PROVENANCE_NOT_AN_OBJECT,
        REASON_RANK_MISSING,
        REASON_RANK_NOT_IN_VOCABULARY,
        REASON_RANK_UNKNOWN_WITH_VALUE,
    }
)

# --- provenance vocabulary: the site_fact measurement ranks (plan section 4 source order) ------
#: The site_fact contract's six ranks, in its order. A test pins this tuple to the schema's
#: ``$defs.measurement_*`` rank constants so the two can never drift apart.
MEASUREMENT_RANKS: tuple[str, ...] = (
    "survey_entered",
    "city_records",
    "approximate_tax_map",
    "entered",
    "assumed",
    "unknown",
)
#: The ranks a supplied (non-null) value may carry: every rank except ``unknown``.
KNOWN_VALUE_RANKS: tuple[str, ...] = tuple(r for r in MEASUREMENT_RANKS if r != "unknown")

_RANK_KEY = "rank"

# --- the example-site signature (apps/web/src/lib/architect/proposal-draft.ts) -----------------
#: ``rectangleSampleDraft()``: a fictional 8,000 sq ft R5 lot on a wide street, with a fake
#: 100 ft x 50 ft EPSG:2263 building outline and one fake lot line. Values copied verbatim.
EXAMPLE_ZONING_DISTRICT = "R5"
EXAMPLE_LOT_AREA_SQ_FT = 8000.0
EXAMPLE_STREET_WIDTH_CLASS = "wide"
EXAMPLE_OUTLINE_CORNERS: frozenset[tuple[float, float]] = frozenset(
    {
        (1000000.0, 200000.0),
        (1000100.0, 200000.0),
        (1000100.0, 200050.0),
        (1000000.0, 200050.0),
    }
)
EXAMPLE_LOT_LINE_ENDPOINTS: frozenset[tuple[float, float]] = frozenset(
    {(999990.0, 199990.0), (999990.0, 200060.0)}
)


class RealPropertyRefusal(_FieldRefusal):
    """A guard refusal: the exact ``field`` plus a machine-readable ``reason``."""

    def __init__(self, message: str, *, field: str, reason: str) -> None:
        super().__init__(message, field=field)
        self.reason = reason


def real_property_guard_enabled(env: Mapping[str, str] | None = None) -> bool:
    """Lane C flag (``LANE_C_ENABLED``): absent / empty / unknown -> off (fail safe)."""
    return lane_enabled("C", env)


def is_real_property_request(lot: Mapping[str, Any]) -> bool:
    """True when ``lot.bbl`` is present and is not ``null`` or a blank string."""
    if "bbl" not in lot:
        return False
    bbl = lot["bbl"]
    if bbl is None:
        return False
    return not (isinstance(bbl, str) and not bbl.strip())


def guard_real_property_request(
    body: Mapping[str, Any],
    *,
    lot: Mapping[str, Any],
    lot_rule_facts: Mapping[str, Any],
    proposed_massing: Mapping[str, Any] | None = None,
) -> None:
    """Apply the guard to one parsed request (a no-op unless it is a real-property request).
    Raises :class:`RealPropertyRefusal` on the first failing check, in the order listed in the
    module docstring. The caller has already shape-checked ``lot`` / ``lot_rule_facts`` /
    ``proposed_massing`` as objects and type-checked the mapped fact values."""
    if not is_real_property_request(lot):
        return
    example = body.get("example", False)
    if not isinstance(example, bool):
        raise RealPropertyRefusal(
            "example must be a boolean when present",
            field="example",
            reason=REASON_EXAMPLE_MARKER_NOT_BOOLEAN,
        )
    if not example:
        _refuse_example_signature(lot, lot_rule_facts, proposed_massing)
    _require_ranks(body, lot, lot_rule_facts)


# --- example signature ---------------------------------------------------------------------------
def _example_refusal(field: str, what: str) -> RealPropertyRefusal:
    return RealPropertyRefusal(
        f"{what} match the built-in example site (plan section 9: no example data in real "
        "work); a request for a real property (lot.bbl present) cannot use them. Send the "
        "property's own values, or mark a demo request \"example\": true",
        field=field,
        reason=REASON_EXAMPLE_VALUES,
    )


def _refuse_example_signature(
    lot: Mapping[str, Any],
    lot_rule_facts: Mapping[str, Any],
    proposed_massing: Mapping[str, Any] | None,
) -> None:
    if _facts_match_example(lot, lot_rule_facts):
        raise _example_refusal(
            "lot_rule_facts", "the lot area, zoning district and street width class together"
        )
    if isinstance(proposed_massing, Mapping):
        outlines = [("proposed_massing.outline.vertices", proposed_massing.get("outline"))]
        levels = proposed_massing.get("levels")
        if isinstance(levels, list):
            outlines += [
                (f"proposed_massing.levels[{i}].outline.vertices", level.get("outline"))
                for i, level in enumerate(levels)
                if isinstance(level, Mapping)
            ]
        for field, outline in outlines:
            if _corner_set(outline) == EXAMPLE_OUTLINE_CORNERS:
                raise _example_refusal(field, "the outline vertices")
    segments = lot.get("lot_line_segments")
    if isinstance(segments, list):
        for idx, seg in enumerate(segments):
            if isinstance(seg, Mapping) and _segment_endpoints(seg) == EXAMPLE_LOT_LINE_ENDPOINTS:
                raise _example_refusal(f"lot.lot_line_segments[{idx}]", "the lot line endpoints")


def _facts_match_example(lot: Mapping[str, Any], facts: Mapping[str, Any]) -> bool:
    area = lot.get("area_sq_ft")
    district = facts.get("zoning_district")
    street = facts.get("street_width_class")
    return (
        _is_number(area)
        and float(area) == EXAMPLE_LOT_AREA_SQ_FT
        and isinstance(district, str)
        and district.strip().upper() == EXAMPLE_ZONING_DISTRICT
        and isinstance(street, str)
        and street.strip().lower() == EXAMPLE_STREET_WIDTH_CLASS
    )


def _is_number(value: object) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _point(value: object) -> tuple[float, float] | None:
    if isinstance(value, list | tuple) and len(value) == 2 and all(map(_is_number, value)):
        return (float(value[0]), float(value[1]))
    return None


def _corner_set(outline: object) -> frozenset[tuple[float, float]] | None:
    """The distinct vertices of an ``{"vertices": [[x, y], ...]}`` outline, or ``None`` when the
    shape is not that (the block validator owns shape refusals)."""
    if not isinstance(outline, Mapping):
        return None
    vertices = outline.get("vertices")
    if not isinstance(vertices, list):
        return None
    points = [_point(v) for v in vertices]
    if any(p is None for p in points):
        return None
    return frozenset(p for p in points if p is not None)


def _segment_endpoints(seg: Mapping[str, Any]) -> frozenset[tuple[float, float]] | None:
    start, end = _point(seg.get("start")), _point(seg.get("end"))
    if start is None or end is None:
        return None
    return frozenset({start, end})


# --- provenance ranks ----------------------------------------------------------------------------
def _require_ranks(
    body: Mapping[str, Any], lot: Mapping[str, Any], lot_rule_facts: Mapping[str, Any]
) -> None:
    if lot.get("area_sq_ft") is not None:
        _require_rank(lot.get("area_provenance"), "lot.area_provenance", has_value=True)
    if lot_rule_facts:
        holder = body.get("lot_rule_facts_provenance")
        if holder is not None and not isinstance(holder, Mapping):
            raise RealPropertyRefusal(
                "lot_rule_facts_provenance must be an object with one {\"rank\": ...} entry per "
                "lot_rule_facts key",
                field="lot_rule_facts_provenance",
                reason=REASON_PROVENANCE_NOT_AN_OBJECT,
            )
        for key, value in lot_rule_facts.items():
            _require_rank(
                None if holder is None else holder.get(key),
                f"lot_rule_facts_provenance.{key}",
                has_value=value is not None,
            )
    streets = lot.get("street_lines")
    if isinstance(streets, list):
        for idx, line in enumerate(streets):
            if isinstance(line, Mapping):
                _require_rank(
                    line.get("attestation"), f"lot.street_lines[{idx}].attestation", has_value=True
                )


def _require_rank(provenance: object, field: str, *, has_value: bool) -> None:
    """``provenance`` must be an object whose ``rank`` is one of :data:`MEASUREMENT_RANKS`, and a
    supplied value may not carry ``unknown``. An absent holder (``None``) reads as a missing rank.
    The refusal never echoes the offending rank."""
    if provenance is not None and not isinstance(provenance, Mapping):
        raise RealPropertyRefusal(
            f"{field} must be an object carrying a \"rank\"",
            field=field,
            reason=REASON_PROVENANCE_NOT_AN_OBJECT,
        )
    rank_field = f"{field}.{_RANK_KEY}"
    rank = None if provenance is None else provenance.get(_RANK_KEY)
    if not isinstance(rank, str) or not rank.strip():
        raise RealPropertyRefusal(
            f"{rank_field} is required for a caller-attested value on a real-property request; "
            f"one of {list(MEASUREMENT_RANKS)}",
            field=rank_field,
            reason=REASON_RANK_MISSING,
        )
    if rank not in MEASUREMENT_RANKS:
        raise RealPropertyRefusal(
            f"{rank_field} is not a site_fact measurement rank; one of {list(MEASUREMENT_RANKS)}",
            field=rank_field,
            reason=REASON_RANK_NOT_IN_VOCABULARY,
        )
    if rank == "unknown" and has_value:
        raise RealPropertyRefusal(
            f"{rank_field} is \"unknown\" but a value was supplied; an unknown value is sent as "
            f"null, a supplied value carries one of {list(KNOWN_VALUE_RANKS)}",
            field=rank_field,
            reason=REASON_RANK_UNKNOWN_WITH_VALUE,
        )
