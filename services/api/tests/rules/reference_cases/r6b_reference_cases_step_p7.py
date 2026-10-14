#!/usr/bin/env python3
"""Step-P7 reference-case constants and guards (M5-T176).

Pure stdlib (no import from the rule engine, the scenario engine or any program
output; it imports nothing from ``app``). It holds the data and the extra rules the
step-P7 case needs, so the checker next to it does not grow past its focus. The
step-P7 case (``short-block-rear-yard``) is the two independent readings of
ZR 23-344(b) (the short dimension of a block) and 23-344(c)(3), written into the
R6B reference cases as one case: the reading of what 23-344(b) measures and whether
its thresholds are strict, of 23-344(c)/(c)(3), of how 23-342/23-343/23-344 fit
together, the ten made-up boundary cases M1 to M10, and the real lot (215-16
Northern Boulevard, lot 70 of block 7334) under Z1 (lot 70 alone) and Z2 (lots 70
and 1 together) on each measurement basis.

* ``STEP_P7_READINGS`` - the two step-P7 readings, each saved unchanged below a
  short header, with the digest that pins the whole saved file (the checker's
  :func:`_reading_digest_errors` consumes it, as for the earlier pairs).
* ``STEP_P7_READING_STEMS`` - the two reading stems a step-P7 row's source
  reference must name, so a value rests on both readings (the "both readings" rule).
* :func:`must_stay_not_known_errors` - the rows the two readings do not jointly
  settle (both read "not known", or the two readings differ on the measured figure,
  or the governing basis the text does not fix) must carry no value.
* :func:`quantity_basis_errors` - every quantity a row carries names exactly one of
  the nine measurement bases of ``tools/research_record_check.py`` QUANTITY_BASES,
  so no quantity is basis-less and none carries two (S7).
* :func:`real_lot_rear_yard_errors` - a real-lot row quotes ZR 23-344 and records no
  unconditional "no rear yard": every "no rear yard" reading on the real lot names
  its condition (the zoning lot, the measurement basis, or the point/street line it
  is measured from) (S8; owner rows R037, R079).

The checker imports this module and wires these in; nothing here imports the
checker, so there is no cycle.
"""
from __future__ import annotations

STEP_P7_CASE_ID = "short-block-rear-yard"

# The two step-P7 readings a step-P7 row must name (a value needs both to agree).
STEP_P7_READING_STEMS = (
    "return-independent-hand-calculation-15",
    "return-independent-hand-calculation-16",
)

# The two step-P7 readings (task M5-T176), each saved unchanged below a short
# header. The digest pins the whole saved file so any later edit is caught.
STEP_P7_READINGS = {
    "return-independent-hand-calculation-15.md": {
        "marker": "ONE HARD RULE",
        "digest": "ba7efca9a4fc2e780da8a749b7dccaf8d4c9d46b0addf3d00b626f06c79edb67",
    },
    "return-independent-hand-calculation-16.md": {
        "marker": "HARD-RULE COMPLIANCE",
        "digest": "1c8069254e582804f285a4ee2bd907378f83fe94a7ef5a6afced8643f10a064e",
    },
}

# The nine measurement bases. Mirrors tools/research_record_check.py QUANTITY_BASES
# (the test asserts this constant equals that authoritative set, so it never drifts);
# kept here as a frozenset so the support module imports nothing outside stdlib.
QUANTITY_BASES = frozenset({
    "law", "deed", "survey", "printed_tax_map", "approved_plan",
    "filing_attribute", "administrative_record", "gis", "derived",
})
QUANTITY_KEYS = {"name", "value", "unit", "basis"}

# Rows the two step-P7 readings do not jointly settle to a single value: both read
# "not known", or the two readings give different measured figures, or the governing
# measurement basis is one the captured text does not fix. They must carry no value.
#  - b-measurement-basis / b-within-100-feet / b-exact-100-ft: both readings read
#    that the captured text does not fix the basis, the method, or the exact-100-ft
#    edge (unresolved law);
#  - fit-b-c-overlap: both readings read that the text sets no priority where (b) and
#    (c) overlap (unresolved law);
#  - M4 / M10: both readings read "not known" (the measurement source / the method
#    for non-parallel streets is not fixed);
#  - real-lot-short-dimension: the two readings give different centreline figures and
#    the governing basis is unresolved;
#  - real-lot-alley / real-lot-z1-rear-yard / real-lot-z2-rear-yard /
#    real-lot-beyond-100-sliver: a missing fact about the property, or the unresolved
#    basis, leaves the answer open.
MUST_STAY_NOT_KNOWN = {
    STEP_P7_CASE_ID: {
        "b-measurement-basis",
        "b-within-100-feet",
        "b-exact-100-ft",
        "fit-b-c-overlap",
        "M4",
        "M10",
        "real-lot-short-dimension",
        "real-lot-alley",
        "real-lot-z1-rear-yard",
        "real-lot-z2-rear-yard",
        "real-lot-beyond-100-sliver",
    },
}

# A real-lot row (its id starts with this) must quote ZR 23-344 and may record no
# unconditional "no rear yard".
_REAL_LOT_PREFIX = "real-lot"
_NO_REAR_YARD_PHRASES = ("no rear yard", "no #rear yard#")
# Words that condition a "no rear yard" reading (the zoning lot, the measurement
# basis, the street line / point it is measured from, or that it is not settled).
_CONDITION_TOKENS = (
    "within 100 feet", "within 100 ft", "basis", "zoning lot", "street line",
    "not known", "not settled", "not sure", "condition", "survey", "centreline",
    "centerline", "measurement",
)


def must_stay_not_known_errors(case_id: str, data: dict) -> list[str]:
    """A step-P7 row the two readings do not jointly settle (or where they differ on
    the measured figure, or the governing basis the text does not fix) must be "not
    known"; giving it a value is refused (a value needs both readings to agree on the
    same basis)."""
    rows = MUST_STAY_NOT_KNOWN.get(case_id, set())
    errs: list[str] = []
    for row in data.get("rows", []):
        if row.get("row_id") in rows:
            kind = row.get("expected", {}).get("kind")
            if kind != "not_known":
                errs.append(
                    f"{case_id}/{row.get('row_id')}: the two step-P7 readings do not jointly "
                    f"settle this (or they differ on the measured figure, or the governing basis "
                    f"is unresolved), so it must be 'not known', not {kind!r}"
                )
    return errs


def quantity_basis_errors(case_id: str, row: dict) -> list[str]:
    """Every quantity a row carries names exactly one of the nine measurement bases;
    a quantity with no basis, or with a basis outside the nine, or a basis that is not
    a single value, is refused (S7)."""
    if case_id != STEP_P7_CASE_ID:
        return []
    errs: list[str] = []
    rid = row.get("row_id", "?")
    for q in row.get("quantities", []):
        if not isinstance(q, dict) or set(q) != QUANTITY_KEYS:
            errs.append(f"{case_id}/{rid}: a quantity's keys differ from the fixed set "
                        f"{sorted(QUANTITY_KEYS)}")
            continue
        basis = q.get("basis")
        if not isinstance(basis, str) or not basis.strip():
            errs.append(f"{case_id}/{rid}: quantity {q.get('name')!r} carries no measurement "
                        "basis (every quantity names exactly one of the nine bases)")
            continue
        if basis not in QUANTITY_BASES:
            errs.append(f"{case_id}/{rid}: quantity {q.get('name')!r} basis {basis!r} is not one "
                        f"of the nine bases {sorted(QUANTITY_BASES)}")
    return errs


def real_lot_rear_yard_errors(case_id: str, data: dict) -> list[str]:
    """A real-lot row quotes ZR 23-344 and records no unconditional 'no rear yard':
    where a real-lot row's value or reason says 'no rear yard' it must also name a
    condition (the zoning lot, the measurement basis, or the street line / point it is
    measured from), so the corner test is never worded as the only exception (S8)."""
    if case_id != STEP_P7_CASE_ID:
        return []
    errs: list[str] = []
    for row in data.get("rows", []):
        rid = row.get("row_id", "?")
        if not rid.startswith(_REAL_LOT_PREFIX):
            continue
        sections = " ".join(str(c.get("section", "")) for c in row.get("citations", []))
        if "23-344" not in sections:
            errs.append(f"{case_id}/{rid}: a real-lot row must quote ZR 23-344")
        exp = row.get("expected", {})
        text = f"{exp.get('value', '')} {exp.get('reason', '')}".lower()
        if any(p in text for p in _NO_REAR_YARD_PHRASES) and not any(
            t in text for t in _CONDITION_TOKENS
        ):
            errs.append(
                f"{case_id}/{rid}: a real-lot 'no rear yard' reading must name its condition "
                "(the zoning lot, the measurement basis, or the street line it is measured from); "
                "no unconditional 'no rear yard' is recorded for the real lot"
            )
    return errs
