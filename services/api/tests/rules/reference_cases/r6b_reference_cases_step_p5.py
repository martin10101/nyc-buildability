#!/usr/bin/env python3
"""Step-P5 reference-case constants and guards (M4-T035).

Pure stdlib (no import from the rule engine, the scenario engine or any program
output). It holds the data and the extra rules the step-P5 case needs, so the
checker next to it does not grow past its focus:

* ``STEP_P5_READINGS`` - the two step-P5 readings, each saved unchanged below a
  short header, with the digest that pins the whole saved file (the checker's
  :func:`_reading_digest_errors` consumes it, as for the step-P1/overlay/step-P3/
  step-P4 pairs).
* ``STEP_P5_READING_STEMS`` - the two reading stems a step-P5 row's source
  reference must name, so a value rests on both readings (the "both readings" rule).
* :func:`must_stay_not_known_errors` - the rows the two step-P5 readings do not
  jointly settle (both read "not known") must carry no value.

The checker imports this module and wires these in; nothing here imports the
checker, so there is no cycle.
"""
from __future__ import annotations

STEP_P5_CASE_ID = "step-p5-worked"

# The two step-P5 readings a step-P5 row must name (a value needs both to agree).
STEP_P5_READING_STEMS = (
    "return-independent-hand-calculation-11",
    "return-independent-hand-calculation-12",
)

# The two step-P5 readings (task M4-T035), each saved unchanged below a short
# header. The digest pins the whole saved file so any later edit is caught.
STEP_P5_READINGS = {
    "return-independent-hand-calculation-11.md": {
        "marker": "one hard rule",
        "digest": "a23fcfbbe505f83c0d06c4b8de02e4e8792498b4b4eac8fdd0c8a02444388f20",
    },
    "return-independent-hand-calculation-12.md": {
        "marker": "ONE HARD RULE",
        "digest": "36b568520d201ef0ba70fa8568f8ad70a299c635c76fe80dbbef1e52b899c95a",
    },
}

# Rows the two step-P5 readings do not jointly settle (both read "not known"):
# the made-up building's commercial floor area ratio and whole-building maximum
# (Article III, Chapter 3 not in the folder) and ZR 23-24's reach (its
# subsections not in the folder). They must carry no number. The benchmark
# rear-yard row is handled by the checker's READINGS_DIFFER (the two readings
# differ on the far-edge reach), so it is not repeated here.
MUST_STAY_NOT_KNOWN = {
    STEP_P5_CASE_ID: {
        "made-up-mixed-commercial-far",
        "made-up-mixed-whole-building-max",
        "zr-23-24-reach",
    },
}


def must_stay_not_known_errors(case_id: str, data: dict) -> list[str]:
    """A step-P5 row the two readings do not jointly settle must be "not known";
    giving it a value is refused (a value needs both readings to agree)."""
    rows = MUST_STAY_NOT_KNOWN.get(case_id, set())
    errs: list[str] = []
    for row in data.get("rows", []):
        if row.get("row_id") in rows:
            kind = row.get("expected", {}).get("kind")
            if kind != "not_known":
                errs.append(
                    f"{case_id}/{row.get('row_id')}: the two step-P5 readings do not jointly "
                    f"settle this, so it must be 'not known', not {kind!r}"
                )
    return errs
