"""Results contract 1.3.0 way-layer rule (task M5-T131, backlog row DB-171).

ONE pure function, no I/O. The JSON Schema of results contract 1.3.0 cannot compare
the keys of an answer's shown values with the keys of its ``value_states`` map, so the
schema alone accepts a 1.3.0 document in which a shown value has no way entry (an empty
map is the extreme case), a key is both shown and withheld, or a settled/conditional way
entry has no shown value. This module computes those breaches AFTER the schema has
passed, for BOTH results validators (``app.scenario.three_answers.contract`` and
``app.contracts.study_contracts``), so the two cannot drift.

It reads no file and raises nothing: :func:`results_way_violations` RETURNS the list of
breaches and each validator raises its own error type naming the answer, the key and the
rule broken. It imports nothing from this package's provenance serializer (it is a proven
non-serializer submodule). Below contract version ``1.3.0`` it returns no breaches: the
rule does nothing, so every 1.0.0 / 1.1.0 / 1.2.0 document is unaffected.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

__all__ = [
    "ANSWER_KEYS",
    "CONTRACT_VERSION_1_3_0",
    "WayRuleViolation",
    "results_way_violations",
]

CONTRACT_VERSION_1_3_0 = "1.3.0"

# The three answers that may carry a value_states way-layer (results.schema.json
# answers: floor_area_allowance, permitted_envelope and the building option).
ANSWER_KEYS = ("floor_area_allowance", "permitted_envelope", "building_option")

# A value is SHOWN (keeps its number in the answer's values[]) when its way is one of
# these; a withheld value carries no number and no values[] entry.
_SHOWN_WAYS = frozenset({"settled", "conditional"})


@dataclass(frozen=True)
class WayRuleViolation:
    """One breach of the 1.3.0 way-layer rule.

    ``answer`` is the answer name (floor_area_allowance / permitted_envelope /
    building_option); ``key`` is the value key involved; ``rule`` is a stable code for
    the clause broken; ``detail`` is a developer/log message naming the answer, the key
    and the rule.
    """

    answer: str
    key: str
    rule: str
    detail: str


def results_way_violations(document: Any) -> list[WayRuleViolation]:
    """Return the way-layer breaches of a results document that already passed the
    schema. An empty list means no breach.

    The rule (applied only when the document declares contract version 1.3.0, in every
    AVAILABLE answer; below 1.3.0 it does nothing):

    1. every shown value (a key of the answer's ``values``) has exactly one way entry in
       ``value_states`` and it is ``settled`` or ``conditional``;
    2. every ``settled`` / ``conditional`` way entry belongs to a shown value;
    3. a ``withheld`` entry belongs to no shown value.

    ``value_states`` is a map, so a key has at most one entry; "exactly one" means the
    entry is present and its way is settled or conditional. An available answer always
    has at least one shown value because ``values`` carries ``minItems: 1`` in the
    schema, so an all-withheld available answer (row DB-171 F4) is refused by the schema
    before this rule, never here.
    """
    if not isinstance(document, Mapping):
        return []
    if document.get("contract_version") != CONTRACT_VERSION_1_3_0:
        return []
    answers = document.get("answers")
    if not isinstance(answers, Mapping):
        return []

    violations: list[WayRuleViolation] = []
    for answer_name in ANSWER_KEYS:
        answer = answers.get(answer_name)
        if not isinstance(answer, Mapping) or answer.get("status") != "available":
            continue  # a not-available answer carries no value_states
        violations.extend(_answer_violations(answer_name, answer))
    return violations


def _shown_keys(answer: Mapping[str, Any]) -> list[str]:
    """The keys of an answer's shown values (values[]), in document order."""
    values = answer.get("values")
    keys: list[str] = []
    if isinstance(values, Sequence) and not isinstance(values, (str, bytes)):
        for value in values:
            if isinstance(value, Mapping) and isinstance(value.get("key"), str):
                keys.append(value["key"])
    return keys


def _answer_violations(answer_name: str, answer: Mapping[str, Any]) -> list[WayRuleViolation]:
    shown = _shown_keys(answer)
    shown_set = set(shown)
    states = answer.get("value_states")
    if not isinstance(states, Mapping):
        states = {}  # null or absent map: every shown value is settled by silence

    # Walk a de-duplicated union of the shown keys (values[] order) and the map keys
    # (map order), so a key yields at most one breach and the order is deterministic.
    ordered: list[str] = []
    seen: set[str] = set()
    for key in [*shown, *states.keys()]:
        if key not in seen:
            seen.add(key)
            ordered.append(key)

    out: list[WayRuleViolation] = []
    for key in ordered:
        is_shown = key in shown_set
        entry = states.get(key)
        way = entry.get("way") if isinstance(entry, Mapping) else None
        if is_shown and way is None:
            out.append(
                WayRuleViolation(
                    answer_name,
                    key,
                    "shown_value_has_no_way_entry",
                    f"answer {answer_name!r}: shown value {key!r} has no way entry in "
                    "value_states (every shown value must be settled or conditional, "
                    "so none is settled by silence)",
                )
            )
        elif is_shown and way == "withheld":
            out.append(
                WayRuleViolation(
                    answer_name,
                    key,
                    "shown_value_marked_withheld",
                    f"answer {answer_name!r}: value {key!r} is shown in values[] but its "
                    "way entry is 'withheld' (a shown value is settled or conditional; a "
                    "withheld value carries no number and is not shown)",
                )
            )
        elif not is_shown and way in _SHOWN_WAYS:
            out.append(
                WayRuleViolation(
                    answer_name,
                    key,
                    "way_entry_for_no_shown_value",
                    f"answer {answer_name!r}: way entry {key!r} is {way!r} but no shown "
                    "value has that key (a settled or conditional entry must belong to a "
                    "shown value)",
                )
            )
        # not shown + withheld  -> allowed: that is what withheld means
        # shown + settled/conditional -> the correct case
        # An unknown `way`, or any value_states entry on a not-available answer, is refused by
        # the schema, which both validators run before this rule; this rule is a check AFTER
        # the schema, so those cases never reach here.
    return out
