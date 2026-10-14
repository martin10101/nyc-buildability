#!/usr/bin/env python3
"""Step-P8 reference-case constants and guards (M5-T177).

Pure stdlib (no import from the rule engine, the scenario engine or any program
output; it imports nothing from ``app``). It holds the data and the extra rules the
step-P8 case needs, so the checker next to it does not grow past its focus. The
step-P8 case (``placement-building-b``) is the two independent readings of where the
three-storey Building B (20,150 sq ft zoning floor area, 10-ft floor-to-floor) sits
on lot 70 of block 7334 (215-16 Northern Boulevard, Queens) under Z1 (lot 70 alone)
and how its floor area divides: the plate as zoning floor area per storey, the
footprint on the printed-tax-map basis reconciled with the plate, the placement and
offsets on that basis with the city-map (GIS) outline as a conflict check only, the
lot coverage and rear yard as far as both readings take them, and the area
allocation at the one stated 60 percent apartment-area share.

* ``STEP_P8_READINGS`` - the two step-P8 readings, each saved unchanged below a
  short header, with the digest that pins the whole saved file (the checker's
  :func:`_reading_digest_errors` consumes it, as for the earlier pairs).
* ``STEP_P8_READING_STEMS`` - the two reading stems a step-P8 row's source
  reference must name, so a value rests on both readings (the "both readings" rule).
* :func:`must_stay_not_known_errors` - the rows the two readings do not jointly
  settle (both read "not known", or the two readings differ on the figure, or the
  governing basis the text does not fix) must carry no value.
* :func:`quantity_basis_errors` - every quantity a row carries names exactly one of
  the nine measurement bases of ``tools/research_record_check.py`` QUANTITY_BASES,
  so no quantity is basis-less and none carries two (S7).
* :func:`placement_basis_errors` - a placement or coverage conclusion row names its
  basis (the printed tax map) and the Z1 zoning-lot condition; a row that omits
  either is refused (S6; owner rows R043, R082).
* :func:`plate_label_errors` - the plate and the footprint figure each carry the
  stated-measure label (zoning floor area per storey; no gross-up, exclusions or
  wall-thickness conversion worked) (S4; owner row R092).

The checker imports this module and wires these in; nothing here imports the
checker, so there is no cycle.
"""
from __future__ import annotations

STEP_P8_CASE_ID = "placement-building-b"

# The two step-P8 readings a step-P8 row must name (a value needs both to agree).
STEP_P8_READING_STEMS = (
    "return-independent-hand-calculation-17",
    "return-independent-hand-calculation-18",
)

# The two step-P8 readings (task M5-T177), each saved unchanged below a short
# header. The digest pins the whole saved file so any later edit is caught.
STEP_P8_READINGS = {
    "return-independent-hand-calculation-17.md": {
        "marker": "ONE-HARD-RULE STATEMENT",
        "digest": "7d6b923da87cb8f53028463c6d6d40e03e3e495b6dd0e1bcd453b30b9db76617",
    },
    "return-independent-hand-calculation-18.md": {
        "marker": "THE ONE HARD RULE",
        "digest": "0e166f96f4831c85c8cb68028366d0412a0bcb4b6b578325ab9739c1d8cf3743",
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

# Rows the two step-P8 readings do not jointly settle to a single value: both read
# "not known", or the governing basis is one the captured text / the facts do not
# fix. They must carry no value.
#  - physical-plate-not-checked: both readings record the plate only as zoning floor
#    area per storey and leave the physical plate unworked;
#  - gis-conflict-check: the printed-tax-map and the city-map (GIS) outline conflict
#    and no reading chooses between them, so no single figure;
#  - lot-coverage-whole-lot: the whole-lot coverage is read by portion and the
#    governing lot area conflicts, so no single whole-lot figure;
#  - rear-yard: not known under Z1 (the measurement basis and the adjoining lot-line
#    kind are unresolved).
MUST_STAY_NOT_KNOWN = {
    STEP_P8_CASE_ID: {
        "physical-plate-not-checked",
        "gis-conflict-check",
        "lot-coverage-whole-lot",
        "rear-yard",
    },
}

# Rows that record a placement or coverage conclusion: each must name its basis (the
# printed tax map) and the Z1 zoning-lot condition (S6). A placement/coverage row
# that omits either is refused; no conclusion is recorded without its conditions.
_PLACEMENT_ROWS = {
    STEP_P8_CASE_ID: {
        "placement-tax-map", "lot-coverage-max", "lot-coverage-whole-lot", "rear-yard",
    },
}
_BASIS_TOKENS = ("tax-map basis", "tax map basis", "printed-tax-map", "printed tax map")
_Z1_TOKENS = ("z1", "lot 70 alone")

# The rows whose figures carry the stated-measure label (S4): the plate and the
# footprint figure. The label guards against a figure presented as a physical plate.
_LABEL_ROWS = {STEP_P8_CASE_ID: {"plate", "footprint-tax-map"}}
_PLATE_LABEL = ("plate = zoning floor area per storey; no gross-up, exclusions or "
                "wall-thickness conversion worked")


def must_stay_not_known_errors(case_id: str, data: dict) -> list[str]:
    """A step-P8 row the two readings do not jointly settle (or where the governing
    basis the text / the facts do not fix) must be "not known"; giving it a value is
    refused (a value needs both readings to agree on the same basis)."""
    rows = MUST_STAY_NOT_KNOWN.get(case_id, set())
    errs: list[str] = []
    for row in data.get("rows", []):
        if row.get("row_id") in rows:
            kind = row.get("expected", {}).get("kind")
            if kind != "not_known":
                errs.append(
                    f"{case_id}/{row.get('row_id')}: the two step-P8 readings do not jointly "
                    f"settle this (or the governing basis is unresolved), so it must be 'not "
                    f"known', not {kind!r}"
                )
    return errs


def quantity_basis_errors(case_id: str, row: dict) -> list[str]:
    """Every quantity a row carries names exactly one of the nine measurement bases;
    a quantity with no basis, or with a basis outside the nine, or a basis that is not
    a single value, is refused (S7)."""
    if case_id != STEP_P8_CASE_ID:
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


def _row_text(row: dict) -> str:
    exp = row.get("expected", {})
    return " ".join([
        str(exp.get("value", "")), str(exp.get("reason", "")),
        str(row.get("quantity", "")), str(row.get("does_not_establish", "")),
    ]).lower()


def placement_basis_errors(case_id: str, data: dict) -> list[str]:
    """A placement or coverage conclusion row names its basis (the printed tax map)
    and the Z1 zoning-lot condition; a row that omits either is refused (S6). No
    placement or coverage conclusion is recorded without its conditions."""
    rows = _PLACEMENT_ROWS.get(case_id, set())
    errs: list[str] = []
    for row in data.get("rows", []):
        if row.get("row_id") not in rows:
            continue
        text = _row_text(row)
        rid = row.get("row_id", "?")
        if not any(t in text for t in _BASIS_TOKENS):
            errs.append(f"{case_id}/{rid}: a placement or coverage conclusion must name its basis "
                        "(the printed-tax-map basis)")
        if not any(t in text for t in _Z1_TOKENS):
            errs.append(f"{case_id}/{rid}: a placement or coverage conclusion must name the Z1 "
                        "zoning-lot condition (lot 70 alone)")
    return errs


def plate_label_errors(case_id: str, data: dict) -> list[str]:
    """The plate and the footprint figure each carry the stated-measure label
    (zoning floor area per storey; no gross-up, exclusions or wall-thickness
    conversion worked), so neither figure is presented as a physical plate (S4)."""
    rows = _LABEL_ROWS.get(case_id, set())
    errs: list[str] = []
    found: set[str] = set()
    for row in data.get("rows", []):
        rid = row.get("row_id")
        if rid not in rows:
            continue
        found.add(rid)
        text = " ".join(str(v) for v in row.get("expected", {}).values())
        text = (text + " " + str(row.get("does_not_establish", ""))).lower()
        if _PLATE_LABEL not in text:
            errs.append(f"{case_id}/{rid}: the figure must carry the stated-measure label "
                        f"({_PLATE_LABEL!r})")
    for rid in sorted(rows - found):
        errs.append(f"{case_id}/{rid}: the labelled row is missing from the case")
    return errs
