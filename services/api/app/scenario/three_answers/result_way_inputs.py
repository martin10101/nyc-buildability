"""Input records for the result-way decision module (task M5-T129, work order Part 0).

This file holds ONLY the inputs :mod:`result_ways` decides from. It is split off so
neither file grows past the modularity warning threshold (CODE_MODULARITY_POLICY). It is
NEW and nothing calls it; it changes no existing file and defines its own records rather
than importing the engine's present ``ThreeAnswerInputs`` (work order Part 0: "The module
defines its own input records; it does not import or change the engine's present input
object").

EVERY fact may be "not given" or "not read", and NOTHING has a default that stands for a
fact (owner rule 1; R240). The tri-state enums below carry the "not read" / "not checked"
state as an explicit value, so the absence of a reading is never silently read as "none"
(gap K10: "a column that was not read is never taken as 'none'").

The reach records below MIRROR the lot-reach measurements of the spatial engine (task
M5-T127) - one value per street frontage, the corner point's reach and the corner angle, each
a value or unknown - but the module defines its OWN records rather than importing the engine's
measurement type (Part 0: "The module defines its own input records; it does not import or
change the engine's present input object"), so nothing here couples to the spatial engine and
the second piece adapts the real measurements into these records at the wiring step. A value
is unknown exactly when it is None - never a zero and never a default.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum

__all__ = [
    "BUILDING_OPTION_KEYS",
    "CORNER_PORTION_WITHIN_100_FT",
    "COVERAGE_KEY",
    "FAMILY_HUMAN",
    "FLOOR_AREA_KEYS",
    "HEIGHT_KEYS",
    "KIND_CONTRADICTED_RECORD",
    "KIND_UNCHECKED_CONDITION",
    "KIND_USER_STATEMENT",
    "LABELS",
    "MISSING_INFORMATION",
    "REAR_YARD_KEY",
    "REAR_YARD_WAIVER_MAX_ANGLE_135_DEG",
    "REAR_YARD_WAIVER_WITHIN_100_FT",
    "REASON_KIND_BY_GAP",
    "SETBACK_KEY",
    "UNIT_QUALIFYING_AFFORDABLE_KEY",
    "UNIT_QUALIFYING_SENIOR_KEY",
    "UNIT_STANDARD_KEY",
    "WORK_ORDER_DISTRICT",
    "WORK_OWED",
    "AnswerWays",
    "AreaAgreement",
    "Checked",
    "Condition",
    "Conditional",
    "CornerReach",
    "DensityKnowledge",
    "LegalMeasure",
    "LotAreaFigures",
    "LotType",
    "OverlayResultSupport",
    "ReachMeasurements",
    "ReachValue",
    "Recorded",
    "ResultFamily",
    "ResultWay",
    "ResultWayInputs",
    "ResultWays",
    "Settled",
    "WayRecord",
    "WholeAnswerNotAvailable",
    "Withheld",
]


class LotType(Enum):
    """The recorded lot type (a fact from the approximate tax-map outline)."""

    CORNER = "corner"
    INTERIOR = "interior"
    THROUGH = "through"


class Recorded(Enum):
    """A recorded condition read from the city record: one of three states, never a
    default (gaps K10, K18, K19). ``NOT_READ`` is never taken as ``ABSENT``."""

    NOT_READ = "not_read"
    ABSENT = "recorded_as_absent"
    PRESENT = "recorded_as_present"


class Checked(Enum):
    """A condition with no data source (gap K20: waterfront, airport height, transit
    easement, a lot near a district line). ``NOT_CHECKED`` is never "confirmed" (R267)."""

    NOT_CHECKED = "not_checked"
    ABSENT = "checked_and_absent"
    PRESENT = "recorded_as_present"


class AreaAgreement(Enum):
    """Whether the tax-map outline's area agrees with the recorded lot area (section 6,
    gap K5). Agreement is an INPUT: the tolerance is not this task's (O4)."""

    AGREES = "agrees"
    DISAGREES = "disagrees"
    COULD_NOT_COMPARE = "could_not_be_compared"


class DensityKnowledge(Enum):
    """What is known about a special density area (gap K11). There is no data source today
    and the ZR 12-10 definition is owed; a user's statement supports only a conditional
    result and is never stored as a fact (R255)."""

    NOT_GIVEN = "not_given"
    EVIDENCE_NOT_IN_ONE = "evidence_not_in_one"
    EVIDENCE_IN_ONE = "evidence_in_one"
    USER_STATEMENT_NOT_IN_ONE = "user_statement_not_in_one"


class ResultFamily(Enum):
    """The result groups whose overlay support the caller states per group (reading O5).
    The module holds NO table of which results an overlay reading supports: for each family
    the caller says whether an independent reading supports showing it under the overlay."""

    FLOOR_AREA = "floor_area"
    HEIGHTS = "heights"
    COVERAGE = "coverage"
    REAR_YARD = "rear_yard"
    SETBACK = "setback"
    BUILDING_OPTION = "building_option"
    UNIT_LIMIT = "unit_limit"


@dataclass(frozen=True)
class ReachValue:
    """One reach measurement, mirroring a site_geometry sourced value: ``value`` is None
    exactly when the measurement is unknown (no outline, or a frontage not straight) - never
    a zero and never a default."""

    value: float | None

    @property
    def known(self) -> bool:
        return self.value is not None


@dataclass(frozen=True)
class StreetReach:
    """How far the lot reaches perpendicular to one street's frontage line (gap K1/K12)."""

    street_name: str
    reach: ReachValue


@dataclass(frozen=True)
class CornerReach:
    """The corner point's measurements (gap K4/K12): the farthest straight-line reach of any
    point of the lot from the corner point, and the angle between the two street lines there."""

    reach: ReachValue
    angle: ReachValue


@dataclass(frozen=True)
class ReachMeasurements:
    """The reach measurements for one lot: one per street frontage, plus the corner. Empty
    street lines (or a reach that is unknown) means there is nothing to measure (no outline)."""

    street_lines: tuple[StreetReach, ...]
    corner: CornerReach


@dataclass(frozen=True)
class OverlayResultSupport:
    """What the caller states, per result family, about a recorded commercial overlay
    (reading O5, gap K9). ``supported`` means an independent reading of the overlay text
    supports showing this family; otherwise the reading is owed and ``reading_owed`` names
    it in plain words with the sections (``zr_sections``). The module decides no legal
    reading and keeps no table of what any reading supports."""

    supported: bool
    reading_owed: str = ""
    zr_sections: tuple[str, ...] = ()


@dataclass(frozen=True)
class LotAreaFigures:
    """The recorded lot area and whether the outline's area agrees with it (section 6,
    gap K5). ``recorded_sq_ft`` is None when no lot area was recorded (then every result
    that needs the area is withheld; the outline's area never stands in - section 6 rule 6).
    Both figures are carried for the WORDING only; neither is ever used in a calculation and
    the module holds no area threshold."""

    recorded_sq_ft: float | None
    agreement: AreaAgreement | None
    outline_sq_ft: float | None = None


@dataclass(frozen=True)
class ResultWayInputs:
    """Everything the module decides from. No field has a default that stands for a fact;
    the tri-state fields must be supplied explicitly as read / not-read / not-checked.

    ``district`` and ``housing_kind`` are carried for the wording and the provenance; they
    change no result's WAY in this milestone (``housing_kind`` is a design choice, rule 2).
    ``large_lot_threshold_met`` is the caller's comparison of the recorded area with the
    gap-K3 large-lot threshold: the module holds no area number, so the caller states the
    comparison (the O5 pattern). ``overlay_support`` is consulted only when
    ``commercial_overlay`` is recorded present."""

    district: str | None
    lot_type: LotType | None
    housing_kind: str | None
    area: LotAreaFigures
    reach: ReachMeasurements | None
    special_purpose_district: Recorded
    split_by_district_line: Recorded
    commercial_overlay: Recorded
    commercial_overlay_code: str | None
    inclusionary_housing_area: Recorded
    flood_zone: Recorded
    landmark_or_historic: Recorded
    waterfront: Checked
    airport_height: Checked
    transit_easement: Checked
    near_district_line: Checked
    special_density: DensityKnowledge
    large_lot_threshold_met: bool | None
    overlay_support: Mapping[ResultFamily, OverlayResultSupport] | None = None


# ---------------------------------------------------------------------------
# The result vocabulary and the way (output) records. These live here with the
# input records so the decision logic in result_ways.py stays one focused module
# (modularity policy); result_ways re-exports them, so its public interface is
# unchanged (a compatibility facade).
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Gap and condition kinds. The contract gap_kind enum has two values; the work
# order's section 5 uses four kinds, mapped onto the two by reading O1:
#   information -> missing_information
#   owed / question / "owed; question" -> work_owed
#   evidence -> missing_information when a recorded fact was not read,
#               work_owed when a recorded condition cannot yet be handled.
# ---------------------------------------------------------------------------
MISSING_INFORMATION = "missing_information"
WORK_OWED = "work_owed"

KIND_USER_STATEMENT = "user_statement"
KIND_CONTRADICTED_RECORD = "contradicted_record"
KIND_UNCHECKED_CONDITION = "unchecked_condition"

# reason_kind of a whole-answer not-available object (results contract).
REASON_KIND_BY_GAP = {WORK_OWED: "rule_not_implemented", MISSING_INFORMATION: "missing_input"}


# ---------------------------------------------------------------------------
# The results this module decides, grouped by answer and by family.
# ---------------------------------------------------------------------------
FLOOR_AREA_KEYS = (
    "max_residential_far",
    "max_residential_floor_area",
    "max_residential_far_qualifying_affordable_or_senior",
    "max_residential_floor_area_qualifying_affordable_or_senior",
)
HEIGHT_KEYS = (
    "min_base_height",
    "max_base_height",
    "max_building_height",
    "min_base_height_qualifying_affordable_or_senior",
    "max_base_height_qualifying_affordable_or_senior",
    "max_building_height_qualifying_affordable_or_senior",
)
COVERAGE_KEY = "max_lot_coverage"
BUILDING_OPTION_KEYS = (
    "achieved_zoning_floor_area",
    "building_floors",
    "building_height",
    "floor_plate_area",
)
REAR_YARD_KEY = "rear_yard"
SETBACK_KEY = "setback_above_base"
UNIT_STANDARD_KEY = "legal_unit_limit_standard"
UNIT_QUALIFYING_AFFORDABLE_KEY = "legal_unit_limit_qualifying_affordable"
UNIT_QUALIFYING_SENIOR_KEY = "legal_unit_limit_qualifying_senior"

# The district the work order's gaps and rules are written for (reading O11). This is the
# SCOPE of the work order, not a zoning number: a district other than this one has rules that
# are owed, and the deciders withhold every result for it. Held once, as a named constant.
WORK_ORDER_DISTRICT = "R6B"

LABELS: dict[str, str] = {
    "max_residential_far": "Maximum residential floor area ratio",
    "max_residential_floor_area": "Maximum residential floor area",
    "max_residential_far_qualifying_affordable_or_senior": (
        "Maximum residential floor area ratio, qualifying affordable or senior housing"
    ),
    "max_residential_floor_area_qualifying_affordable_or_senior": (
        "Maximum residential floor area, qualifying affordable or senior housing"
    ),
    "min_base_height": "Minimum base height",
    "max_base_height": "Maximum base height",
    "max_building_height": "Maximum building height",
    "min_base_height_qualifying_affordable_or_senior": (
        "Minimum base height, qualifying affordable or senior housing"
    ),
    "max_base_height_qualifying_affordable_or_senior": (
        "Maximum base height, qualifying affordable or senior housing"
    ),
    "max_building_height_qualifying_affordable_or_senior": (
        "Maximum building height, qualifying affordable or senior housing"
    ),
    "max_lot_coverage": "Maximum lot coverage",
    "achieved_zoning_floor_area": "Building option: achieved zoning floor area",
    "building_floors": "Building option: floors",
    "building_height": "Building option: height",
    "floor_plate_area": "Building option: floor plate area",
    "rear_yard": "Rear yard",
    "setback_above_base": "Setback above the base",
    # Reading O12 (gap K14): the standard limit is labelled for a new all-residential building;
    # the work order's words ("The limit is labelled 'new all-residential building'. Other cases
    # are withheld.") are carried alongside "standard residences".
    "legal_unit_limit_standard": (
        "Legal dwelling-unit limit, standard residences (new all-residential building)"
    ),
    "legal_unit_limit_qualifying_affordable": (
        "Legal dwelling-unit limit, qualifying affordable housing"
    ),
    "legal_unit_limit_qualifying_senior": (
        "Legal dwelling-unit limit, qualifying senior housing"
    ),
}

FAMILY_HUMAN = {
    ResultFamily.FLOOR_AREA: "floor-area",
    ResultFamily.HEIGHTS: "height",
    ResultFamily.COVERAGE: "coverage",
    ResultFamily.REAR_YARD: "rear-yard",
    ResultFamily.SETBACK: "setback",
    ResultFamily.BUILDING_OPTION: "building-option",
    ResultFamily.UNIT_LIMIT: "dwelling-unit",
}


# ---------------------------------------------------------------------------
# The way records (mirror results contract 1.3.0 value_state / answer_not_available).
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Condition:
    """One explicit, defensible assumption behind a conditional value (value_condition)."""

    kind: str
    assumption: str
    settled_by: str

    def to_dict(self) -> dict:
        return {"kind": self.kind, "assumption": self.assumption, "settled_by": self.settled_by}


@dataclass(frozen=True)
class Settled:
    """A settled value: no condition (value_state way 'settled')."""

    way: str = "settled"

    def to_value_state(self) -> dict:
        return {"way": "settled"}


@dataclass(frozen=True)
class Conditional:
    """A conditional value: one or more named conditions (value_state way 'conditional')."""

    conditions: tuple[Condition, ...]
    way: str = "conditional"

    def to_value_state(self) -> dict:
        return {"way": "conditional", "conditions": [c.to_dict() for c in self.conditions]}


@dataclass(frozen=True)
class Withheld:
    """A withheld value: no number, with its label, reason, gap kind, what would resolve it
    and, where one applies, the law section(s) (value_state way 'withheld')."""

    label: str
    reason: str
    gap_kind: str
    resolved_by: str
    zr_sections: tuple[str, ...] = ()
    way: str = "withheld"

    def to_value_state(self) -> dict:
        state = {
            "way": "withheld",
            "label": self.label,
            "reason": self.reason,
            "gap_kind": self.gap_kind,
            "resolved_by": self.resolved_by,
        }
        if self.zr_sections:
            state["zr_sections"] = list(self.zr_sections)
        return state


WayRecord = Settled | Conditional | Withheld


@dataclass(frozen=True)
class WholeAnswerNotAvailable:
    """The whole answer is not available because every one of its values is withheld (the
    contract cannot keep an answer 'available' with no shown value). Mirrors
    answer_not_available with the additive 1.3.0 resolution fields."""

    reason: str
    reason_kind: str
    gap_kind: str
    resolved_by: str

    def to_dict(self) -> dict:
        return {
            "status": "not_available",
            "reason": self.reason,
            "reason_kind": self.reason_kind,
            "gap_kind": self.gap_kind,
            "resolved_by": self.resolved_by,
        }


@dataclass(frozen=True)
class ResultWay:
    """One result's key, human label and way."""

    key: str
    label: str
    way: WayRecord


@dataclass(frozen=True)
class AnswerWays:
    """One of the three answers: the way of each of its value keys, and - when every value
    is withheld - the whole-answer not-available record."""

    answer: str
    values: tuple[ResultWay, ...]
    whole_answer_not_available: WholeAnswerNotAvailable | None = None

    @property
    def is_available(self) -> bool:
        return self.whole_answer_not_available is None


@dataclass(frozen=True)
class ResultWays:
    """The way of every result the packet lists: the three answers and the five results
    that are not value keys today (the rear yard, the setback above the base, the legal unit
    limit for standard residences and for qualifying affordable and qualifying senior
    housing)."""

    floor_area_allowance: AnswerWays
    permitted_envelope: AnswerWays
    building_option: AnswerWays
    rear_yard: ResultWay
    setback_above_base: ResultWay
    unit_limit_standard: ResultWay
    unit_limit_qualifying_affordable: ResultWay
    unit_limit_qualifying_senior: ResultWay

    def result_ways(self) -> tuple[ResultWay, ...]:
        """Every result, flattened: the answers' value ways plus the five standalone ones."""
        rows: list[ResultWay] = []
        for answer in (self.floor_area_allowance, self.permitted_envelope, self.building_option):
            rows.extend(answer.values)
        rows.extend([
            self.rear_yard, self.setback_above_base, self.unit_limit_standard,
            self.unit_limit_qualifying_affordable, self.unit_limit_qualifying_senior,
        ])
        return tuple(rows)


# ---------------------------------------------------------------------------
# The two legal measures (reading O9). These are the ONLY legal numbers in this
# module; each carries the capture id of the ZR text it comes from and the
# comparison written as the captured words have it. 100 feet is cited from the
# ZR 12-10 corner-lot-portion definition for coverage, and from ZR 23-344(a) for
# the rear-yard waiver; 135 degrees is the ZR 23-344(a) waiver angle.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class LegalMeasure:
    """One legal measure read from a pinned ZR capture (reading O9). Never a zoning number
    the module derives: a captured threshold the reach measurements are compared against."""

    value: float
    unit: str
    zr_section: str
    capture_snapshot_id: str
    capture_content_digest: str
    captured_words: str
    comparison: str


CORNER_PORTION_WITHIN_100_FT = LegalMeasure(
    value=100.0,
    unit="feet",
    zr_section="ZR 12-10",
    capture_snapshot_id="zr-12-10-lot-corner",
    capture_content_digest="86b686b683e4ed37531319130ee49dc99a3cba3acbd41c27da2bccb2eb686a58",
    captured_words=(
        "The portion of such zoning lot subject to the regulations for corner lots is that "
        "portion bounded by the intersecting street line and lines parallel to and 100 feet "
        "from each intersecting street line."
    ),
    comparison="the whole lot is within 100 feet of each intersecting street line",
)

REAR_YARD_WAIVER_WITHIN_100_FT = LegalMeasure(
    value=100.0,
    unit="feet",
    zr_section="ZR 23-344",
    capture_snapshot_id="zr-23-344",
    capture_content_digest="91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007",
    captured_words=(
        "no rear yard shall be required within 100 feet of the point of intersection of two "
        "street lines intersecting at an angle of 135 degrees or less"
    ),
    comparison="the whole lot is within 100 feet of the point where the two street lines meet",
)

REAR_YARD_WAIVER_MAX_ANGLE_135_DEG = LegalMeasure(
    value=135.0,
    unit="degrees",
    zr_section="ZR 23-344",
    capture_snapshot_id="zr-23-344",
    capture_content_digest="91f949153c7b682040151f1ad88c574dbe8e53f630cd720883a761e054068007",
    captured_words=(
        "no rear yard shall be required within 100 feet of the point of intersection of two "
        "street lines intersecting at an angle of 135 degrees or less"
    ),
    comparison="the two street lines meet at an angle of 135 degrees or less",
)
