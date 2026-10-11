"""Derive the engine's five lot conditions from the SAME evidence the decision step gathers
(task M5-T137, the piece before the server route of docs/plans/
R6B_RESULTS_CONNECTION_WORK_ORDER_2026-10-06.md, Part A).

The older three-answer engine takes five facts of a lot as plain caller values: a commercial
overlay is present; a special purpose district is present; the whole lot lies within 100 feet of
the corner where its two street lines meet; the angle at which those two street lines meet; the
lot lies in a special density area. This module turns the evidence the program already holds -
the recorded city-record states, the measured corner reach and angle, and a user's statement -
into those five plain values, and records for EACH where it comes from (recorded, measured, the
user's statement, or not known / not applicable).

PLAIN STATES IN, PLAIN VALUES OUT. This module imports nothing from the scenario decision step or
the spatial measurement: the caller passes plain states and gets back, for each of the five, the
value to give the engine and the source saying where it came from. So no import-guard list has to
grow for it.

NO DEFAULT STANDS FOR A FACT. "Not read", "not known", "no statement" and "not a corner lot" are
states of their own and are never read as "no" or "absent". The engine cannot take "not known",
and the engine is NOT changed here; so where a condition is not known the engine is given a value
chosen ONLY in the direction that makes the engine itself give nothing for what depends on it, and
no shown result ever rests on such a value (the emit transform and its invariant test hold that
line). Each direction is proved from the rule files in the producer report:

* Overlay present/absent come from the record; not read -> the engine is given "no overlay", which
  adds no commercial-overlay note, so nothing unsupported is asserted.
* Special purpose district present/absent come from the record; not read -> the engine is given
  "present", which makes every rule ask for review so every dependent result is withheld.
* Within 100 feet of the corner and the angle are measured from the corner reach and angle; when
  there is no corner measurement the engine is given "not within 100 feet" (the rear-yard waiver
  then does not apply) and an angle past the waiver's limit; when the lot is not a corner lot the
  same, recorded as not applicable (there is no corner).
* The special density area is the ONE decision the record (ZR 12-10) and any user's statement are
  combined into (task M5-T157): the record read as "not in one", or a user's statement to the same
  effect where the record is silent, gives the engine "not in one" so the dwelling-unit rule applies
  and the limit is shown; "in one" (recorded), a disagreement, or "not known" gives the engine
  "inside one" so the rule is not applicable and the limit is withheld. The engine is given "not in
  one" if and only if the limit is shown (the invariant test holds that line).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

__all__ = [
    "CONDITION_KEYS",
    "WITHIN_100_FT",
    "Derived",
    "DensityDecision",
    "Presence",
    "Source",
    "angle_when_not_measured_degrees",
    "derive_conditions",
]


class Presence(Enum):
    """A recorded condition's three states, as the caller reads them from the city-record facts
    (without this module importing the decision step). ``NOT_READ`` is never taken as ``ABSENT``."""

    PRESENT = "present"
    ABSENT = "absent"
    NOT_READ = "not_read"


class DensityDecision(Enum):
    """The ONE special-density decision (task M5-T157), the record (ZR 12-10) combined with any
    user's statement by the decision step. Each maps to the engine's ``special_density_area`` value
    and the scope line's source: ``RECORDED_NOT_IN_ONE`` and ``USER_STATEMENT_NOT_IN_ONE`` give the
    engine "not in one" (the limit is shown); ``RECORDED_IN_ONE``, ``RECORD_STATEMENT_DISAGREE`` and
    ``NOT_KNOWN`` give it "in one" (the limit is withheld). A statement is never a recorded fact."""

    RECORDED_NOT_IN_ONE = "recorded_not_in_one"
    RECORDED_IN_ONE = "recorded_in_one"
    USER_STATEMENT_NOT_IN_ONE = "user_statement_not_in_one"
    RECORD_STATEMENT_DISAGREE = "record_statement_disagree"
    NOT_KNOWN = "not_known"


class Source(Enum):
    """Where a derived condition comes from - the scope line says this in plain words."""

    RECORDED = "recorded"
    MEASURED = "measured"
    USER_STATEMENT = "user_statement"
    RECORD_STATEMENT_DISAGREE = "record_statement_disagree"
    NOT_KNOWN = "not_known"
    NOT_APPLICABLE = "not_applicable"


# The within-100 comparison the rear-yard waiver uses (ZR 23-344(a) "within 100 feet of the point
# of intersection", inclusive). It is the SAME comparison the decision step uses on the SAME
# measured reach, so the value the engine is given can never disagree with what the decision step
# used for a shown rear yard.
WITHIN_100_FT = 100.0


def angle_when_not_measured_degrees() -> float:
    """The angle the engine is given when the corner angle is not measured. The rear-yard waiver
    applies only at "135 degrees or less" (ZR 23-344(a)); 136 degrees is past that limit, so the
    waiver never applies on it. "Within 100 feet: no" already withholds the waiver whenever the
    corner is not measured, so this value never reaches a shown result (the invariant test holds
    that line); it is chosen past the limit so the engine withholds on it in either case."""
    return 136.0


# The five scope keys this module derives, in the order the engine's scope block lists them.
CONDITION_KEYS = (
    "overlay_present",
    "special_district_present",
    "within_100_ft_of_street_line_intersection",
    "street_line_intersection_angle_degrees",
    "special_density_area",
)


@dataclass(frozen=True)
class Derived:
    """One of the five engine conditions: the ``engine_value`` to give the engine, the ``source``
    saying where it comes from, the measured ``figure`` (for a measured reach or angle) and the
    recorded ``code`` (for a recorded commercial overlay). ``figure``/``code`` are carried only for
    the scope statement; the engine reads only ``engine_value``."""

    engine_value: bool | float
    source: Source
    figure: float | None = None
    code: str | None = None


def overlay(presence: Presence, code: str | None = None) -> Derived:
    """overlay_present from the recorded commercial-overlay column. Present -> yes (carrying the
    recorded code); absent -> no; not read -> the engine is given "no overlay" (no note), recorded
    as not known so the scope line says so and every result that depends on it is withheld."""
    if presence is Presence.PRESENT:
        return Derived(True, Source.RECORDED, code=code)
    if presence is Presence.ABSENT:
        return Derived(False, Source.RECORDED)
    return Derived(False, Source.NOT_KNOWN)


def special_district(presence: Presence) -> Derived:
    """special_district_present from the recorded special-purpose-district column. Present -> yes;
    absent -> no; not read -> the engine is given "present" (every rule then asks for review, so
    every dependent result is withheld), recorded as not known."""
    if presence is Presence.PRESENT:
        return Derived(True, Source.RECORDED)
    if presence is Presence.ABSENT:
        return Derived(False, Source.RECORDED)
    return Derived(True, Source.NOT_KNOWN)


def within_100_and_angle(
    *, is_corner: bool | None, reach_ft: float | None, angle_deg: float | None,
) -> tuple[Derived, Derived]:
    """within_100_ft_of_street_line_intersection and street_line_intersection_angle_degrees from
    the corner reach and angle measured from the prepared outline and the site geometry.

    ``is_corner`` is True for a corner lot, False for an interior or through lot (no corner), None
    when the lot type was not read. A corner lot with both the reach and the angle measured gives
    the measured pair (within 100 feet is reach <= 100, the SAME comparison the decision step uses);
    a lot that is not a corner lot gives "not within 100 feet" and the past-limit angle, recorded as
    not applicable (there is no corner); otherwise (no corner measurement) the same values recorded
    as not known."""
    if is_corner is False:
        return (
            Derived(False, Source.NOT_APPLICABLE),
            Derived(angle_when_not_measured_degrees(), Source.NOT_APPLICABLE),
        )
    if reach_ft is not None and angle_deg is not None:
        return (
            Derived(reach_ft <= WITHIN_100_FT, Source.MEASURED, figure=reach_ft),
            Derived(angle_deg, Source.MEASURED, figure=angle_deg),
        )
    return (
        Derived(False, Source.NOT_KNOWN),
        Derived(angle_when_not_measured_degrees(), Source.NOT_KNOWN),
    )


def special_density(decision: DensityDecision) -> Derived:
    """special_density_area from the ONE special-density decision (task M5-T157). The engine is
    given "not in one" (False) for a record read outside both areas, or a user's statement to that
    effect where the record is silent; "in one" (True) for a record inside one, a disagreement, or
    a not-known record (then the dwelling-unit rule is not applicable, so the limit is withheld).
    The source carried for the scope line says where the decision came from."""
    if decision is DensityDecision.RECORDED_NOT_IN_ONE:
        return Derived(False, Source.RECORDED)
    if decision is DensityDecision.RECORDED_IN_ONE:
        return Derived(True, Source.RECORDED)
    if decision is DensityDecision.USER_STATEMENT_NOT_IN_ONE:
        return Derived(False, Source.USER_STATEMENT)
    if decision is DensityDecision.RECORD_STATEMENT_DISAGREE:
        return Derived(True, Source.RECORD_STATEMENT_DISAGREE)
    return Derived(True, Source.NOT_KNOWN)


def derive_conditions(
    *,
    overlay_presence: Presence,
    overlay_code: str | None,
    special_district_presence: Presence,
    is_corner: bool | None,
    reach_ft: float | None,
    angle_deg: float | None,
    density_decision: DensityDecision,
) -> dict[str, Derived]:
    """Derive all five engine conditions from the plain evidence states, keyed by the scope key
    each emits. The caller (the evidence entry) reads the engine value of each to build the engine's
    inputs and hands this mapping to the emit transform, which rewrites the five scope lines."""
    within, angle = within_100_and_angle(
        is_corner=is_corner, reach_ft=reach_ft, angle_deg=angle_deg,
    )
    return {
        "overlay_present": overlay(overlay_presence, overlay_code),
        "special_district_present": special_district(special_district_presence),
        "within_100_ft_of_street_line_intersection": within,
        "street_line_intersection_angle_degrees": angle,
        "special_density_area": special_density(density_decision),
    }
