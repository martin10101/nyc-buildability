#!/usr/bin/env python3
"""Step-P4 reference-case constants and guards (M4-T032).

Pure stdlib (no import from the rule engine, the scenario engine or any program
output). It holds the data and the extra rules the step-P4 case needs, so the
checker next to it does not grow past its focus:

* ``STEP_P4_READINGS`` - the two step-P4 readings, each saved unchanged below a
  short header, with the digest that pins the whole saved file (the checker's
  :func:`_reading_digest_errors` consumes it, as for the step-P1/overlay/step-P3
  pairs).
* ``STEP_P4_READING_STEMS`` - the two reading stems a step-P4 row's source
  reference must name, so a value rests on both readings (the "both readings" rule).
* :func:`must_stay_not_known_errors` - the rows the two step-P4 readings do not
  jointly settle (both read "not known", or the two readings differ) must carry
  no value.

The checker imports this module and wires these in; nothing here imports the
checker, so there is no cycle.
"""
from __future__ import annotations

STEP_P4_CASE_ID = "step-p4-worked"

# The two step-P4 readings a step-P4 row must name (a value needs both to agree).
STEP_P4_READING_STEMS = (
    "return-independent-hand-calculation-9",
    "return-independent-hand-calculation-10",
)

# The two step-P4 readings (task M4-T032), each saved unchanged below a short
# header. The digest pins the whole saved file so any later edit is caught.
STEP_P4_READINGS = {
    "return-independent-hand-calculation-9.md": {
        "marker": "ONE HARD RULE",
        "digest": "d49c8bf2344a285b034226bf167fe8d928f8d82d092b990d57e46d644aff579f",
    },
    "return-independent-hand-calculation-10.md": {
        "marker": "one hard rule",
        "digest": "d46fd0e7b75b6751a1b63f1101d75ef7983c0a9ba159209ccecc5588463eb4d9",
    },
}

# Rows the two step-P4 readings do not jointly settle: both read "not known"
# (the real lot's prevailing street wall frontage - no neighbouring-building
# data), or the two readings differ within the row (ZR 23-443, where its
# paragraph (c) Limited-Height-District reading differs between the two). They
# must carry no number.
MUST_STAY_NOT_KNOWN = {
    STEP_P4_CASE_ID: {
        "real-lot-prevailing-frontage",
        "zr-23-443-reach",
    },
}


def must_stay_not_known_errors(case_id: str, data: dict) -> list[str]:
    """A step-P4 row the two readings do not jointly settle must be "not known";
    giving it a value is refused (a value needs both readings to agree)."""
    rows = MUST_STAY_NOT_KNOWN.get(case_id, set())
    errs: list[str] = []
    for row in data.get("rows", []):
        if row.get("row_id") in rows:
            kind = row.get("expected", {}).get("kind")
            if kind != "not_known":
                errs.append(
                    f"{case_id}/{row.get('row_id')}: the two step-P4 readings do not jointly "
                    f"settle this, so it must be 'not known', not {kind!r}"
                )
    return errs
