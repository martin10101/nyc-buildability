"""The ZR envelope constraints from research record NB-06 - the street wall, the setback
above the base, and the side yard - combined into the contract-1.5.0 envelope_rows block, its
constraint_lines and its input_facts (task M5-T170).

This is the SCENARIO layer. It holds the captured legal readings of NB-06 (overlay-reading.json
rows setback-above-base and street-wall-location; real-lot.json; the ZR snapshots) and turns the
facts the decision step gathered - whether a commercial overlay is mapped, the building type, the
per-frontage wide / narrow class (from the ACCEPTED D-052 classifier, never re-derived here), the
building street-wall height against the maximum base height, and whether an operative street line
is known - into the additive 1.5.0 blocks. Every text is a plain, labelled DRAFT reading: no
internal name, no record id, no task id, never "professional review", never a statement about
which law text is "captured" or "built". Expected outcomes come from the R6B reference case and
the law, never a program run.

THREE RULES (result-deciding).
(1) No default stands for a fact. A frontage whose width class is unresolved or unknown never
    becomes narrow (D-051: the street-wall offset without the overlay is 8 ft on a wide frontage
    but 10 ft on a narrow one, so "narrow" is not the safe side); its setback depth is withheld.
    A building type not stated is never taken as residential-only (23-335(b) "no side yard" would
    then be assumed, while a single- or two-family detached residence needs two 5-ft side yards).
    Whether a commercial overlay is mapped decides the street-wall rule; when it is not read the
    rule is held conditional, never defaulted.
(2) One state per input. The street wall always applies (a street-wall location rule governs any
    building with a street frontage), Conditional on the prevailing-frontage test and the
    operative street line. The setback is keyed on the building street-wall height against the
    maximum base height: at or below it the setback is not triggered (not_applicable), strictly
    above it the setback applies. The side yard is none required for all residences other than a
    single- or two-family detached one (and for any residential building in the overlay), two
    5-ft yards for a detached one- or two-family residence without the overlay.
(3) A not_known row carries NO number (schema oneOf); a constraint line is drawn only when its
    geometry AND basis are established (D-094-R017): without an operative street line the bands
    are not_established and carry no geometry.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from app.connectors.dcm_street_width_policy import (
    DECISION_NARROW,
    DECISION_UNKNOWN,
    DECISION_UNRESOLVED,
    DECISION_WIDE,
)

__all__ = [
    "BUILDING_MIXED",
    "BUILDING_MULTI_FAMILY",
    "BUILDING_RESIDENTIAL_ONLY",
    "BUILDING_SINGLE_TWO_FAMILY_DETACHED",
    "MAX_BASE_HEIGHT_R6B_FT",
    "SETBACK_DEPTH_NARROW_FT",
    "SETBACK_DEPTH_WIDE_FT",
    "SIDE_YARD_OPEN_AREA_MIN_FT",
    "STREET_WALL_OFFSET_FT",
    "STREET_WALL_OFFSET_NARROW_NO_OVERLAY_FT",
    "WIDTH_NARROW",
    "WIDTH_UNKNOWN",
    "WIDTH_UNRESOLVED",
    "WIDTH_WIDE",
    "EnvelopeAnalysis",
    "Frontage",
    "build_envelope_analysis",
    "setback_value_state_from_row",
]

_SETBACK_LABEL = "Setback above the base"

_DOB = "Not a determination by the Department of Buildings."

# The per-frontage width class mirrors the ACCEPTED D-052 policy decision states exactly; this
# module never re-derives a width (the bridge runs the classifier through
# app.spatial.frontage_street_width.derive_frontage_street_widths).
WIDTH_WIDE = DECISION_WIDE
WIDTH_NARROW = DECISION_NARROW
WIDTH_UNRESOLVED = DECISION_UNRESOLVED
WIDTH_UNKNOWN = DECISION_UNKNOWN

# Building types. None means the building type was not stated, which is never read as any one of
# these (RULE 1).
BUILDING_RESIDENTIAL_ONLY = "residential_only"
BUILDING_MIXED = "mixed"
BUILDING_MULTI_FAMILY = "multi_family"
BUILDING_SINGLE_TWO_FAMILY_DETACHED = "single_two_family_detached"
_RESIDENCE_MULTI = (BUILDING_RESIDENTIAL_ONLY, BUILDING_MIXED, BUILDING_MULTI_FAMILY)

# Legal numbers, each from a captured reading (NB-06; overlay-reading.json). The module derives
# none of them.
STREET_WALL_OFFSET_FT = 8.0  # ZR 35-631(b) / 23-431(b) wide: within 8 ft of the street line
STREET_WALL_OFFSET_NARROW_NO_OVERLAY_FT = 10.0  # ZR 23-431(b) narrow: within 10 ft (D-051)
SETBACK_DEPTH_WIDE_FT = 10.0  # ZR 23-433: at least 10 ft from a wide-street wall
SETBACK_DEPTH_NARROW_FT = 15.0  # ZR 23-433: at least 15 ft from a narrow-street wall
SIDE_YARD_OPEN_AREA_MIN_FT = 5.0  # ZR 23-335(b) / 34-232: an open area must be at least 5 ft wide
_DETACHED_SIDE_YARD_FT = 5.0  # ZR 23-335(a): two side yards each at least 5 ft wide
MAX_BASE_HEIGHT_R6B_FT = 45.0  # ZR 23-432 R6B row, standard residences (the setback trigger)

_ZR_STREET_WALL_OVERLAY = ["ZR 35-631"]
_ZR_STREET_WALL_PLAIN = ["ZR 23-431"]
_ZR_SETBACK_OVERLAY = ["ZR 23-433", "ZR 35-632"]
_ZR_SETBACK_PLAIN = ["ZR 23-433"]
_ZR_SIDE_YARD = ["ZR 23-335"]
_ZR_SIDE_YARD_OVERLAY = ["ZR 23-335", "ZR 34-232"]


@dataclass(frozen=True)
class Frontage:
    """One street frontage of the lot with its D-052 wide / narrow class. ``width_class`` is one
    of the four D-052 decision states; ``mapped_width_ft`` is the mapped width emitted as an
    input_fact (basis gis) only when a number was read."""

    name: str
    width_class: str
    mapped_width_ft: float | None = None


@dataclass(frozen=True)
class EnvelopeAnalysis:
    """The additive contract-1.5.0 envelope emission: the envelope_rows (street wall, setback,
    side yard), the constraint_lines (street_wall_band and setback_line) and the input_facts.
    Attached to the document by :func:`three_way_document.emit_three_way_document`."""

    envelope_rows: list[dict] = field(default_factory=list)
    constraint_lines: list[dict] = field(default_factory=list)
    input_facts: list[dict] = field(default_factory=list)


def _prevailing_frontage_condition() -> dict:
    return {
        "kind": "unchecked_condition",
        "assumption": (
            "If no block frontage has a prevailing street wall further from the street line than "
            "the rule's own eight feet (which could instead line the street wall up with the "
            "existing adjacent buildings)"
        ),
        "settled_by": (
            "A survey of the existing street walls on each block frontage within 150 feet of the "
            "building"
        ),
    }


def _operative_street_line_condition() -> dict:
    return {
        "kind": "unchecked_condition",
        "assumption": (
            "If the operative street line is confirmed: the eight feet are measured from the "
            "street line, and a mapped street width does not by itself fix where that line sits"
        ),
        "settled_by": "A survey or the approved plan that fixes the street line",
    }


def _building_type_condition() -> dict:
    return {
        "kind": "unchecked_condition",
        "assumption": (
            "If the building is a new all-residential building: a building that is partly "
            "commercial reaches the same rule here by a different route, which was not confirmed"
        ),
        "settled_by": "A stated building type (all-residential, or partly commercial)",
    }


def _overlay_offset_name(name: str) -> str:
    return f"Street wall within this distance of the {name} street line"


def _street_wall_check(
    overlay_present: bool | None,
    building_type: str | None,
    frontages: Sequence[Frontage],
) -> dict:
    """ZR street-wall location. It always applies; the rule and the distance depend on whether a
    commercial overlay is mapped. With the overlay (ZR 35-631(b), reached by 35-63 for a mixed
    building via 35-01 and for an all-residential building via 34-11 and 34-24(b)(1)) the street
    wall sits within 8 ft of each street line, wide or narrow alike. Without the overlay (plain
    R6B, ZR 23-431(b)) it sits within 8 ft of a wide-street line but 10 ft of a narrow-street line
    - the D-051 asymmetry, never collapsed - and a frontage whose width class is unresolved or
    unknown carries no distance (never narrow by default). Conditional on the prevailing-frontage
    test and the operative street line."""
    conditions = [_prevailing_frontage_condition(), _operative_street_line_condition()]
    values: list[dict] = []
    if overlay_present is True:
        zr = list(_ZR_STREET_WALL_OVERLAY)
        # The pathway to 35-631(b) differs by building type (35-01 for a mixed building; 34-11 and
        # 34-24(b)(1) for an all-residential one); cited here as a single operative section so page
        # 3 stays concise (the full pathway is in NB-06 and the rule file).
        zr += ["ZR 35-01"] if building_type == BUILDING_MIXED else ["ZR 34-24"]
        if building_type is None:
            conditions.append(_building_type_condition())
        for f in frontages:
            values.append({"name": _overlay_offset_name(f.name), "value": STREET_WALL_OFFSET_FT,
                           "unit": "ft"})
        text = "A conditional reading of the street-wall location."
        return _applies_row("street_wall", values, conditions, text, zr)
    if overlay_present is False:
        zr = list(_ZR_STREET_WALL_PLAIN)
        for f in frontages:
            offset = _no_overlay_offset(f.width_class)
            if offset is not None:
                values.append({"name": _overlay_offset_name(f.name), "value": offset,
                               "unit": "ft"})
        if any(_no_overlay_offset(f.width_class) is None for f in frontages):
            conditions.append(_width_condition())
        text = "A conditional reading of the street-wall location under ZR 23-431."
        return _applies_row("street_wall", values, conditions, text, zr)
    # The overlay was not read: the rule depends on whether a commercial overlay is mapped, so no
    # distance is shown and the dependency is a named condition (RULE 1, never defaulted).
    conditions.append(_overlay_condition())
    zr = list(_ZR_STREET_WALL_OVERLAY) + list(_ZR_STREET_WALL_PLAIN)
    text = "A conditional reading of the street-wall location (the rule depends on the overlay)."
    return _applies_row("street_wall", values, conditions, text, zr)


def _no_overlay_offset(width_class: str) -> float | None:
    """The plain-R6B street-wall distance (ZR 23-431(b)): 8 ft on a wide frontage, 10 ft on a
    narrow one; None when the width class is unresolved or unknown (never narrow by default)."""
    if width_class == WIDTH_WIDE:
        return STREET_WALL_OFFSET_FT
    if width_class == WIDTH_NARROW:
        return STREET_WALL_OFFSET_NARROW_NO_OVERLAY_FT
    return None


def _overlay_condition() -> dict:
    return {
        "kind": "unchecked_condition",
        "assumption": "If whether a commercial overlay is mapped is confirmed",
        "settled_by": "Reading the commercial-overlay column of the city record for this lot",
    }


def _width_condition() -> dict:
    return {
        "kind": "unchecked_condition",
        "assumption": (
            "If each street's width class is settled: a frontage whose mapped width does not "
            "settle the wide-or-narrow question shows no distance, because the two distances "
            "differ and narrow is not the safe side"
        ),
        "settled_by": "A settled mapped width for each frontage, checked against the ZR 12-10 "
                      "wide-street exceptions",
    }


def _setback_depth(width_class: str) -> float | None:
    """ZR 23-433 setback depth above the maximum base height: 10 ft from a wide-street wall, 15 ft
    from a narrow-street wall; None when the width class is unresolved or unknown (never narrow by
    default, D-051)."""
    if width_class == WIDTH_WIDE:
        return SETBACK_DEPTH_WIDE_FT
    if width_class == WIDTH_NARROW:
        return SETBACK_DEPTH_NARROW_FT
    return None


def _setback_name(name: str) -> str:
    return f"Setback depth above the maximum base height on the {name} frontage"


def _setback_values(frontages: Sequence[Frontage]) -> tuple[list[dict], bool]:
    """The per-frontage setback depths (10 ft wide / 15 ft narrow); a frontage whose width class
    is unresolved or unknown carries no depth. Returns the values and whether any depth was
    withheld."""
    values: list[dict] = []
    any_withheld = False
    for f in frontages:
        depth = _setback_depth(f.width_class)
        if depth is None:
            any_withheld = True
        else:
            values.append({"name": _setback_name(f.name), "value": depth, "unit": "ft"})
    return values, any_withheld


def _setback_triggered(street_wall_height_ft: float | None,
                       max_base_height_ft: float | None) -> bool | None:
    """Whether the setback is triggered: the building street wall STRICTLY exceeds the maximum
    base height (ZR 23-432 / 35-632(a); the setback is required only 'for portions of a building
    street wall that exceed the maximum base height'). None when either height is not known. At
    the maximum base height the setback is not triggered (44.99, 45.00 are not above 45.00; 45.01
    is)."""
    if street_wall_height_ft is None or max_base_height_ft is None:
        return None
    return street_wall_height_ft > max_base_height_ft


def _setback_check(
    overlay_present: bool | None,
    frontages: Sequence[Frontage],
    street_wall_height_ft: float | None,
    max_base_height_ft: float | None,
) -> dict:
    """ZR 23-433 setback above the base (reached by 23-432 without the overlay, by 35-632(a) with
    it). The setback is required only for the part of a building street wall above the maximum base
    height. The width class sets only the depth (10 ft wide / 15 ft narrow); a frontage whose width
    is unresolved or unknown withholds its depth (never narrow by default)."""
    zr = list(_ZR_SETBACK_OVERLAY) if overlay_present else list(_ZR_SETBACK_PLAIN)
    values, any_withheld = _setback_values(frontages)
    conditions: list[dict] = []
    if any_withheld:
        conditions.append(_width_condition())
    triggered = _setback_triggered(street_wall_height_ft, max_base_height_ft)
    base = max_base_height_ft
    if triggered is True:
        conditions.append(_setback_depth_minimum_condition())
        text = "A conditional reading: a setback above the base applies."
        return _applies_row("setback", values, conditions, text, zr)
    if triggered is False:
        conditions.append(_above_base_condition(base))
        text = "A conditional reading: no setback above the base is required."
        return _not_applicable_row("setback", values, conditions, text, zr)
    # The building street-wall height (or the maximum base height) was not stated: the law is
    # known (a setback above the maximum base height), but whether this building reaches above it
    # is a named condition, never read as "no setback" (RULE 1 / R061).
    conditions.append(_above_base_condition(base))
    text = "A conditional reading of the setback above the base."
    return _applies_row("setback", values, conditions, text, zr)


def _setback_depth_minimum_condition() -> dict:
    return {
        "kind": "unchecked_condition",
        "assumption": (
            "The 10-foot and 15-foot depths are the least the setback must be; ZR 23-433(a) to "
            "(d) may reduce or waive them (for example where part of the wall is far enough from "
            "the street line)"
        ),
        "settled_by": "The building design checked against ZR 23-433(a) to (d)",
    }


def _above_base_condition(max_base_height_ft: float | None) -> dict:
    where = f"the {_ft(max_base_height_ft)} maximum base height" if max_base_height_ft is not None \
        else "the maximum base height"
    return {
        "kind": "unchecked_condition",
        "assumption": f"If any part of the building street wall rises above {where}",
        "settled_by": "The building's street-wall height against the maximum base height",
    }


def _side_yard_check(
    overlay_present: bool | None,
    building_type: str | None,
    open_area_provided: bool,
) -> dict:
    """ZR 23-335 side yards in R6 through R12 (34-232 in a commercial overlay). No side yard is
    required for any residence other than a single- or two-family detached one (23-335(b)); in the
    overlay no side yard is required for any residential building (34-232). A single- or two-family
    detached residence needs two side yards each at least 5 feet wide without the overlay
    (23-335(a)). Any open area along a side lot line, if provided, must be at least 5 feet wide."""
    zr = list(_ZR_SIDE_YARD_OVERLAY) if overlay_present else list(_ZR_SIDE_YARD)
    open_note = _open_area_condition()
    if building_type == BUILDING_SINGLE_TWO_FAMILY_DETACHED:
        if overlay_present is True:
            text = "A draft reading: no side yard is required under ZR 34-232."
            return _not_applicable_row("side_yard", [], [open_note], text, zr)
        text = "A draft reading: two side yards are required under ZR 23-335(a)."
        conditions = [_overlay_condition()] if overlay_present is None else []
        values = [{"name": "Each of two side yards", "value": _DETACHED_SIDE_YARD_FT, "unit": "ft"}]
        return _applies_row("side_yard", values, conditions, text, zr)
    if building_type in _RESIDENCE_MULTI:
        if building_type == BUILDING_MIXED:
            # A mixed building reaches "no side yard required" through the Chapter 5 bulk
            # (ZR 35-01 -> 23-335(b)); ZR 34-232 by its words governs a residential building
            # only, so it is not the citation for a mixed building (and ZR 35-24 is not captured,
            # so it is not cited).
            where = "ZR 23-335(b)"
            zr = ["ZR 23-335", "ZR 35-01"]
        elif overlay_present:
            where = "ZR 34-232"
        else:
            where = "ZR 23-335(b)"
        text = f"A draft reading: no side yard is required under {where}."
        return _not_applicable_row("side_yard", [], [open_note], text, zr)
    # The building type was not stated.
    if overlay_present is True:
        text = "A draft reading: no side yard is required under ZR 34-232."
        return _not_applicable_row("side_yard", [], [open_note], text, zr)
    text = "A draft reading of the side yard under ZR 23-335 (it depends on the building type)."
    return _not_applicable_row("side_yard", [], [_side_yard_type_condition(), open_note], text, zr)


def _open_area_condition() -> dict:
    return {
        "kind": "unchecked_condition",
        "assumption": (
            "If any open area is provided along a side lot line it must be at least 5 feet wide "
            "(measured perpendicular to the side lot line)"
        ),
        "settled_by": "The building design: whether an open area along a side lot line is provided",
    }


def _side_yard_type_condition() -> dict:
    return {
        "kind": "unchecked_condition",
        "assumption": (
            "If the building is not a single- or two-family detached residence (which would need "
            "two side yards each at least 5 feet wide, ZR 23-335(a))"
        ),
        "settled_by": "A stated building type",
    }


def _applies_row(kind: str, values: list[dict], conditions: list[dict], text: str,
                 zr: list[str]) -> dict:
    row = {"kind": kind, "state": "applies", "text": text, "zr_sections": zr}
    if values:
        row["values"] = values
    if conditions:
        row["conditions"] = conditions
    return row


def _not_applicable_row(kind: str, values: list[dict], conditions: list[dict], text: str,
                        zr: list[str]) -> dict:
    row = {"kind": kind, "state": "not_applicable", "text": text, "zr_sections": zr}
    if values:
        row["values"] = values
    if conditions:
        row["conditions"] = conditions
    return row


def _ft(value: float | None) -> str:
    if value is None:
        return "the maximum base height"
    text = f"{value:.2f}".rstrip("0").rstrip(".") or "0"
    return f"{text} ft"


def _constraint_lines(
    overlay_present: bool | None,
    street_wall_band_geometry: dict | None,
) -> list[dict]:
    """The envelope constraint lines. The street-wall band is established only when an operative
    street line and a geometry were supplied (a constructed case); without them (the benchmark) it
    is not_established, carrying its basis and ZR sections and NO geometry (D-094-R017: draw only
    when geometry and basis are established). The setback line is never established here (the
    building's own setback geometry is not modelled)."""
    zr_wall = list(_ZR_STREET_WALL_OVERLAY) if overlay_present else list(_ZR_STREET_WALL_PLAIN)
    zr_setback = list(_ZR_SETBACK_OVERLAY) if overlay_present else list(_ZR_SETBACK_PLAIN)
    if street_wall_band_geometry is not None:
        wall = {"kind": "street_wall_band", "state": "established", "basis": "derived",
                "zr_sections": zr_wall, "geometry": street_wall_band_geometry}
    else:
        wall = {"kind": "street_wall_band", "state": "not_established", "basis": "derived",
                "zr_sections": zr_wall}
    setback = {"kind": "setback_line", "state": "not_established", "basis": "derived",
               "zr_sections": zr_setback}
    return [wall, setback]


def _input_facts(frontages: Sequence[Frontage], source_title: str, source_date: str) -> list[dict]:
    """The mapped street width of each frontage as an input_fact (basis gis - the DCM mapped width
    is a GIS value, never called a tax-map or recorded figure, G-10). Emitted only with a source
    title and date (D-093: no provenance, no fact)."""
    if not (source_title and source_date):
        return []
    facts: list[dict] = []
    for f in frontages:
        if f.mapped_width_ft is None:
            continue
        facts.append({
            "key": f"mapped_street_width:{f.name}",
            "value": float(f.mapped_width_ft),
            "unit": "ft",
            "basis": "gis",
            "source_title": source_title,
            "source_date": source_date,
        })
    return facts


def setback_value_state_from_row(envelope_setback_row: dict) -> dict:
    """The ``setback_above_base`` value state RECONCILED to the engine's applied envelope reading
    (M5-T170, lesson iii / RISK 2). The decision module decides the setback from the lot facts the
    decision step gathers and stays Withheld 'not covered' where no envelope analysis ran (a 1.4.0
    document, byte-identical). Where the envelope analysis DID run (a 1.5.0 document carrying the
    envelope setback row) this value state is reconciled so the two setback emitters agree
    byte-for-meaning: its reason is the envelope row's own draft reading and its ZR sections are
    the row's. It stays way 'withheld' (a standalone value state carries no number and is never
    conditional in place, which would need a value object); the applied reading is shown by the
    envelope row on page 3 and by the appendix open item on page 8."""
    return {
        "way": "withheld",
        "label": _SETBACK_LABEL,
        "reason": str(envelope_setback_row.get("text") or ""),
        "gap_kind": "missing_information",
        "resolved_by": (
            "Confirming the building's street-wall height against the maximum base height and the "
            "operative street line, then checking the setback against an independently worked "
            "example."
        ),
        "zr_sections": list(envelope_setback_row.get("zr_sections", ()) or ()),
    }


def build_envelope_analysis(
    *,
    overlay_present: bool | None,
    building_type: str | None,
    frontages: Sequence[Frontage],
    street_wall_height_ft: float | None,
    max_base_height_ft: float | None,
    side_yard_open_area_provided: bool = False,
    street_wall_band_geometry: dict | None = None,
    source_title: str = "",
    source_date: str = "",
) -> EnvelopeAnalysis:
    """Build the additive 1.5.0 envelope analysis from the gathered facts.

    ``overlay_present`` - whether a commercial overlay is mapped (True / False / None=not read).
    ``building_type`` - one of the BUILDING_* constants, or None when not stated (never defaulted).
    ``frontages`` - each with its D-052 wide / narrow class and mapped width.
    ``street_wall_height_ft`` / ``max_base_height_ft`` - the building street-wall height against the
    maximum base height; the setback is triggered only strictly above the maximum base height.
    ``street_wall_band_geometry`` - an established 8-ft band within the lot, supplied only by a
    constructed case where an operative street line is known; without it it is not_established.
    """
    rows = [
        _street_wall_check(overlay_present, building_type, frontages),
        _setback_check(overlay_present, frontages, street_wall_height_ft, max_base_height_ft),
        _side_yard_check(overlay_present, building_type, side_yard_open_area_provided),
    ]
    return EnvelopeAnalysis(
        envelope_rows=rows,
        constraint_lines=_constraint_lines(overlay_present, street_wall_band_geometry),
        input_facts=_input_facts(frontages, source_title, source_date),
    )
