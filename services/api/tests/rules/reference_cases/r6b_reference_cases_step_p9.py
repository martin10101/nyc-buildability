#!/usr/bin/env python3
"""Step-P9 reference-case constants and guards (M5-T184).

Pure stdlib (no import from the rule engine, the scenario engine or any program
output; it imports nothing from ``app``). It holds the data and the extra rules the
step-P9 case needs, so the checker next to it does not grow past its focus. The
step-P9 case (``benchmark-options-2-3-6-7``) is the agreed worked values of options
2 (qualifying affordable housing), 3 (qualifying senior housing), 6 (residences with
a community facility) and 7 (a community facility alone) for the benchmark lot
(215-16 Northern Boulevard, lot 70 of block 7334; R6B with a C2-2 overlay; corner),
read independently twice per option and confirmed by an independent comparer.

Unlike the step-P1 through step-P8 cases, this one case rests on THREE reading pairs
plus a comparer, so it is deliberately NOT registered in the checker's generic
``CASE_READINGS`` (which forces one reading tuple on every row of a case). Instead
the per-row reading pair is enforced here by row-id prefix: an ``opt2-*`` row names
readings -19 and -20, an ``opt3-*`` row names -21 and -22, an ``opt6-*``/``opt7-*``/
``opt67-*`` row names -23 and -24, and a shared row names the comparer -25.

The checker wires in exactly two entries so it grows ~2 lines and stays under its
600-line cap (Risk 1):

* :func:`reading_digest_errors` - the seven reading files -19..-25 are each present
  unchanged (digest pinned), carry their distinctive marker and the literal phrase
  "sealed folder", end with END-OF-REPORT, and do NOT claim "no outside access"
  (some readers read official pages live, so the headers state the method truthfully)
  (S1).
* :func:`case_errors` - all the per-row and per-case guards for the step-P9 case,
  behind one entry: the per-row reading pair (S2), the rows that must stay not known
  (S4), every quantity on exactly one of the nine bases and never two bases combined
  (S6), the eligibility caveat on the qualifying-housing and community-facility-use
  rows (S5), the forbidden present-tense "not captured" wording (S5) and the
  rear-yard conditions (S8).

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

STEP_P9_CASE_ID = "benchmark-options-2-3-6-7"

# The seven reading files (six option readings -19..-24 plus the comparer -25), each
# saved unchanged below a short truthful header. The digest pins the whole saved file
# (header + the reader's verbatim return) so any later edit is caught (S1).
STEP_P9_READINGS = {
    "return-independent-hand-calculation-19.md": {
        "marker": "M5-T184 PROVENANCE -19 (OPTION 2, READING A)",
        "digest": "ece8920e1ffd0ddc62a53234f5ff63f4648fbc0fec32c0d6650d915365a8f854",
    },
    "return-independent-hand-calculation-20.md": {
        "marker": "M5-T184 PROVENANCE -20 (OPTION 2, READING B)",
        "digest": "9bf98fd001d09881ec4882b93ca272eb9b05a22fa35b9b20256aa66a385b9518",
    },
    "return-independent-hand-calculation-21.md": {
        "marker": "M5-T184 PROVENANCE -21 (OPTION 3, READING A)",
        "digest": "6b5f81d2c48c73695c0e42a3d5711f4630ac469623f545bd30b2ce569d250de9",
    },
    "return-independent-hand-calculation-22.md": {
        "marker": "M5-T184 PROVENANCE -22 (OPTION 3, READING B)",
        "digest": "b72ad7969ac5482e254ce43fa47131d6ebb9bf84cd5a92d6bfc52456b1799797",
    },
    "return-independent-hand-calculation-23.md": {
        "marker": "M5-T184 PROVENANCE -23 (OPTIONS 6-7, READING A)",
        "digest": "498f2a554a620d6334fa2a20f72f8e387fbe3f1b86bcb3b2fad254073a4a4b92",
    },
    "return-independent-hand-calculation-24.md": {
        "marker": "M5-T184 PROVENANCE -24 (OPTIONS 6-7, READING B)",
        "digest": "728266a29c9e51a49efd1c7ab7ccf58a3a01221232b7b2c3c8083c084477ec77",
    },
    "return-independent-hand-calculation-25.md": {
        "marker": "M5-T184 PROVENANCE -25 (INDEPENDENT COMPARER)",
        "digest": "414a5068800a8e2ca500fca5556b1c429230efd388fbc95d548be789d9419bd7",
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
# readings of that option agree, so every option row must name both of its readings;
# a shared row names the comparer (S2).
_PAIR_19_20 = ("return-independent-hand-calculation-19", "return-independent-hand-calculation-20")
_PAIR_21_22 = ("return-independent-hand-calculation-21", "return-independent-hand-calculation-22")
_PAIR_23_24 = ("return-independent-hand-calculation-23", "return-independent-hand-calculation-24")
COMPARER_STEM = "return-independent-hand-calculation-25"
READING_PAIRS = (
    ("opt2-", _PAIR_19_20),
    ("opt3-", _PAIR_21_22),
    ("opt67-", _PAIR_23_24),
    ("opt6-", _PAIR_23_24),
    ("opt7-", _PAIR_23_24),
)

# Rows the two readings do not jointly settle to one value on one basis, or where the
# captured text does not fix the point. They must carry no value (S4).
MUST_STAY_NOT_KNOWN = {
    STEP_P9_CASE_ID: {
        "opt2-lot-coverage",
        "opt2-affordable-share",
        "opt2-mih-area-membership",
        "opt3-max-dwelling-units",
        "opt6-dwelling-units",
        "opt67-cf-max-footprint",
        "opt67-which-uses-not-known",
        "opt67-street-wall",
        "real-lot-missing-facts",
    },
}

# The whole-lot community-facility footprint is not a single figure on this lot. The
# lot spans a corner portion (within 100 feet of each street line) and a strip beyond
# the 100-foot corner reach, so the 24-11 corner rate 0.80 and interior/through rate
# 0.60 are each a PORTION rate, not a whole-lot rate; the portion areas are a missing
# fact about the property (see the settled residential reading real-lot.json, which
# records the 23-362 coverage by portion). So the opt67-cf-max-footprint row stays NOT
# KNOWN, and a settled (value) footprint that records 6,045 or 8,060 sq ft as a
# whole-lot maximum - or that multiplies the whole recorded lot area by a portion
# coverage rate and records the product as a footprint - is refused (S4/S6).
_FOOTPRINT_ROW_ID = "opt67-cf-max-footprint"
_PORTION_FOOTPRINT_PRODUCTS = {"8060", "6045"}
_PORTION_COVERAGE_RATES = {"0.80", "0.8", "0.60", "0.6"}

# The qualifying-housing rows (opt2-*/opt3-*) and the community-facility use-permission
# rows must carry a does_not_establish caveat that the case decides no eligibility (S5).
_ELIGIBILITY_PREFIXES = ("opt2-", "opt3-")
_ELIGIBILITY_ROW_IDS = {"opt67-use-group-iii", "opt67-which-uses-not-known"}
_ELIGIBILITY_CAVEAT = "decides no eligibility"

# No present-tense "not captured" wording anywhere outside the change log (S5): the
# proven convention names uncaptured sections in prose ("the readers did not have ...").
_FORBIDDEN_WORDING = (
    "does not hold", "is not captured", "are not captured", "not captured", "uncaptured",
)

# The rear-yard rows: each must name its condition and the zoning-lot scope, and the
# corner waiver must name the within-100-feet-of-a-135-degree-corner condition (S8).
_REAR_YARD_ROWS = {"opt67-corner-rear-yard-waiver", "opt67-cf-rear-yard", "opt2-rear-yard"}
_CORNER_WAIVER_ROW = "opt67-corner-rear-yard-waiver"
_RY_CONDITION = ("within 100 feet", "within 100 ft", "135 degrees", "not known")
_RY_SCOPE = ("zoning lot", "per zoning lot", "z1", "lot 70 alone")

# The recorded area (administrative_record) and the GIS area (gis) must never be
# combined in one arithmetic step (S6); every figure uses the recorded 10,075.
_RECORDED_AREA = "10075"
_GIS_AREA = "10387.99"


# --------------------------------------------------------------------------
# S1: the seven reading files are present unchanged
# --------------------------------------------------------------------------
def reading_digest_errors() -> list[str]:
    """The seven step-P9 reading files are present unchanged: each carries its marker
    and END-OF-REPORT, says it was made from the "sealed folder" (here the pinned
    read-only captures in the detached checkout), does NOT claim "no outside access"
    (some readers read official pages live), and hashes to the recorded digest, so any
    later edit to a saved reading is caught (S1)."""
    errs: list[str] = []
    for name, spec in STEP_P9_READINGS.items():
        path = lib.PROVENANCE_DIR / name
        if not path.is_file():
            errs.append(f"step-P9 reading missing: {name}")
            continue
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        if spec["marker"] not in text:
            errs.append(f"step-P9 reading {name} does not carry its distinctive marker")
        if "END-OF-REPORT" not in text:
            errs.append(f"step-P9 reading {name} is not the return in full (no END-OF-REPORT)")
        if "sealed folder" not in text:
            errs.append(f"step-P9 reading {name} does not say it was made from the sealed folder")
        if "no outside access" in text:
            errs.append(f"step-P9 reading {name} claims 'no outside access'; some readers read "
                        "official pages live, so the header must state the method truthfully")
        got = hashlib.sha256(raw).hexdigest()
        if got != spec["digest"]:
            errs.append(
                f"step-P9 reading {name} digest changed: {got} != recorded {spec['digest']} "
                "(the saved reading must stay byte-for-byte unchanged)"
            )
    return errs


# --------------------------------------------------------------------------
# S2: a value only where both readings of the option agree
# --------------------------------------------------------------------------
def _pair_for(rid: str):
    for prefix, pair in READING_PAIRS:
        if rid.startswith(prefix):
            return pair
    return None


def reading_pair_errors(case_id: str, data: dict) -> list[str]:
    """Every option row names BOTH its readings in the source reference (a value needs
    both readings of that option to agree); a shared row names the comparer -25. A row
    that names only one reading of its pair, or the wrong pair, is refused (S2)."""
    if case_id != STEP_P9_CASE_ID:
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
    """A step-P9 row the two readings do not jointly settle (they differ, one says not
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
    if case_id != STEP_P9_CASE_ID:
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
    if case_id != STEP_P9_CASE_ID:
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
# S5: eligibility caveat and forbidden present-tense wording
# --------------------------------------------------------------------------
def eligibility_errors(case_id: str, data: dict) -> list[str]:
    """The qualifying-housing rows (opt2-*/opt3-*) and the community-facility
    use-permission rows carry a does_not_establish caveat that the case decides no
    eligibility; a row that drops it is refused (S5)."""
    if case_id != STEP_P9_CASE_ID:
        return []
    errs: list[str] = []
    for row in data.get("rows", []):
        rid = row.get("row_id", "?")
        if rid.startswith(_ELIGIBILITY_PREFIXES) or rid in _ELIGIBILITY_ROW_IDS:
            dne = str(row.get("does_not_establish", "")).lower()
            if _ELIGIBILITY_CAVEAT not in dne:
                errs.append(f"{case_id}/{rid}: a qualifying-housing or community-facility "
                            f"use-permission row must carry the eligibility caveat "
                            f"({_ELIGIBILITY_CAVEAT!r}) in does_not_establish")
    return errs


def forbidden_wording_errors(case_id: str, data: dict) -> list[str]:
    """No present-tense "not captured" wording appears anywhere outside the change log;
    uncaptured sections are named in prose ("the readers did not have ...") (S5)."""
    if case_id != STEP_P9_CASE_ID:
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
    if case_id != STEP_P9_CASE_ID:
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
# S4/S6: the whole-lot community-facility footprint is not a portion-rate figure
# --------------------------------------------------------------------------
def portion_footprint_errors(case_id: str, data: dict) -> list[str]:
    """The opt67-cf-max-footprint row stays NOT KNOWN: the whole-lot community-facility
    footprint cannot be worked from one 24-11 rate on the whole recorded lot area,
    because the lot spans a corner portion and a strip beyond the 100-foot corner reach
    (the portion areas are a missing fact). A settled (value) footprint that records
    6,045 or 8,060 sq ft as a whole-lot maximum, or an arithmetic step that multiplies
    the whole recorded lot area by a portion coverage rate (0.80 corner / 0.60 interior)
    and records the product as this row's footprint, is refused."""
    if case_id != STEP_P9_CASE_ID:
        return []
    errs: list[str] = []
    for row in data.get("rows", []):
        if row.get("row_id") != _FOOTPRINT_ROW_ID:
            continue
        if row.get("expected", {}).get("kind") != "not_known":
            errs.append(f"{case_id}/{_FOOTPRINT_ROW_ID}: the whole-lot community-facility "
                        "footprint is not settled (the corner-portion area and the area beyond "
                        "the 100-foot corner reach are a missing fact), so it must be 'not "
                        f"known', not {row.get('expected', {}).get('kind')!r}")
        for quant in row.get("quantities", []):
            val = str(quant.get("value", "")).replace(",", "").strip()
            if val in _PORTION_FOOTPRINT_PRODUCTS:
                errs.append(f"{case_id}/{_FOOTPRINT_ROW_ID}: quantity {quant.get('name')!r} "
                            f"records {quant.get('value')!r} sq ft as a settled footprint; it "
                            "multiplies the whole recorded lot area by one portion's coverage "
                            "rate, so it is not a whole-lot maximum footprint")
        for stp in row.get("arithmetic", []):
            vals = {str(op.get("value", "")).strip() for op in stp.get("operands", [])}
            if _RECORDED_AREA in vals and (vals & _PORTION_COVERAGE_RATES):
                errs.append(f"{case_id}/{_FOOTPRINT_ROW_ID}: an arithmetic step multiplies the "
                            f"whole recorded lot area {_RECORDED_AREA} by a portion coverage rate "
                            "(0.80 corner / 0.60 interior) and records it as a footprint; the "
                            "whole-lot maximum footprint is not known (the portion areas are a "
                            "missing fact about the property)")
    return errs


# --------------------------------------------------------------------------
# one entry the checker calls (keeps check.py thin: Risk 1)
# --------------------------------------------------------------------------
def case_errors(case_id: str, data: dict) -> list[str]:
    """All the step-P9 per-row and per-case guards behind one entry, so the checker
    grows the fewest lines and stays under its 600-line cap."""
    if case_id != STEP_P9_CASE_ID:
        return []
    errs: list[str] = []
    errs += reading_pair_errors(case_id, data)
    errs += must_stay_not_known_errors(case_id, data)
    errs += portion_footprint_errors(case_id, data)
    errs += quantity_basis_errors(case_id, data)
    errs += no_mixed_basis_errors(case_id, data)
    errs += eligibility_errors(case_id, data)
    errs += forbidden_wording_errors(case_id, data)
    errs += rear_yard_errors(case_id, data)
    return errs
