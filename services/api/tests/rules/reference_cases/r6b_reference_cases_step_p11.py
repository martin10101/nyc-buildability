#!/usr/bin/env python3
"""Step-P11 reference-case constants and guards (M5-T186).

Pure stdlib (no import from the rule engine, the scenario engine or any program
output; it imports nothing from ``app``). It holds the data and the extra rules the
step-P11 case needs, so the checker next to it does not grow past its focus. The
step-P11 case (``benchmark-options-4-11``) is the agreed worked values of option 4
(more, smaller apartments) and option 11 (all programs combined) for the benchmark
lot (215-16 Northern Boulevard, lot 70 of block 7334; R6B with a C2-2 overlay;
corner), read independently twice per option plus an independent comparer per option.
With these two the eleven-option set is complete across the reference cases.

Unlike the step-P9 and step-P10 cases (three reading pairs plus one shared comparer),
this one case rests on TWO reading pairs AND TWO comparers: option 4 = readings -32 and
-33 with comparer -34; option 11 = readings -35 and -36 with comparer -37. The generic
``CASE_READINGS`` in the checker forces one reading tuple on every row of a case, so
this case is deliberately NOT registered there. Instead the per-row reading pair and
comparer are enforced here by row-id prefix: an ``opt4-*`` row names -32, -33 and the
option-4 comparer -34; an ``opt11-*`` row names -35, -36 and the option-11 comparer
-37; a shared row (what the readers did not have, the real-lot missing facts, the
options out of scope) names both comparers -34 and -37.

The checker wires in exactly one case entry (its per-row/per-case guards) and one
reading-digest entry (the six NEW reading files -32..-37), both through the shared
``r6b_reference_cases_cases`` aggregator so the checker stays under its 600-line cap
(Risk 1). Nothing here imports the checker, so there is no cycle.
"""
from __future__ import annotations

import hashlib
import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import r6b_reference_cases_lib as lib  # noqa: E402

STEP_P11_CASE_ID = "benchmark-options-4-11"

# The six NEW reading files (option 4 = -32/-33 + comparer -34; option 11 = -35/-36 +
# comparer -37), each saved unchanged below a short truthful header. The digest pins the
# whole saved file (header + the reader's verbatim return) so any later edit is caught
# (S1). The two comparers -34 and -37 are new here (not reused from M5-T184/M5-T185).
STEP_P11_READINGS = {
    "return-independent-hand-calculation-32.md": {
        "marker": "M5-T186 PROVENANCE -32 (OPTION 4, READING A)",
        "digest": "87672565a1c78bcc49fd36c53174a1155584232cd336dabd5b3ec2cca6803835",
    },
    "return-independent-hand-calculation-33.md": {
        "marker": "M5-T186 PROVENANCE -33 (OPTION 4, READING B)",
        "digest": "dfe4d9760bce6061feae8ecb714830f4a7377492b0c459ae26bcb83c18407400",
    },
    "return-independent-hand-calculation-34.md": {
        "marker": "M5-T186 PROVENANCE -34 (OPTION 4, INDEPENDENT COMPARER)",
        "digest": "a9d3f6b5bec18e2ea389ee1dcb424097a2fea5ec5119155028a01216af3cdfec",
    },
    "return-independent-hand-calculation-35.md": {
        "marker": "M5-T186 PROVENANCE -35 (OPTION 11, READING A)",
        "digest": "b7dfde7abdce51c8fa4883fc333928f1d551bd70ac2eb55cd07b64d251dc5bd7",
    },
    "return-independent-hand-calculation-36.md": {
        "marker": "M5-T186 PROVENANCE -36 (OPTION 11, READING B)",
        "digest": "c2b08bbbbe66491010d4beb61bb20db51020b928aad18bd82abb5e53b772b3e5",
    },
    "return-independent-hand-calculation-37.md": {
        "marker": "M5-T186 PROVENANCE -37 (OPTION 11, INDEPENDENT COMPARER)",
        "digest": "fee1eb07d8acd563be68ed093c8663d584305e8a57f7c20616c2143acfe0ff0e",
    },
}

# The nine measurement bases. Mirrors tools/research_record_check.py QUANTITY_BASES
# (the test asserts this constant equals that authoritative set, so it never drifts).
QUANTITY_BASES = frozenset({
    "law", "deed", "survey", "printed_tax_map", "approved_plan",
    "filing_attribute", "administrative_record", "gis", "derived",
})
QUANTITY_KEYS = {"name", "value", "unit", "basis"}

# The per-row reading pair and comparer, by row-id prefix. A value is recorded only
# where both readings of that option agree, so every option row names both of its
# readings AND the option's comparer; a shared row names both comparers (S2).
OPT4_PAIR = ("return-independent-hand-calculation-32", "return-independent-hand-calculation-33")
OPT4_COMPARER = "return-independent-hand-calculation-34"
OPT11_PAIR = ("return-independent-hand-calculation-35", "return-independent-hand-calculation-36")
OPT11_COMPARER = "return-independent-hand-calculation-37"
# (prefix, pair, comparer) - ordered so the longer prefix is not shadowed.
READING_GROUPS = (
    ("opt4-", OPT4_PAIR, OPT4_COMPARER),
    ("opt11-", OPT11_PAIR, OPT11_COMPARER),
)

# Rows the two readings do not jointly settle to one value on one basis, or where the
# captured text does not fix the point. They must carry no value (S4).
MUST_STAY_NOT_KNOWN = {
    STEP_P11_CASE_ID: {
        "opt4-nofactor-senior",
        "opt4-nofactor-conversions",
        "opt4-min-unit-size",
        "opt4-affordable-2.40-not-opt4",
        "opt11-street-wall-line",
        "opt11-affordable-senior-together",
        "opt11-shared-housing",
        "opt11-split-lot-meaning",
        "opt11-overlay-extent",
        "opt11-uap-text",
        "opt11-35-31-full-carveout-sweep",
        "opt11-senior-nofactor-cap",
        "opt11-rear-yard-beyond-100ft",
        "real-lot-missing-facts",
    },
}

# The use-permission / qualifying-eligibility rows must carry a does_not_establish
# caveat that the case decides no eligibility (S5).
_ELIGIBILITY_ROW_IDS = {
    "opt11-combine-shops",
    "opt11-combination-ceiling-qualifying",
    "opt11-du-qualifying-affordable",
    "opt11-du-qualifying-senior",
}
_ELIGIBILITY_CAVEAT = "decides no eligibility"

# The owner-question rows must carry a does_not_establish caveat that the case decides
# neither owner question N1 (what option 8 means) nor N2 (shared housing) (S5).
_MEANING_ROW_IDS = {"opt11-split-lot-meaning", "opt11-shared-housing"}
_MEANING_CAVEAT = "decides neither owner question"

# No present-tense "not captured" wording anywhere outside the change log (S5): the
# proven convention names sections the readers did not have in prose ("not among the
# captures").
_FORBIDDEN_WORDING = (
    "does not hold", "is not captured", "are not captured", "not captured", "uncaptured",
)

# The street-wall row (RISK 4): the two readings do not jointly settle the final
# street-wall line, and the comparer's 8-foot correction is an adjudicator's note, never
# a recorded value. The row must stay not known and carry no measured quantity (S4).
_STREET_WALL_ROW = "opt11-street-wall-line"

# The recorded area (administrative_record) and the GIS area (gis) must never be
# combined in one arithmetic step (S6); every figure uses the recorded 10,075.
_RECORDED_AREA = "10075"
_GIS_AREA = "10387.99"


# --------------------------------------------------------------------------
# S1: the six new reading files are present unchanged
# --------------------------------------------------------------------------
def reading_digest_errors() -> list[str]:
    """The six new step-P11 reading files (option 4 -32/-33/-34, option 11 -35/-36/-37)
    are present unchanged: each carries its marker and END-OF-REPORT, says it was made
    from the "sealed folder" (here the pinned read-only captures and settled cases), does
    NOT claim "no outside access", and hashes to the recorded digest, so any later edit to
    a saved reading is caught (S1)."""
    errs: list[str] = []
    for name, spec in STEP_P11_READINGS.items():
        path = lib.PROVENANCE_DIR / name
        if not path.is_file():
            errs.append(f"step-P11 reading missing: {name}")
            continue
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        if spec["marker"] not in text:
            errs.append(f"step-P11 reading {name} does not carry its distinctive marker")
        if "END-OF-REPORT" not in text:
            errs.append(f"step-P11 reading {name} is not the return in full (no END-OF-REPORT)")
        if "sealed folder" not in text:
            errs.append(f"step-P11 reading {name} does not say it was made from the sealed folder")
        if "no outside access" in text:
            errs.append(f"step-P11 reading {name} claims 'no outside access'; the header must "
                        "state the method truthfully")
        got = hashlib.sha256(raw).hexdigest()
        if got != spec["digest"]:
            errs.append(
                f"step-P11 reading {name} digest changed: {got} != recorded {spec['digest']} "
                "(the saved reading must stay byte-for-byte unchanged)"
            )
    return errs


# --------------------------------------------------------------------------
# S2: a value only where both readings of the option agree (and the comparer confirms)
# --------------------------------------------------------------------------
def _group_for(rid: str):
    for prefix, pair, comparer in READING_GROUPS:
        if rid.startswith(prefix):
            return pair, comparer
    return None


def reading_pair_errors(case_id: str, data: dict) -> list[str]:
    """Every option row names BOTH its readings AND its comparer in the source reference
    (a value needs both readings of that option to agree, confirmed by that option's
    comparer); a shared row names both comparers -34 and -37. A row that names only one
    reading of its pair, the wrong pair, or the wrong comparer is refused (S2)."""
    if case_id != STEP_P11_CASE_ID:
        return []
    errs: list[str] = []
    for row in data.get("rows", []):
        rid = row.get("row_id", "?")
        ref = str(row.get("source_reference", ""))
        group = _group_for(rid)
        if group is None:  # a shared row
            missing = [c for c in (OPT4_COMPARER, OPT11_COMPARER) if c not in ref]
            if missing:
                errs.append(f"{case_id}/{rid}: a shared row must name both comparers "
                            f"{OPT4_COMPARER} and {OPT11_COMPARER}; missing {missing}")
            continue
        pair, comparer = group
        missing = [stem for stem in pair if stem not in ref]
        if missing:
            errs.append(f"{case_id}/{rid}: an option row must name BOTH its readings {pair} "
                        f"(a value needs both readings to agree); missing {missing}")
        if comparer not in ref:
            errs.append(f"{case_id}/{rid}: an option row must name its comparer {comparer} "
                        "in the source reference")
    return errs


# --------------------------------------------------------------------------
# S4: the rows the two readings do not jointly settle stay not known
# --------------------------------------------------------------------------
def must_stay_not_known_errors(case_id: str, data: dict) -> list[str]:
    """A step-P11 row the two readings do not jointly settle (they differ, one says not
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


def street_wall_not_recorded_errors(case_id: str, data: dict) -> list[str]:
    """RISK 4: the final street-wall line is not jointly settled (one reading was numeric
    and partly wrong, the other gave no number), and the comparer's 8-foot correction is an
    adjudicator's note, never a recorded value. The street-wall row must be not known and
    carry no measured quantity, so the 8-foot figure is never recorded (S4)."""
    if case_id != STEP_P11_CASE_ID:
        return []
    errs: list[str] = []
    for row in data.get("rows", []):
        if row.get("row_id") != _STREET_WALL_ROW:
            continue
        if row.get("expected", {}).get("kind") != "not_known":
            errs.append(f"{case_id}/{_STREET_WALL_ROW}: the final street-wall line is not jointly "
                        "settled, so the row must be 'not known'")
        if row.get("quantities"):
            errs.append(f"{case_id}/{_STREET_WALL_ROW}: the street-wall row records no measured "
                        "quantity; the comparer's 8-foot correction is an adjudicator's note, "
                        "not a recorded value")
    return errs


# --------------------------------------------------------------------------
# S6: every quantity on exactly one of the nine bases; never two bases combined
# --------------------------------------------------------------------------
def quantity_basis_errors(case_id: str, data: dict) -> list[str]:
    """Every quantity a row carries names exactly one of the nine measurement bases; a
    quantity with no basis, or with a basis outside the nine, is refused (S6)."""
    if case_id != STEP_P11_CASE_ID:
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
    if case_id != STEP_P11_CASE_ID:
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
# S5: eligibility / owner-question caveats and forbidden present-tense wording
# --------------------------------------------------------------------------
def eligibility_errors(case_id: str, data: dict) -> list[str]:
    """The use-permission / qualifying-eligibility rows carry a does_not_establish caveat
    that the case decides no eligibility, and the owner-question rows carry a caveat that
    the case decides neither owner question N1 nor N2; a row that drops its caveat is
    refused (S5)."""
    if case_id != STEP_P11_CASE_ID:
        return []
    errs: list[str] = []
    for row in data.get("rows", []):
        rid = row.get("row_id", "?")
        dne = str(row.get("does_not_establish", "")).lower()
        if rid in _ELIGIBILITY_ROW_IDS and _ELIGIBILITY_CAVEAT not in dne:
            errs.append(f"{case_id}/{rid}: a use-permission / eligibility row must carry the "
                        f"eligibility caveat ({_ELIGIBILITY_CAVEAT!r}) in does_not_establish")
        if rid in _MEANING_ROW_IDS and _MEANING_CAVEAT not in dne:
            errs.append(f"{case_id}/{rid}: an owner-question row must carry the caveat that the "
                        f"case {_MEANING_CAVEAT!r} in does_not_establish")
    return errs


def forbidden_wording_errors(case_id: str, data: dict) -> list[str]:
    """No present-tense "not captured" wording appears anywhere outside the change log;
    sections the readers did not have are named in prose ("not among the captures") (S5)."""
    if case_id != STEP_P11_CASE_ID:
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
# one entry the checker calls (keeps check.py thin: Risk 1)
# --------------------------------------------------------------------------
def case_errors(case_id: str, data: dict) -> list[str]:
    """All the step-P11 per-row and per-case guards behind one entry, so the checker
    grows the fewest lines and stays under its 600-line cap."""
    if case_id != STEP_P11_CASE_ID:
        return []
    errs: list[str] = []
    errs += reading_pair_errors(case_id, data)
    errs += must_stay_not_known_errors(case_id, data)
    errs += street_wall_not_recorded_errors(case_id, data)
    errs += quantity_basis_errors(case_id, data)
    errs += no_mixed_basis_errors(case_id, data)
    errs += eligibility_errors(case_id, data)
    errs += forbidden_wording_errors(case_id, data)
    return errs
