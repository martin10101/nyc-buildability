"""Scope-line code of the three-way results emitter (task M5-T143; backlog DB-205 a).

Moved verbatim from ``three_way_document.py`` under CLAUDE.md principle 16 and
docs/CODE_MODULARITY_POLICY.md. Two pieces live here: the five engine-condition
scope lines (M5-T137, reading O36) and the two design-choice scope rows (M5-T139,
DB-204 a).

When the evidence entry hands the per-condition sources, the transform rewrites each
of the five scope rows to say, in plain words, where the condition comes from:
recorded, measured from the tax-map outline, the user's statement, or not known / not
applicable. The engine's own scope block and the schema stay read-only; the transform
rewrites only the row's value, basis and statement. When the entry hands no sources
the scope lines stay as the engine made them.

There is NO "not known" basis in the schema, so a not-known / not-applicable value
carries the stand-in it was given with basis 'assumed', while the statement says it is
not known / not applicable (reading O36; DB-196 holds the contract question). Every
statement here is one of the transform's texts (plain and true: no internal name, no
gap or reading number, no task id, never 'professional review'); the guard test over
the transform's texts covers them.

``three_way_document.py`` keeps every one of these names behind a compatibility facade
(ruling B2). This module imports from ``.engine_conditions`` only (a leaf), so no
import-guard list grows for it.
"""

from __future__ import annotations

from .engine_conditions import Derived, Source

_SCOPE_BASIS_BY_SOURCE = {
    Source.RECORDED: "city_records",
    Source.MEASURED: "approximate_tax_map",
    Source.USER_STATEMENT: "entered",
    Source.NOT_KNOWN: "assumed",
    Source.NOT_APPLICABLE: "assumed",
}

# The WORDS a scope line SHOWS for a condition that is not known or does not apply. The value the
# engine was given (the stand-in) is never shown as the scope row's value - a reader must not see a
# substitute figure for something not known (orchestrator correction of reading O36). The schema's
# scope_assumption value may be a string, and the unit is null for these words (the stand-in the
# engine received does not reach the emitted document). The statement still says it is not known /
# does not apply, what was taken for the calculation, and what is withheld.
_NOT_KNOWN_VALUE = "Not known"
_NOT_APPLICABLE_VALUE = "Not applicable"
_WORDS_VALUE_BY_SOURCE = {
    Source.NOT_KNOWN: _NOT_KNOWN_VALUE,
    Source.NOT_APPLICABLE: _NOT_APPLICABLE_VALUE,
}


# ---------------------------------------------------------------------------
# The two scope rows that carry a DESIGN CHOICE the user may make (M5-T139, DB-204 a). The engine's
# disclosure builder (read-only here) writes BOTH as "the default" (basis 'default'). When the
# caller's request CARRIED the choice, the transform rewrites only the row's basis (to 'entered')
# and its statement; the VALUE and UNIT are never touched. The keys match each scope row's `key`.
# ---------------------------------------------------------------------------
HOUSING_PROGRAM_KEY = "housing_program"
FLOOR_TO_FLOOR_KEY = "floor_to_floor_ft"
#: The two design-choice scope keys the user may make; the transform rewrites only these.
USER_CHOICE_KEYS = frozenset({HOUSING_PROGRAM_KEY, FLOOR_TO_FLOOR_KEY})

# Plain-words housing-program labels (study.schema.json vocabulary, closed): the document's own
# presentation labels. An unknown key falls back to itself so the sentence is never empty.
_HOUSING_PROGRAM_DISPLAY = {
    "standard_residence": "Standard residence",
    "qualifying_affordable_housing": "Qualifying affordable housing",
    "qualifying_senior_housing": "Qualifying senior housing",
}

# The two sentences the transform WRITES when the user made the choice (plain and true: no internal
# name, no task id, never 'professional review', never 'the default'). The guard test renders both.
USER_ENTERED_FLOOR_TO_FLOOR_STATEMENT = (
    "A {height}-foot floor-to-floor height was entered for this run."
)
USER_SELECTED_HOUSING_PROGRAM_STATEMENT = (
    "{program} was selected for this run as the housing program."
)


def _fmt_feet(value: float) -> str:
    return f"{value:.2f} feet"


def _fmt_degrees(value: float) -> str:
    whole = int(round(value))
    return f"{whole} degrees" if float(whole) == float(value) else f"{value:.1f} degrees"


def _scope_statement(key: str, derived: Derived) -> str:
    """The plain-words scope line for one of the five conditions, saying where it comes from."""
    source = derived.source
    if key == "overlay_present":
        if source is Source.RECORDED:
            if derived.engine_value:
                code = f" ({derived.code})" if derived.code else ""
                return f"A commercial overlay{code} is recorded for this lot in the city's records."
            return "The city's records list no commercial overlay for this lot."
        return (
            "Whether a commercial overlay applies to this lot is not known; every result that "
            "depends on it is withheld."
        )
    if key == "special_district_present":
        if source is Source.RECORDED:
            if derived.engine_value:
                return "A special purpose district is recorded for this lot in the city's records."
            return "The city's records list no special purpose district for this lot."
        return (
            "Whether a special purpose district applies to this lot is not known; a special "
            "purpose district is taken for the calculation, so every result that depends on it is "
            "withheld."
        )
    if key == "within_100_ft_of_street_line_intersection":
        if source is Source.MEASURED:
            reach = _fmt_feet(derived.figure)
            if derived.engine_value:
                return (
                    f"Measured from the tax-map outline, the lot's farthest point is {reach} from "
                    "the corner where its two street lines meet, within 100 feet of it."
                )
            return (
                f"Measured from the tax-map outline, the lot's farthest point is {reach} from the "
                "corner where its two street lines meet, more than 100 feet from it."
            )
        if source is Source.NOT_APPLICABLE:
            return (
                "This lot is not a corner lot, so whether it lies within 100 feet of a street-line "
                "corner does not apply."
            )
        return (
            "Whether the lot lies within 100 feet of the corner where two street lines meet is not "
            "known; it is taken as not within 100 feet for the calculation, so the rear yard that "
            "depends on it is withheld."
        )
    if key == "street_line_intersection_angle_degrees":
        if source is Source.MEASURED:
            return (
                "Measured from the tax-map outline, the lot's two street lines meet at about "
                f"{_fmt_degrees(derived.figure)}."
            )
        if source is Source.NOT_APPLICABLE:
            return (
                "This lot is not a corner lot, so the angle at which two street lines meet does "
                "not apply."
            )
        return (
            "The angle at which the lot's two street lines meet is not known; the rear yard that "
            "depends on it is withheld."
        )
    # special_density_area
    if source is Source.USER_STATEMENT:
        return (
            "The lot is taken to be outside a special density area because that was stated for "
            "this run; it is a statement, not a recorded fact."
        )
    return (
        "Whether the lot is in a special density area is not known; it is taken to be in one for "
        "the calculation, so the legal dwelling-unit limit that depends on it is withheld."
    )


def _user_choice_statement(key: str, value: object) -> str:
    """The plain-words scope line for a design choice the user made (M5-T139): the floor-to-floor
    height entered, or the housing program selected. ``value`` is read for the sentence only."""
    if key == FLOOR_TO_FLOOR_KEY:
        return USER_ENTERED_FLOOR_TO_FLOOR_STATEMENT.format(height=f"{float(value):g}")
    display = _HOUSING_PROGRAM_DISPLAY.get(value, value)
    return USER_SELECTED_HOUSING_PROGRAM_STATEMENT.format(program=display)


def _rewrite_scope_lines(
    doc: dict,
    condition_sources: dict[str, Derived] | None,
    user_choices: frozenset[str] | None,
) -> None:
    """Rewrite the scope rows the evidence entry can say more about: the five engine conditions from
    ``condition_sources`` (M5-T137), and the two design-choice rows (housing program, floor-to-floor
    height) named in ``user_choices`` when the user chose them (M5-T139). Every other row, and a
    design choice the user did NOT make, stays as the engine made it. Does nothing with no scope."""
    scope = doc.get("scope")
    if not isinstance(scope, dict):
        return
    assumptions = scope.get("assumptions")
    if not isinstance(assumptions, list):
        return
    sources = condition_sources if condition_sources is not None else {}
    choices = user_choices if user_choices is not None else frozenset()
    for row in assumptions:
        if not isinstance(row, dict):
            continue
        key = row.get("key")
        derived = sources.get(key)
        if derived is not None:
            row["basis"] = _SCOPE_BASIS_BY_SOURCE[derived.source]
            row["statement"] = _scope_statement(key, derived)
            words = _WORDS_VALUE_BY_SOURCE.get(derived.source)
            if words is not None:
                # Not known / not applicable: show the words, never the stand-in the engine
                # received; the unit is null (the stand-in does not reach the document).
                row["value"] = words
                row["unit"] = None
            else:
                # Recorded, measured or the user's statement: the real value (and its unit, as the
                # engine set it - degrees for the angle, null for the flags).
                row["value"] = derived.engine_value
            continue
        if key in choices and key in USER_CHOICE_KEYS:
            # A design choice the user made: basis 'entered' and a sentence that says so. The value
            # and the unit are NOT touched - only the basis and the statement move.
            row["basis"] = "entered"
            row["statement"] = _user_choice_statement(key, row["value"])

