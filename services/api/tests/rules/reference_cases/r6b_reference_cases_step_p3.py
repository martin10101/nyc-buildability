#!/usr/bin/env python3
"""Step-P3 reference-case constants and guards (M4-T030).

Pure stdlib (no import from the rule engine, the scenario engine or any program
output). It holds the data and the two extra rules the step-P3 case needs, so the
520-line checker next to it does not grow past its focus:

* ``STEP_P3_READINGS`` - the two step-P3 readings, each saved unchanged below a
  short header, with the digest that pins the whole saved file (the checker's
  :func:`_reading_digest_errors` consumes it, as for the step-P1/overlay pairs).
* ``STEP_P3_READING_STEMS`` - the two reading stems a step-P3 row's source
  reference must name, so a value rests on both readings (the "both readings" rule).
* :func:`must_stay_not_known_errors` - the rows the two step-P3 readings do not
  jointly settle (both read "not known") must carry no value.
* :func:`pinned_coverage_errors` - the whole-lot corner-coverage rows that must
  NOT move on the step-P3 readings' passing Q7c remark ("100 percent for this
  corner lot"), which neither reading worked through the corner-lot-portion rule.

The checker imports this module and wires these in; nothing here imports the
checker, so there is no cycle.
"""
from __future__ import annotations

STEP_P3_CASE_ID = "step-p3-worked"

# The two step-P3 readings a step-P3 row must name (a value needs both to agree).
STEP_P3_READING_STEMS = (
    "return-independent-hand-calculation-7",
    "return-independent-hand-calculation-8",
)

# The two step-P3 readings (task M4-T030), each saved unchanged below a short
# header. The digest pins the whole saved file so any later edit is caught.
STEP_P3_READINGS = {
    "return-independent-hand-calculation-7.md": {
        "marker": "ONE HARD RULE",
        "digest": "c0f09e913f4d274f3082553be50ee05cd3f42fb7ce42978d4373a88b381ae1c3",
    },
    "return-independent-hand-calculation-8.md": {
        "marker": "ONE HARD RULE",
        "digest": "9c2b3d263e49a4396af922d5e709b1e051a95373029f775002a2920e96e8d10d",
    },
}

# Rows the two step-P3 readings do not jointly settle (both read "not known"):
# they must carry no number (a value is recorded only where both readings settle
# the point on the same basis).
MUST_STAY_NOT_KNOWN = {
    STEP_P3_CASE_ID: {
        "real-lot-lot-width",
        "real-lot-rear-yard-beyond-corner",
        "corner-150x100-rear-yard-beyond-corner",
        "base-plane-real-lot",
    },
}

# The whole-lot corner-coverage rows that must NOT move on the step-P3 readings'
# passing Q7c remark ("the standard coverage for this corner lot is 100 percent"),
# which neither reading worked through the ZR 12-10 corner-lot-portion rule. Each
# stays "not known" (its per-portion reading is recorded elsewhere).
PINNED_COVERAGE_ROWS = {
    ("real-lot", "L5"): ("not_known", None),
    ("corner-reach", "real-lot-coverage"): ("not_known", None),
    ("step-p1-worked", "corner-150x100-coverage"): ("not_known", None),
    ("step-p1-worked", "corner-200x120-coverage"): ("not_known", None),
}


def must_stay_not_known_errors(case_id: str, data: dict) -> list[str]:
    """A step-P3 row the two readings do not jointly settle must be "not known";
    giving it a value is refused (a value needs both readings to agree)."""
    rows = MUST_STAY_NOT_KNOWN.get(case_id, set())
    errs: list[str] = []
    for row in data.get("rows", []):
        if row.get("row_id") in rows:
            kind = row.get("expected", {}).get("kind")
            if kind != "not_known":
                errs.append(
                    f"{case_id}/{row.get('row_id')}: the two step-P3 readings do not jointly "
                    f"settle this, so it must be 'not known', not {kind!r}"
                )
    return errs


def pinned_coverage_errors(load_case) -> list[str]:
    """The four whole-lot corner-coverage rows must keep their "not known" kind and
    no value: the step-P3 readings' Q7c "100 percent for this corner lot" is a
    passing remark, not a reading of whole-lot coverage, and must not move them."""
    errs: list[str] = []
    for (case_id, row_id), (want_kind, want_value) in PINNED_COVERAGE_ROWS.items():
        row = next((r for r in load_case(case_id)["rows"] if r["row_id"] == row_id), None)
        if row is None:
            errs.append(f"{case_id}/{row_id}: pinned corner-coverage row is missing")
            continue
        exp = row.get("expected", {})
        if exp.get("kind") != want_kind or exp.get("value") != want_value:
            errs.append(
                f"{case_id}/{row_id}: this whole-lot corner-coverage row must stay "
                f"{want_kind}/{want_value!r} (the step-P3 Q7c '100 percent' is a passing remark, "
                f"not a reading of whole-lot coverage), got {exp.get('kind')}/{exp.get('value')!r}"
            )
    return errs
