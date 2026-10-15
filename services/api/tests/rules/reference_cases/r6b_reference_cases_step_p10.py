#!/usr/bin/env python3
"""Step-P10 reference-case constants and guards (M5-T185).

Pure stdlib (no import from the rule engine, the scenario engine or any program
output; it imports nothing from ``app``). It holds the data and the extra rules the
step-P10 case needs, so the checker next to it does not grow past its focus. The
step-P10 case (``benchmark-options-5-8-9-10``) is the agreed worked values of option
5 (ground-floor shops with residences above), option 8 (two buildings on one lot / a
divided lot - both meanings) and options 9-10 (shared housing; parking and the
transit zone) for the benchmark lot (215-16 Northern Boulevard, lot 70 of block 7334;
R6B with a C2-2 overlay; corner), read independently twice per option family and
confirmed by the same independent comparer as M5-T184.

Like the step-P9 case, this one case rests on THREE reading pairs plus a comparer, so
it is deliberately NOT registered in the checker's generic ``CASE_READINGS`` (which
forces one reading tuple on every row of a case). Instead the per-row reading pair is
enforced here by row-id prefix: an ``opt5-*`` row names readings -26 and -27, an
``opt8*`` row names -28 and -29, an ``opt9-*``/``opt910-*``/``opt10-*`` row names -30
and -31, and a shared row names the comparer -25 (shared with M5-T184, frozen there).

The checker wires in exactly two entries so it grows ~3 lines and stays under its
600-line cap (Risk 1):

* :func:`reading_digest_errors` - the six NEW reading files -26..-31 (two per family)
  are each present unchanged (digest pinned), carry their distinctive marker and the
  literal phrase "sealed folder", end with END-OF-REPORT, and do NOT claim "no outside
  access" (some readers read official pages live) (S1). The comparer -25 is pinned by
  step-P9 and is not re-pinned here.
* :func:`case_errors` - all the per-row and per-case guards for the step-P10 case,
  behind one entry: the per-row reading pair (S2), the rows that must stay not known
  (S4), every quantity on exactly one of the nine bases and never two bases combined
  (S6), the eligibility caveat on the use-permission rows and the "decides neither
  meaning" caveat on the owner-question rows (S5), the forbidden present-tense "not
  captured" wording (S5) and the rear-yard conditions (S8).

Nothing here imports the checker, so there is no cycle.
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import r6b_reference_cases_lib as lib  # noqa: E402

STEP_P10_CASE_ID = "benchmark-options-5-8-9-10"

# The six NEW reading files (two per family: option 5 = -26/-27; option 8 = -28/-29;
# options 9-10 = -30/-31), each saved unchanged below a short truthful header. The
# digest pins the whole saved file (header + the reader's verbatim return) so any later
# edit is caught (S1). The comparer -25 is pinned by step-P9 and is reused unchanged.
STEP_P10_READINGS = {
    "return-independent-hand-calculation-26.md": {
        "marker": "M5-T185 PROVENANCE -26 (OPTION 5, READING A)",
        "digest": "bb19e6f0398ff6640c471d65e2eac86afa2ab670c45955fb55bab8996b83c246",
    },
    "return-independent-hand-calculation-27.md": {
        "marker": "M5-T185 PROVENANCE -27 (OPTION 5, READING B)",
        "digest": "ed085e6e1921f86c0c65a49625f9f628a5bb8d6787a37bc438320d8105b37460",
    },
    "return-independent-hand-calculation-28.md": {
        "marker": "M5-T185 PROVENANCE -28 (OPTION 8, READING A)",
        "digest": "2e2f0f1d7f65bacaa7e8b0ac56934e57f45b2fc440b947d463b57714ff9cb9a5",
    },
    "return-independent-hand-calculation-29.md": {
        "marker": "M5-T185 PROVENANCE -29 (OPTION 8, READING B)",
        "digest": "285c427b78999009d6b2f74e551f21425d5c45d5b44d019b0f3996e31fbed6ee",
    },
    "return-independent-hand-calculation-30.md": {
        "marker": "M5-T185 PROVENANCE -30 (OPTIONS 9-10, READING A)",
        "digest": "6dbe12c7fbeb39ae58a2726af0aa8888c79ae60e865c83f2606eec6e2f2127f5",
    },
    "return-independent-hand-calculation-31.md": {
        "marker": "M5-T185 PROVENANCE -31 (OPTIONS 9-10, READING B)",
        "digest": "5066be9f12b3cdf7966fd6c3899dabbe499e5c202ef8febfb93bb7dc90f724c3",
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

# The per-row reading pair, by row-id prefix. A value is recorded only where both
# readings of that option family agree, so every option row must name both of its
# readings; a shared row names the comparer -25 (S2).
_PAIR_26_27 = ("return-independent-hand-calculation-26", "return-independent-hand-calculation-27")
_PAIR_28_29 = ("return-independent-hand-calculation-28", "return-independent-hand-calculation-29")
_PAIR_30_31 = ("return-independent-hand-calculation-30", "return-independent-hand-calculation-31")
COMPARER_STEM = "return-independent-hand-calculation-25"
READING_PAIRS = (
    ("opt5-", _PAIR_26_27),
    ("opt8", _PAIR_28_29),
    ("opt910-", _PAIR_30_31),
    ("opt9-", _PAIR_30_31),
    ("opt10-", _PAIR_30_31),
)

# Rows the two readings do not jointly settle to one value on one basis, or where the
# captured text does not fix the point. They must carry no value (S4).
MUST_STAY_NOT_KNOWN = {
    STEP_P10_CASE_ID: {
        "opt5-storey-limit",
        "opt5-commercial-rear-yard",
        "opt5-lot-coverage-whole-lot",
        "opt5-overlay-mapped-line",
        "opt5-select-commercial-overlay-status",
        "opt5-street-wall-final-line",
        "opt8a-windows-courts",
        "opt8b-aggregate-dwelling-units",
        "opt8b-coverage-by-half",
        "opt8b-interior-half-rear-yard",
        "opt8b-min-lot-area",
        "opt8-which-meaning",
        "opt910-rooming-vs-dwelling-classification",
        "opt10-distinct-meaning",
        "opt910-shared-housing-framework",
        "real-lot-missing-facts",
    },
}

# The use-permission rows must carry a does_not_establish caveat that the case decides
# no eligibility (S5).
_ELIGIBILITY_ROW_IDS = {"opt5-retail-use-grade", "opt910-use-permission"}
_ELIGIBILITY_CAVEAT = "decides no eligibility"

# The owner-question rows must carry a does_not_establish caveat that the case decides
# neither meaning of option 8 (N1) nor option 10 (N2) (S5).
_MEANING_ROW_IDS = {"opt8-which-meaning", "opt10-distinct-meaning"}
_MEANING_CAVEAT = "decides neither meaning"

# No present-tense "not captured" wording anywhere outside the change log (S5): the
# proven convention names uncaptured sections in prose ("the readers did not have ...").
_FORBIDDEN_WORDING = (
    "does not hold", "is not captured", "are not captured", "not captured", "uncaptured",
)

# The rear-yard rows: each must name its condition and the zoning-lot scope, and the
# corner waiver must name the within-100-feet-of-a-135-degree-corner condition (S8).
_REAR_YARD_ROWS = {"opt5-commercial-rear-yard", "opt8b-interior-half-rear-yard"}
_CORNER_WAIVER_ROW = "opt5-commercial-rear-yard"
_RY_CONDITION = ("within 100 feet", "within 100 ft", "135 degrees", "not known")
_RY_SCOPE = ("zoning lot", "per zoning lot", "z1", "lot 70 alone")

# The recorded area (administrative_record) and the GIS area (gis) must never be
# combined in one arithmetic step (S6); every figure uses the recorded 10,075.
_RECORDED_AREA = "10075"
_GIS_AREA = "10387.99"


# --------------------------------------------------------------------------
# S1: the six new reading files are present unchanged
# --------------------------------------------------------------------------
def reading_digest_errors() -> list[str]:
    """The six new step-P10 reading files are present unchanged: each carries its marker
    and END-OF-REPORT, says it was made from the "sealed folder" (here the pinned
    read-only captures in the detached checkout), does NOT claim "no outside access"
    (some readers read official pages live), and hashes to the recorded digest, so any
    later edit to a saved reading is caught (S1)."""
    errs: list[str] = []
    for name, spec in STEP_P10_READINGS.items():
        path = lib.PROVENANCE_DIR / name
        if not path.is_file():
            errs.append(f"step-P10 reading missing: {name}")
            continue
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        if spec["marker"] not in text:
            errs.append(f"step-P10 reading {name} does not carry its distinctive marker")
        if "END-OF-REPORT" not in text:
            errs.append(f"step-P10 reading {name} is not the return in full (no END-OF-REPORT)")
        if "sealed folder" not in text:
            errs.append(f"step-P10 reading {name} does not say it was made from the sealed folder")
        if "no outside access" in text:
            errs.append(f"step-P10 reading {name} claims 'no outside access'; some readers read "
                        "official pages live, so the header must state the method truthfully")
        got = hashlib.sha256(raw).hexdigest()
        if got != spec["digest"]:
            errs.append(
                f"step-P10 reading {name} digest changed: {got} != recorded {spec['digest']} "
                "(the saved reading must stay byte-for-byte unchanged)"
            )
    return errs


# --------------------------------------------------------------------------
# S2: a value only where both readings of the option family agree
# --------------------------------------------------------------------------
def _pair_for(rid: str):
    for prefix, pair in READING_PAIRS:
        if rid.startswith(prefix):
            return pair
    return None


def reading_pair_errors(case_id: str, data: dict) -> list[str]:
    """Every option row names BOTH its readings in the source reference (a value needs
    both readings of that option family to agree); a shared row names the comparer -25.
    A row that names only one reading of its pair, or the wrong pair, is refused (S2)."""
    if case_id != STEP_P10_CASE_ID:
        return []
    errs: list[str] = []
    for row in data.get("rows", []):
        rid = row.get("row_id", "?")
        ref = str(row.get("source_reference", ""))
        pair = _pair_for(rid)
        if pair is None:
            if COMPARER_STEM not in ref:
                errs.append(f"{case_id}/{rid}: a shared row must name the comparer {COMPARER_STEM} "
                            "in its source reference")
        else:
            missing = [stem for stem in pair if stem not in ref]
            if missing:
                errs.append(f"{case_id}/{rid}: an option row must name BOTH its readings {pair} "
                            f"(a value needs both readings to agree); missing {missing}")
    return errs


# --------------------------------------------------------------------------
# S4: the rows the two readings do not jointly settle stay not known
# --------------------------------------------------------------------------
def must_stay_not_known_errors(case_id: str, data: dict) -> list[str]:
    """A step-P10 row the two readings do not jointly settle (they differ, one says not
    known, or the captured text does not fix it) must be "not known"; giving it a value
    is refused (S4)."""
    rows = MUST_STAY_NOT_KNOWN.get(case_id, set())
    errs: list[str] = []
    for row in data.get("rows", []):
        if row.get("row_id") in rows:
            kind = row.get("expected", {}).get("kind")
            if kind != "not_known":
                errs.append(
                    f"{case_id}/{row.get('row_id')}: the two readings do not jointly settle "
                    f"this, so it must be 'not known', not {kind!r}"
                )
    return errs


# --------------------------------------------------------------------------
# S6: every quantity on exactly one of the nine bases; never two bases combined
# --------------------------------------------------------------------------
def quantity_basis_errors(case_id: str, data: dict) -> list[str]:
    """Every quantity a row carries names exactly one of the nine measurement bases; a
    quantity with no basis, or with a basis outside the nine, is refused (S6)."""
    if case_id != STEP_P10_CASE_ID:
        return []
    errs: list[str] = []
    for row in data.get("rows", []):
        rid = row.get("row_id", "?")
        for quant in row.get("quantities", []):
            if not isinstance(quant, dict) or set(quant) != QUANTITY_KEYS:
                errs.append(f"{case_id}/{rid}: a quantity's keys differ from the fixed set "
                            f"{sorted(QUANTITY_KEYS)}")
                continue
            basis = quant.get("basis")
            if not isinstance(basis, str) or not basis.strip():
                errs.append(f"{case_id}/{rid}: quantity {quant.get('name')!r} carries no "
                            "measurement basis (name exactly one of the nine bases)")
                continue
            if basis not in QUANTITY_BASES:
                errs.append(f"{case_id}/{rid}: quantity {quant.get('name')!r} basis {basis!r} is "
                            f"not one of the nine bases {sorted(QUANTITY_BASES)}")
    return errs


def no_mixed_basis_errors(case_id: str, data: dict) -> list[str]:
    """The recorded lot area 10,075 (administrative_record) and the GIS outline area
    10,387.99 (gis) must never appear combined in one arithmetic step; every floor-area
    figure uses the recorded 10,075 (S6)."""
    if case_id != STEP_P10_CASE_ID:
        return []
    errs: list[str] = []
    for row in data.get("rows", []):
        rid = row.get("row_id", "?")
        for stp in row.get("arithmetic", []):
            vals = {str(op.get("value", "")) for op in stp.get("operands", [])}
            if _RECORDED_AREA in vals and _GIS_AREA in vals:
                errs.append(f"{case_id}/{rid}: an arithmetic step mixes the recorded area "
                            f"{_RECORDED_AREA} (administrative_record) and the GIS area "
                            f"{_GIS_AREA} (gis); the two bases are never combined in one figure")
    return errs


# --------------------------------------------------------------------------
# S5: eligibility / meaning caveats and forbidden present-tense wording
# --------------------------------------------------------------------------
def eligibility_errors(case_id: str, data: dict) -> list[str]:
    """The use-permission rows carry a does_not_establish caveat that the case decides no
    eligibility, and the owner-question rows carry a caveat that the case decides neither
    meaning of option 8 (N1) nor option 10 (N2); a row that drops its caveat is refused
    (S5)."""
    if case_id != STEP_P10_CASE_ID:
        return []
    errs: list[str] = []
    for row in data.get("rows", []):
        rid = row.get("row_id", "?")
        dne = str(row.get("does_not_establish", "")).lower()
        if rid in _ELIGIBILITY_ROW_IDS and _ELIGIBILITY_CAVEAT not in dne:
            errs.append(f"{case_id}/{rid}: a use-permission row must carry the eligibility caveat "
                        f"({_ELIGIBILITY_CAVEAT!r}) in does_not_establish")
        if rid in _MEANING_ROW_IDS and _MEANING_CAVEAT not in dne:
            errs.append(f"{case_id}/{rid}: an owner-question row must carry the caveat that the "
                        f"case {_MEANING_CAVEAT!r} in does_not_establish")
    return errs


def forbidden_wording_errors(case_id: str, data: dict) -> list[str]:
    """No present-tense "not captured" wording appears anywhere outside the change log;
    uncaptured sections are named in prose ("the readers did not have ...") (S5)."""
    if case_id != STEP_P10_CASE_ID:
        return []
    errs: list[str] = []

    def walk(node, where: str):
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "change_log":
                    continue
                walk(value, f"{where}.{key}")
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, f"{where}[{i}]")
        elif isinstance(node, str):
            low = node.lower()
            for phrase in _FORBIDDEN_WORDING:
                if phrase in low:
                    errs.append(f"{case_id}: forbidden present-tense wording {phrase!r} at {where}")

    walk(data, case_id)
    return errs


# --------------------------------------------------------------------------
# S8: no unconditional "no rear yard"; every rear-yard conclusion names its condition
# --------------------------------------------------------------------------
def _row_text(row: dict) -> str:
    exp = row.get("expected", {})
    return " ".join([
        str(exp.get("value", "")), str(exp.get("reason", "")),
        str(row.get("quantity", "")), str(row.get("why_applies", "")),
        str(row.get("does_not_establish", "")),
    ]).lower()


def rear_yard_errors(case_id: str, data: dict) -> list[str]:
    """Every rear-yard row names its condition and the zoning-lot scope, and records no
    unconditional "no rear yard"; the corner waiver names the
    within-100-feet-of-a-135-degree-or-less-corner condition (S8)."""
    if case_id != STEP_P10_CASE_ID:
        return []
    errs: list[str] = []
    for row in data.get("rows", []):
        rid = row.get("row_id", "?")
        if rid not in _REAR_YARD_ROWS:
            continue
        text = _row_text(row)
        if not any(t in text for t in _RY_CONDITION):
            errs.append(f"{case_id}/{rid}: a rear-yard conclusion must name its condition "
                        "(within 100 feet / the <=135-degree corner / not known)")
        if not any(t in text for t in _RY_SCOPE):
            errs.append(f"{case_id}/{rid}: a rear-yard conclusion must name the zoning-lot scope "
                        "(Z1 / the zoning lot / lot 70 alone)")
        if "no rear yard" in text and not any(t in text for t in _RY_CONDITION):
            errs.append(f"{case_id}/{rid}: no unconditional 'no rear yard' is recorded; it must "
                        "name its condition")
        if rid == _CORNER_WAIVER_ROW:
            if "within 100 feet" not in text and "within 100 ft" not in text:
                errs.append(f"{case_id}/{rid}: the corner waiver must name the within-100-feet "
                            "condition")
            if "135 degrees" not in text:
                errs.append(f"{case_id}/{rid}: the corner waiver must name the 135-degrees-or-less "
                            "corner condition")
    return errs


# --------------------------------------------------------------------------
# one entry the checker calls (keeps check.py thin: Risk 1)
# --------------------------------------------------------------------------
def case_errors(case_id: str, data: dict) -> list[str]:
    """All the step-P10 per-row and per-case guards behind one entry, so the checker
    grows the fewest lines and stays under its 600-line cap."""
    if case_id != STEP_P10_CASE_ID:
        return []
    errs: list[str] = []
    errs += reading_pair_errors(case_id, data)
    errs += must_stay_not_known_errors(case_id, data)
    errs += quantity_basis_errors(case_id, data)
    errs += no_mixed_basis_errors(case_id, data)
    errs += eligibility_errors(case_id, data)
    errs += forbidden_wording_errors(case_id, data)
    errs += rear_yard_errors(case_id, data)
    return errs
