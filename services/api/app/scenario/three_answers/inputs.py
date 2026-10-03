"""Typed inputs and declared assumptions for the three-answer generator (task A-04,
plan M1-14 / C-2 / C-11; directive D-090).

All values are CALLER-SUPPLIED - the site facts (Lane B), the zoning facts, the
document identity, and the editable building defaults. Nothing here reads the
network, a connector, or a file; the generator is pure computation over these
inputs plus the Lane A rule registry.

A floor-to-floor height is a STATED, EDITABLE default. It is modelled as a
first-class :class:`Assumption` so it is never a silent constant: it travels in
the generator's output as a named assumption and its value is visible in the
emitted floor stack and floor-by-floor table.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

# Default residential floor-to-floor height (ft). STATED and EDITABLE: the architect
# may override it per option; it is surfaced as a named assumption, never hidden.
DEFAULT_FLOOR_TO_FLOOR_FT = 10.0

# The site-fact measurement rank the answers carry by default (PLUTO / DOF lot area
# and recorded dimensions are rank-2 "City records"). The building option additionally
# rests on the floor-to-floor assumption, so its own weakest-input label is "Assumed".
DEFAULT_SITE_MEASUREMENT_RANK = "city_records"

# 'Best combination' goal vocabulary (results.schema.json study goal def). A CLOSED set the
# add-on search optimizes; the default is stated and editable per option, exactly like the
# floor-to-floor height. goal_value_sf (results.schema.json) is always a floor area, so both
# kinds below resolve to a square-foot figure.
ADDON_GOAL_KINDS = ("most_residential_floor_area", "most_total_floor_area")
DEFAULT_ADDON_GOAL_KIND = "most_residential_floor_area"


@dataclass(frozen=True)
class AddonGoal:
    """The stated, editable 'Best combination' goal saved with the option (plan section 5:
    'The goal, program and assumptions are saved with the option'). ``kind`` is a closed
    vocabulary; ``text`` is required only for the open 'other' kind (results contract), null
    otherwise. The default is most residential floor area."""

    kind: str = DEFAULT_ADDON_GOAL_KIND
    text: str | None = None

    def as_contract(self) -> dict:
        return {"kind": self.kind, "text": self.text}


@dataclass(frozen=True)
class Assumption:
    """One stated, named assumption surfaced with the results (plan section 9
    'Explicit assumptions'). ``value``/``unit`` are present for a numeric
    assumption (e.g. the floor-to-floor height); ``None`` for a textual one."""

    assumption_id: str
    label: str
    value: float | None = None
    unit: str | None = None

    def as_dict(self) -> dict:
        return {
            "assumption_id": self.assumption_id,
            "label": self.label,
            "value": self.value,
            "unit": self.unit,
        }


@dataclass(frozen=True)
class BuildingDefaults:
    """The editable building-option defaults. Each is a named assumption."""

    floor_to_floor_ft: float = DEFAULT_FLOOR_TO_FLOOR_FT

    def assumptions(self) -> tuple[Assumption, ...]:
        return (
            Assumption(
                assumption_id="floor_to_floor_ft",
                label=(
                    f"Floor-to-floor height assumed at {self.floor_to_floor_ft:g} ft "
                    "(stated default; editable per option)"
                ),
                value=float(self.floor_to_floor_ft),
                unit="feet",
            ),
        )


@dataclass(frozen=True)
class ThreeAnswerInputs:
    """Everything the three-answer generator consumes for ONE option at ONE study
    revision. The zoning facts feed the Lane A rules; the lot facts feed the
    allowance, coverage and geometry; the document identity stamps the emitted
    results-v1 document."""

    # --- document identity (stamped onto the results-v1 document) ---
    results_id: str
    study_id: str
    option_id: str
    revision: int
    computed_at: str

    # --- zoning / site facts ---
    zoning_district: str
    lot_area_sq_ft: float
    lot_type: str  # corner | interior | through
    # standard_residence | qualifying_affordable_housing | qualifying_senior_housing
    housing_program: str
    overlay_present: bool
    special_district_present: bool
    within_100_ft_of_street_line_intersection: bool
    street_line_intersection_angle_degrees: float
    special_density_area: bool

    # --- optional lot geometry inputs (feet) ---
    lot_front_ft: float | None = None
    lot_depth_ft: float | None = None
    lot_outline: Sequence[Sequence[float]] | None = None

    # --- editable building defaults ---
    building_defaults: BuildingDefaults = field(default_factory=BuildingDefaults)

    # --- editable 'Best combination' goal (saved with the option) ---
    addon_goal: AddonGoal = field(default_factory=AddonGoal)

    # --- provenance plumbing ---
    depends_on_fact_ids: tuple[str, ...] = ()
    lot_area_fact_id: str | None = None
    site_measurement_rank: str = DEFAULT_SITE_MEASUREMENT_RANK

    def far_inputs(self) -> dict:
        """Inputs for the standard residential-FAR rule (r6-r12-residential-far)."""
        return {
            "zoning_district": self.zoning_district,
            "lot_area_sq_ft": self.lot_area_sq_ft,
            "housing_program": self.housing_program,
        }

    def qualifying_far_inputs(self) -> dict:
        """Inputs for the qualifying-housing FAR alternative (r6b-qualifying-housing-far)."""
        return {
            "zoning_district": self.zoning_district,
            "lot_area_sq_ft": self.lot_area_sq_ft,
            "housing_program": self.housing_program,
        }

    def height_inputs(self) -> dict:
        """Inputs for the height rule (r6b-height)."""
        return {
            "zoning_district": self.zoning_district,
            "overlay_present": self.overlay_present,
            "special_district_present": self.special_district_present,
        }

    def coverage_inputs(self) -> dict:
        """Inputs for the lot-coverage rule (r6b-lot-coverage)."""
        return {
            "zoning_district": self.zoning_district,
            "lot_type": self.lot_type,
            "overlay_present": self.overlay_present,
            "special_district_present": self.special_district_present,
        }

    def rear_yard_inputs(self) -> dict:
        """Inputs for the rear-yard corner-waiver rule (r6b-rear-yard-corner-waiver)."""
        return {
            "zoning_district": self.zoning_district,
            "within_100_ft_of_street_line_intersection": (
                self.within_100_ft_of_street_line_intersection
            ),
            "street_line_intersection_angle_degrees": (
                self.street_line_intersection_angle_degrees
            ),
            "overlay_present": self.overlay_present,
            "special_district_present": self.special_district_present,
        }

    def dwelling_unit_inputs(self, max_residential_floor_area_sq_ft: float) -> dict:
        """Inputs for the dwelling-unit rule (r6b-dwelling-units). The dividend is the
        standard residential-FAR allowance already computed by this generator."""
        return {
            "zoning_district": self.zoning_district,
            "max_residential_floor_area_sq_ft": max_residential_floor_area_sq_ft,
            "housing_program": self.housing_program,
            "special_density_area": self.special_density_area,
            "special_district_present": self.special_district_present,
        }

    def all_assumptions(self) -> tuple[Assumption, ...]:
        return self.building_defaults.assumptions()

    def site_measurement(self) -> Mapping[str, str]:
        """The measurement_known label for a city-recorded site fact (default)."""
        return _MEASUREMENT_BY_RANK[self.site_measurement_rank]


# measurement_known labels (site_fact.schema.json). Only the ranks this slice emits.
_MEASUREMENT_BY_RANK: Mapping[str, Mapping[str, str]] = {
    "survey_entered": {"rank": "survey_entered", "label": "Survey (entered)"},
    "city_records": {"rank": "city_records", "label": "City records"},
    "approximate_tax_map": {"rank": "approximate_tax_map", "label": "Approximate — tax map"},
    "entered": {"rank": "entered", "label": "Entered"},
    "assumed": {"rank": "assumed", "label": "Assumed"},
}

MEASUREMENT_ASSUMED: Mapping[str, str] = _MEASUREMENT_BY_RANK["assumed"]
MEASUREMENT_APPROXIMATE_TAX_MAP: Mapping[str, str] = _MEASUREMENT_BY_RANK["approximate_tax_map"]
