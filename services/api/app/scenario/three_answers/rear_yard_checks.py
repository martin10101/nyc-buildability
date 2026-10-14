"""The ZR 23-344 rear-yard checks - (a) the corner-area waiver, (b) the short dimension of a
block, (c)(3) the adjoining side lot line - combined into the contract-1.5.0 rear_yard block,
its input_facts and its rear-yard constraint lines (task M5-T167, steps 3-4).

This is the SCENARIO layer: it holds the ZR 12-10 230-foot captured threshold and the
UNRESOLVED measurement-basis law, and it turns the geometry the spatial block-frontage measure
(:mod:`app.spatial.site_geometry.block_frontage`) supplies, plus the corner reach/angle and the
lot facts the decision step gathered, into the additive 1.5.0 blocks. Every text is a plain,
labelled DRAFT reading: no internal name, no reading/gap number, no task id, never "professional
review", never a statement about which law text is "captured" or "built", never an unconditional
"no rear yard" (the corner waiver (a) is never the only exception named). Expected outcomes come
from the R6B reference case (docs/reference-cases/R6B), never a program run.

THREE RULES (result-deciding). (1) No default stands for a fact: a missing reach/angle/area is
not known and holds its result back; the real lot's short-dimension (b) is NOT KNOWN because the
Zoning Resolution does not fix the measurement basis (reference row b-measurement-basis), NOT
because a measured value is at or above 230 ft. (2) A not_known check carries NO number (schema
oneOf). (3) Every emitted input_fact equals the value the calculation uses on its basis, with no
second figure for one basis (DB-262), and every emitted constraint line lies within the lot (so a
line that is not established within the lot is emitted not_known, carrying no geometry)."""

from __future__ import annotations

from dataclasses import dataclass, field

from app.spatial.site_geometry.block_frontage import BlockFrontageMeasure

__all__ = [
    "SHORT_DIMENSION_MAX_230",
    "CapturedMeasure",
    "RearYardAnalysis",
    "build_rear_yard_analysis",
    "classify_short_dimension",
]

_DOB = "Not a determination by the Department of Buildings."
_ZR_23_344 = "ZR 23-344"
_ZR_12_10 = "ZR 12-10"

# The R6-R12 districts ZR 23-344(c)(3) names (letter-suffix districts like R6B read as within
# "R6 through R12"; reference row c-1-vs-c-3 holds this subject to professional confirmation).
_R6_R12_PREFIXES = ("R6", "R7", "R8", "R9", "R10", "R11", "R12")


@dataclass(frozen=True)
class CapturedMeasure:
    """A legal threshold read from a pinned ZR capture (never a number this module derives):
    the captured words and the capture digest travel with the value."""

    value: float
    unit: str
    zr_section: str
    capture_snapshot_id: str
    capture_content_digest: str
    captured_words: str


# ZR 12-10 "short dimension of a block": strict "less than 230 feet". Pinned capture digest from
# docs/research/zr-snapshots/v1/zr-12-10-short-dimension-of-a-block.snapshot.json.
SHORT_DIMENSION_MAX_230 = CapturedMeasure(
    value=230.0,
    unit="feet",
    zr_section=_ZR_12_10,
    capture_snapshot_id="zr-12-10-short-dimension-of-a-block",
    capture_content_digest="3ec2dadd555aef1101fe37c14bb34f48bf4ffd73068fe3b0036cd1b6e2401648",
    captured_words=(
        "shall be a block frontage where the dimension between any two streets bounding the "
        "block measures less than 230 feet"
    ),
)

# The ZR 23-344(a) corner-waiver limits (reused as captured thresholds; reference rows
# fit-multiple-apply / real-lot-reach): no rear yard within 100 ft of a corner whose two street
# lines meet at 135 degrees or less.
_WAIVER_WITHIN_100_FT = 100.0
_WAIVER_MAX_ANGLE_135 = 135.0


@dataclass(frozen=True)
class RearYardAnalysis:
    """The additive contract-1.5.0 rear-yard emission: the rear_yard block (checks + combined),
    the input_facts list and the rear-yard constraint lines. Attached to the document and binding
    contract_version to 1.5.0 by :func:`three_way_document.emit_three_way_document`."""

    rear_yard: dict
    input_facts: list[dict] = field(default_factory=list)
    constraint_lines: list[dict] = field(default_factory=list)


def _fmt(value: float) -> str:
    """Plain two-decimal feet/degrees, trailing zeros trimmed (angles and reaches, where the
    second decimal is the finest the geometry carries)."""
    text = f"{value:.2f}".rstrip("0").rstrip(".")
    return text or "0"


def _fmt_measure(value: float) -> str:
    """A separation display that NEVER rounds a value UP across the two-decimal boundary, so a
    short-dimension separation below 230 feet is never printed as '230' (229.996 shows as 229.996,
    not 230.00) - the strict '< 230 feet' test is decided on the raw value and the printed value
    never contradicts it (S1). Values that do not round up print as plain two-decimal feet."""
    rounded = f"{value:.2f}"
    if float(rounded) > value:
        rounded = f"{value:.6f}"
    return rounded.rstrip("0").rstrip(".") or "0"


def classify_short_dimension(
    separation_ft: float | None, basis: str | None, *, basis_fixed_by_law: bool,
) -> tuple[str, str]:
    """Classify the short-dimension test, returning ``(state, reason)`` where ``state`` is one of
    ``applies`` / ``not_applicable`` / ``not_known``.

    ``basis_fixed_by_law`` is True only for a dimension STATED on a given basis (the made-up
    boundary cases M1-M10, reference rows b-less-than-230 / M1-M3): then the strict ``< 230 ft``
    test decides (229.99 applies; 230.00 and 230.01 do not). For a REAL lot it is False: the
    Zoning Resolution does not fix whether the dimension is measured between street lines,
    centrelines or lot lines (reference row b-measurement-basis), so the short-dimension test is
    NOT KNOWN whatever the measured separation - a value at or above 230 ft on one basis cannot
    settle it when a street-line reading could be below 230 ft. A missing separation is not
    known."""
    if not basis_fixed_by_law:
        return "not_known", (
            "whether the frontage is a short dimension of a block is not known: the Zoning "
            "Resolution does not fix whether the distance between the two streets bounding the "
            "block is measured between street lines, centrelines or lot lines, and on different "
            "readings it falls on different sides of 230 feet"
        )
    if separation_ft is None:
        return "not_known", (
            "the distance between the two streets bounding the block is not known, so whether "
            "the frontage is a short dimension of a block is not known"
        )
    shown = _fmt_measure(separation_ft)
    if separation_ft < SHORT_DIMENSION_MAX_230.value:
        return "applies", (
            f"the distance between the two streets bounding the block is {shown} feet, less "
            "than 230 feet, so the frontage is a short dimension of a block"
        )
    return "not_applicable", (
        f"the distance between the two streets bounding the block is {shown} feet, not less "
        "than 230 feet, so the frontage is not a short dimension of a block"
    )


def _check_a(reach_ft: float | None, angle_deg: float | None) -> dict:
    """ZR 23-344(a) the corner-area waiver. Applies where the two street lines meet at 135 degrees
    or less; within 100 ft of that corner no rear yard is required. A missing reach/angle is not
    known (no number). The lot's farthest reach from the corner, when known, says how much of the
    lot the waiver covers - it is never presented as the only exception (the combined row names
    (b)/(c)(3) too)."""
    base = {"provision": "23-344(a)", "zr_sections": [_ZR_23_344]}
    if angle_deg is None or reach_ft is None:
        return {
            **base, "state": "not_known",
            "text": (
                "A labelled draft reading: whether the corner-area waiver of ZR 23-344(a) applies "
                "is not known, because the corner angle or the lot's reach from the corner could "
                f"not be measured. No number is shown. {_DOB}"
            ),
        }
    if angle_deg > _WAIVER_MAX_ANGLE_135:
        return {
            **base, "state": "not_applicable",
            "inputs": [_angle_input(angle_deg)],
            "text": (
                f"A labelled draft reading: the two street lines meet at about {_fmt(angle_deg)} "
                "degrees, more than 135 degrees, so the corner-area waiver of ZR 23-344(a) does "
                f"not apply. {_DOB}"
            ),
        }
    covers = (
        f"The lot reaches about {_fmt(reach_ft)} feet from the corner, so (a) covers only the "
        "part within 100 feet of it."
        if reach_ft > _WAIVER_WITHIN_100_FT
        else "The whole lot lies within 100 feet of the corner, so (a) reaches all of it."
    )
    return {
        **base, "state": "applies",
        "inputs": [_angle_input(angle_deg), _reach_input(reach_ft)],
        "text": (
            f"A labelled draft reading: the two street lines meet at about {_fmt(angle_deg)} "
            "degrees (not more than 135), so under ZR 23-344(a) no rear yard is required within "
            f"100 feet of the corner. {covers} {_DOB}"
        ),
    }


def _angle_input(angle_deg: float) -> dict:
    return {
        "name": "Angle between the two street lines at the corner",
        "value": round(angle_deg, 2), "unit": "degrees", "basis": "derived",
    }


def _reach_input(reach_ft: float) -> dict:
    return {
        "name": "Farthest reach of the lot from the corner",
        "value": round(reach_ft, 2), "unit": "ft", "basis": "derived",
    }


def _check_b(block_frontage: BlockFrontageMeasure | None, *, basis_fixed_by_law: bool) -> dict:
    """ZR 23-344(b) the short dimension of a block. For a real lot the measurement basis is
    unresolved law, so (b) is not known (no number) whatever the block-frontage measure found."""
    separation = None
    basis = None
    if block_frontage is not None and block_frontage.separations:
        basis, separation = next(iter(block_frontage.separations.items()))
    state, reason = classify_short_dimension(
        separation, basis, basis_fixed_by_law=basis_fixed_by_law,
    )
    base = {"provision": "23-344(b)", "zr_sections": [_ZR_23_344, _ZR_12_10]}
    if state == "not_known":
        return {
            **base, "state": "not_known",
            "text": f"A labelled draft reading: {reason}. No number is shown. {_DOB}",
        }
    inputs = []
    if separation is not None and basis is not None:
        inputs = [{
            "name": "Distance between the two streets bounding the block",
            "value": round(separation, 2), "unit": "ft", "basis": basis,
        }]
    return {
        **base, "state": state, "inputs": inputs,
        "text": (
            f"A labelled draft reading: {reason}; within 100 feet of that street line no rear "
            f"yard would be required under ZR 23-344(b). {_DOB}"
        ),
    }


def _in_r6_r12(district: str | None) -> bool | None:
    """True when the district is within 'R6 through R12' (letter-suffix districts like R6B read as
    within it, reference row c-1-vs-c-3), False when plainly outside, None when not known."""
    if not district:
        return None
    text = district.strip().upper()
    if text.startswith(_R6_R12_PREFIXES):
        return True
    if text.startswith(("R1", "R2", "R3", "R4", "R5")):
        return False
    return None


def _check_c3(district: str | None) -> dict:
    """ZR 23-344(c)(3): in R6 through R12 districts, beyond 100 ft of a street line, no rear yard is
    required where the deemed rear lot line coincides with a side lot line of an adjoining zoning
    lot. A district plainly outside R6-R12 is not applicable (S10); within it (R6B read as within,
    a point for professional confirmation), whether the deemed rear lot line so coincides turns on
    the neighbour's lot-line kind, which is not captured, so it is not known."""
    base = {"provision": "23-344(c)(3)", "zr_sections": [_ZR_23_344, _ZR_12_10]}
    in_range = _in_r6_r12(district)
    if in_range is False:
        return {
            **base, "state": "not_applicable",
            "text": (
                f"A labelled draft reading: ZR 23-344(c)(3) applies in R6 through R12 districts; "
                f"district {district} is outside that range, so (c)(3) does not apply. {_DOB}"
            ),
        }
    return {
        **base, "state": "not_known",
        "text": (
            "A labelled draft reading: in R6 through R12 districts, beyond 100 feet of a street "
            "line, whether a rear yard is required under ZR 23-344(c)(3) turns on whether the "
            "deemed rear lot line coincides with a side lot line of an adjoining zoning lot. The "
            "neighbouring zoning lots' lot-line kinds are not recorded for this lot, so this is "
            f"not known. No number is shown. {_DOB}"
        ),
    }


def _combined() -> dict:
    """The combined rear-yard row: for a real lot, not known, shown as Conditional with the
    conditions that would settle it. Never an unconditional 'no rear yard'; ZR 23-344(b) linked;
    (a) is not the only exception named (the row names (b) and (c)(3) too)."""
    return {
        "state": "not_known",
        "way": "conditional",
        "conditions": [
            {
                "kind": "unchecked_condition",
                "assumption": (
                    "If the distance between the two streets bounding the block is measured on the "
                    "governing basis and is under 230 feet (ZR 23-344(b))"
                ),
                "settled_by": (
                    "An express measurement basis in the Zoning Resolution or City Planning "
                    "guidance, with a surveyed or certified street-line separation"
                ),
            },
            {
                "kind": "unchecked_condition",
                "assumption": (
                    "If the neighbours' side lot lines are confirmed for ZR 23-344(c)(3) beyond "
                    "100 feet of a street line"
                ),
                "settled_by": (
                    "Reading the adjoining zoning lots' recorded lot-line kinds"
                ),
            },
            {
                "kind": "unchecked_condition",
                "assumption": (
                    "If the zoning lot is confirmed (whether this lot alone, or together with an "
                    "adjoining lot, is one zoning lot)"
                ),
                "settled_by": "Reading the recorded zoning-lot description",
            },
        ],
        # A SHORT summary line: it must fit the report's page-1 uncertainty cap, so the detail
        # lives in the conditions below and in the per-check texts, not here. It stays a conditional
        # reading (never an unconditional "no rear yard"); its ZR 23-344 link resolves to the
        # section that carries (a)/(b)/(c)(3).
        "text": "A conditional rear-yard reading under ZR 23-344.",
        "zr_sections": [_ZR_23_344, _ZR_12_10],
    }


def _input_fact(key: str, value: float, unit: str, basis: str, title: str, date: str) -> dict:
    return {
        "key": key, "value": float(value), "unit": unit, "basis": basis,
        "source_title": title, "source_date": date,
    }


def _rear_yard_constraint_lines(operative_reach_ft: float | None) -> list[dict]:
    """The rear-yard constraint lines. For a real lot the 100-ft line is not established within the
    lot (the whole lot is within 100 ft of the operative street line, so the line lies beyond it),
    and the corner area is not drawn - both not_known, carrying no geometry (S24: an emitted line
    lies within the lot)."""
    return [
        {"kind": "rear_yard_100ft_line", "state": "not_known", "basis": "derived",
         "zr_sections": [_ZR_23_344]},
        {"kind": "corner_area", "state": "not_known", "basis": "derived",
         "zr_sections": [_ZR_23_344, _ZR_12_10]},
    ]


def build_rear_yard_analysis(
    *,
    corner_reach_ft: float | None,
    corner_angle_deg: float | None,
    operative_street_reach_ft: float | None,
    district: str | None,
    block_frontage: BlockFrontageMeasure | None,
    recorded_area_sqft: float | None,
    outline_area_sqft: float | None,
    source_title: str,
    source_date: str,
    basis_fixed_by_law: bool = False,
) -> RearYardAnalysis:
    """Build the additive 1.5.0 rear-yard analysis from the gathered geometry and lot facts.

    ``basis_fixed_by_law`` stays False on every real-lot path (the measurement basis is unresolved
    law), so (b) and the combined row are not known; it is True only for a stated-dimension test
    case. ``recorded_area_sqft`` / ``outline_area_sqft`` are emitted as input_facts ONLY when
    present, each the value the calculation uses on its basis (DB-262), with no second figure for a
    basis. ``district`` reserves the R6-R12 check for (c)(3) (not known here regardless)."""
    checks = [
        _check_a(corner_reach_ft, corner_angle_deg),
        _check_b(block_frontage, basis_fixed_by_law=basis_fixed_by_law),
        _check_c3(district),
    ]
    rear_yard = {"checks": checks, "combined": _combined()}
    input_facts: list[dict] = []
    # A fact needs real provenance (D-093 / backend rule): with no source title or date, emit none
    # rather than invent one. The schema also requires a non-empty source title and date.
    if not (source_title and source_date):
        return RearYardAnalysis(
            rear_yard=rear_yard,
            constraint_lines=_rear_yard_constraint_lines(operative_street_reach_ft),
        )
    if recorded_area_sqft is not None:
        input_facts.append(_input_fact(
            "recorded_lot_area", recorded_area_sqft, "sq_ft", "administrative_record",
            source_title, source_date,
        ))
    if outline_area_sqft is not None:
        input_facts.append(_input_fact(
            "lot_outline_area", round(outline_area_sqft, 2), "sq_ft", "gis",
            source_title, source_date,
        ))
    return RearYardAnalysis(
        rear_yard=rear_yard,
        input_facts=input_facts,
        constraint_lines=_rear_yard_constraint_lines(operative_street_reach_ft),
    )
