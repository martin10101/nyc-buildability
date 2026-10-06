"""The add-on catalogue as DATA, not prose (task A-06, plan section 6; M1-25; directive
D-090:D-090-R001).

Each add-on is a typed record: its group (plan section 6 A/B/C/D), whether it is automatic
(always on) or an optional switch (starts off), the Lane A rule id(s) it switches, the
generator inputs it changes, what it requires in plain English, and whether it selects the
ZR 23-22 / ZR 23-432 qualifying-housing columns. EXCLUSIONS are COMPUTED, never written as a
sentence per pair: two add-ons conflict exactly when they set the same generator input to
different values (for example two housing programs), so a development can apply only one.

Slice 1 (task A-06) builds Groups A and B for the R6-R12 contextual family. The add-ons whose
reviewed Lane A rule is not in the registry (community facility, choice of bulk rules,
ground-floor commercial, certification transfers) stay in the catalogue as NOT available with
reason_kind ``rule_not_implemented`` - never a guessed number. Groups C and D are out of this
slice (task A-12) and are listed the same way; Group D2 never produces a number at all.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

# Plan section 6 catalogue groups.
GROUP_A = "A"  # as-of-right
GROUP_B = "B"  # certification
GROUP_C = "C"  # neighbor (depends on an agreement)
GROUP_D1 = "D1"  # approval with a text maximum
GROUP_D2 = "D2"  # variance / rezoning - opportunity note only, never a number

# Housing programs that select the ZR 23-22 (FAR) and ZR 23-432 (height) qualifying columns.
# These come straight from the rule-table input enum (r6b-qualifying-housing-far), not invented.
QUALIFYING_PROGRAMS = frozenset(
    {"qualifying_affordable_housing", "qualifying_senior_housing"}
)


@dataclass(frozen=True)
class AddOn:
    """One catalogue add-on. Immutable and hashable (``input_changes`` is a tuple of pairs),
    so an add-on can live in a selection set."""

    addon_id: str
    group: str
    label: str
    automatic: bool
    rule_ids: tuple[str, ...]
    # Generator inputs this add-on switches, as (input_key, value) pairs. Empty for a
    # geometry-driven automatic add-on or an add-on with no reviewed rule.
    input_changes: tuple[tuple[str, object], ...]
    requires: tuple[str, ...]
    selects_qualifying_housing: bool = False

    @property
    def optional(self) -> bool:
        return not self.automatic

    def input_change_map(self) -> dict[str, object]:
        return {key: value for key, value in self.input_changes}


def conflicting_input_keys(first: AddOn, second: AddOn) -> tuple[str, ...]:
    """The input keys both add-ons set to DIFFERENT values - the computed basis of an
    exclusion (never a hand-written per-pair sentence). Order-stable (sorted)."""
    first_map = first.input_change_map()
    second_map = second.input_change_map()
    shared = set(first_map) & set(second_map)
    return tuple(sorted(key for key in shared if first_map[key] != second_map[key]))


def conflicts(first: AddOn, second: AddOn) -> bool:
    """True when the two add-ons cannot be applied together (they set a shared input to
    different values). An add-on never conflicts with itself."""
    if first.addon_id == second.addon_id:
        return False
    return bool(conflicting_input_keys(first, second))


def is_available(addon: AddOn, rule_ids: frozenset[str]) -> bool:
    """An add-on is available only when it names at least one Lane A rule AND every named rule
    is indexed in the registry. An add-on with no reviewed rule is never available: its gain is
    ``not_available`` with reason_kind ``rule_not_implemented`` (never a guessed number)."""
    if not addon.rule_ids:
        return False
    return all(rule_id in rule_ids for rule_id in addon.rule_ids)


def unavailable_reason(addon: AddOn) -> str:
    """The computed reason an add-on is not available in this slice (rule_not_implemented).
    Derived from the add-on's own rule_ids - no per-add-on sentence."""
    if not addon.rule_ids:
        return (
            f"No reviewed Lane A rule for '{addon.label}' in this slice "
            "(task A-12); not a guessed number."
        )
    missing = ", ".join(addon.rule_ids)
    return f"Rule(s) not built for this district yet: {missing}."


# --- The slice-1 catalogue (plan section 6 starting list, R6-R12 contextual family) --------
#
# Automatic Group A add-ons are always applied by the generator and never appear as a gain
# switch; optional add-ons start off. Only the two qualifying-housing add-ons carry a reviewed
# rule in this slice, so only they produce a number; the rest are honestly not_available.
_CATALOGUE: tuple[AddOn, ...] = (
    # Group A - as-of-right, automatic.
    AddOn(
        addon_id="wide_street_portion",
        group=GROUP_A,
        label="Wide-street portion",
        automatic=True,
        rule_ids=("r6-r7-r8-wide-street-conditional-far",),
        input_changes=(),
        requires=(
            "Any part of the zoning lot within 100 ft of a wide street (ZR 23-22 footnote 1); "
            "R6B carries no wide-street increase.",
        ),
    ),
    AddOn(
        addon_id="corner_lot_coverage",
        group=GROUP_A,
        label="Corner-lot coverage",
        automatic=True,
        rule_ids=("r6b-lot-coverage", "r6b-rear-yard-corner-waiver"),
        input_changes=(),
        requires=("A corner lot (ZR 23-362 coverage, ZR 23-344(a) rear-yard waiver).",),
    ),
    # Group A - as-of-right, optional switches.
    AddOn(
        addon_id="qualifying_affordable_housing",
        group=GROUP_A,
        label="Qualifying affordable housing (City of Yes)",
        automatic=False,
        rule_ids=("r6b-qualifying-housing-far", "r6b-height"),
        input_changes=(("housing_program", "qualifying_affordable_housing"),),
        requires=(
            "A development containing qualifying affordable housing (ZR 23-22, ZR 23-432) - a "
            "separate legal determination this app does not make.",
        ),
        selects_qualifying_housing=True,
    ),
    AddOn(
        addon_id="qualifying_senior_housing",
        group=GROUP_A,
        label="Qualifying senior housing (City of Yes)",
        automatic=False,
        rule_ids=("r6b-qualifying-housing-far", "r6b-height"),
        input_changes=(("housing_program", "qualifying_senior_housing"),),
        requires=(
            "A development containing qualifying senior housing (ZR 23-22, ZR 23-432) - a "
            "separate legal determination this app does not make.",
        ),
        selects_qualifying_housing=True,
    ),
    AddOn(
        addon_id="community_facility_floor_area",
        group=GROUP_A,
        label="Community-facility floor area",
        automatic=False,
        rule_ids=(),
        input_changes=(("housing_program", "community_facility"),),
        requires=("A reviewed community-facility floor-area rule (task A-12).",),
    ),
    AddOn(
        addon_id="choice_of_bulk_rules",
        group=GROUP_A,
        label="Choice of bulk rules (Quality Housing vs height factor)",
        automatic=False,
        rule_ids=(),
        input_changes=(),
        requires=("A reviewed bulk-rule-choice rule (task A-12).",),
    ),
    AddOn(
        addon_id="ground_floor_commercial",
        group=GROUP_A,
        label="Ground-floor commercial space",
        automatic=False,
        rule_ids=(),
        input_changes=(),
        requires=(
            "A reviewed ground-floor-commercial trade-off rule and a commercial overlay or "
            "commercial district (task A-12).",
        ),
    ),
    # Group B - certification, optional.
    AddOn(
        addon_id="certification_transfer",
        group=GROUP_B,
        label="Transfer by certification (e.g. from a nearby landmark)",
        automatic=False,
        rule_ids=(),
        input_changes=(),
        requires=("A reviewed certification-transfer rule (task A-12).",),
    ),
    # Group C - neighbor; never part of Best combination (plan section 6).
    AddOn(
        addon_id="neighbor_unused_floor_area",
        group=GROUP_C,
        label="A neighbor's unused floor area (estimate; needs an agreement)",
        automatic=False,
        rule_ids=(),
        input_changes=(),
        requires=(
            "A recorded agreement with a neighbor and a reviewed estimate rule (task A-12).",
        ),
    ),
    # Group D1 - approval with a text maximum; never part of Best combination.
    AddOn(
        addon_id="approval_with_text_maximum",
        group=GROUP_D1,
        label="Approval with a text maximum ('up to X with approval')",
        automatic=False,
        rule_ids=(),
        input_changes=(),
        requires=(
            "A City Planning special permit or authorization with a text maximum (task A-12).",
        ),
    ),
    # Group D2 - variance / rezoning; an opportunity note, never a number (plan section 6).
    AddOn(
        addon_id="variance_or_rezoning",
        group=GROUP_D2,
        label="Variance or rezoning (opportunity note; no number)",
        automatic=False,
        rule_ids=(),
        input_changes=(),
        requires=("Case-specific BSA findings or a rezoning; never a number.",),
    ),
)


def build_catalogue() -> tuple[AddOn, ...]:
    """The slice-1 add-on catalogue (plan section 6). A stable, deterministic tuple."""
    return _CATALOGUE


def optional_group_a_b(catalogue: Mapping[int, AddOn] | tuple[AddOn, ...]) -> tuple[AddOn, ...]:
    """The optional Group A and B add-ons, in catalogue order. These are the only add-ons that
    appear as gains and that 'Best combination' may choose (plan section 5 'Best combination ...
    uses only ... Groups A and B'; section 6). Groups C, D1 and D2 are excluded here."""
    entries = catalogue if isinstance(catalogue, tuple) else tuple(catalogue.values())
    return tuple(a for a in entries if a.optional and a.group in (GROUP_A, GROUP_B))
