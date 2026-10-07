#!/usr/bin/env python3
"""Deterministic checker for the R6B reference cases (M4-T024).

Pure stdlib. No rule math, no network, no AI call, and no import from the rule
engine, the scenario engine or any program output. It reads the authored case
data files, the captured law snapshots and the hand-written README, and returns
a list of plain-text problems (empty == clean). It covers:

* S1  - every row of the work order's tables A, B, C and D is present under its id.
* S2  - each row carries the facts with their source, the quoted law, why the
  rule applies, the arithmetic and the expected value (enough to follow by hand).
* S3  - no field, column or sentence carries a program result; the words
  'program today', 'first screen' and the like never appear in a case file.
* S5  - every arithmetic step recomputes to its recorded result (delegated to
  :mod:`r6b_reference_cases_lib`).
* S6  - a captured citation names its snapshot id, file and content digest, the
  digest matches the live capture, and the quoted words are in the capture; a
  not-captured section gives the official page and the date it was read.
* S7  - a 'not known' row carries no number and a reason; a numeric row has
  arithmetic or a quoted basis.
* S8  - the README lists the cases, the change rule, what a case is worth and
  the not-captured sections.

The small per-row checkers are kept as separate functions so the test can call
them on mutated in-memory data for the negative cases (a changed operand, a
changed digest).
"""
from __future__ import annotations

import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import hashlib  # noqa: E402
import json  # noqa: E402

import r6b_reference_cases_lib as lib  # noqa: E402
import r6b_reference_cases_step_p3 as step_p3  # noqa: E402

# A field name (key) that would smuggle a program result into a case file.
FORBIDDEN_KEY_SUBSTRINGS = ("program", "actual", "first_screen", "firstscreen")
# A sentence (string value) that would quote a program run.
FORBIDDEN_VALUE_PHRASES = (
    "program today", "first screen", "the program gives", "program's answer",
    "program result", "as the program", "what the program",
)
# The sections the README's "what the readers did not have" lists name - the
# step-P1 (M4-T025) and step-P2 (M4-T026/M4-T028) readers did not have these when
# they made their readings (on 2026-10-06 and 2026-10-07). Several (ZR 23-343,
# 23-434, 23-435, 23-436, 23-41, 34-21) have since been captured by task M4-T029
# and read independently in step P3 (M4-T030, cases/step-p3-worked.json); the step-P3
# readers still did not have 34-22 and 34-23. The README still names each item so a
# reader can trace which readers had which text and when.
NOT_CAPTURED_SECTIONS = (
    "23-343", "23-434", "23-435", "23-436", "23-41",
    "34-21", "34-22", "34-23", "35-64", "35-71", "36-64",
)

# The cases whose rows rest on two independent readings (step-P1 and step-P2),
# and the two reading files whose agreement a value needs (S2): a value may be
# recorded only where both readings agree on the same basis.
STEP_P1_CASE_ID = "step-p1-worked"
OVERLAY_CASE_ID = "overlay-reading"
CASE_READINGS = {
    STEP_P1_CASE_ID: (
        "return-independent-hand-calculation-3", "return-independent-hand-calculation-4",
    ),
    OVERLAY_CASE_ID: (
        "return-independent-hand-calculation-5", "return-independent-hand-calculation-6",
    ),
    step_p3.STEP_P3_CASE_ID: step_p3.STEP_P3_READING_STEMS,
}
# The human label for each such case, used in the "name both readings" message.
_READINGS_LABEL = {
    STEP_P1_CASE_ID: "step-P1", OVERLAY_CASE_ID: "overlay",
    step_p3.STEP_P3_CASE_ID: "step-P3",
}
# Per case, the rows whose two readings disagree (or where one says not known),
# which must therefore stay "not known".
READINGS_DIFFER = {
    STEP_P1_CASE_ID: {"interior-40x100-rear-yard"},
    OVERLAY_CASE_ID: {"section-35-633"},
}


# --------------------------------------------------------------------------
# S3: nothing from a program run
# --------------------------------------------------------------------------
def program_result_errors(case_id: str, data) -> list[str]:
    """Scan a case (keys and string values) for anything that would carry a
    program result. A field named like 'program_today' or 'actual', or a
    sentence such as 'the program gives 29', is refused."""
    errs: list[str] = []

    def walk(node, where: str):
        if isinstance(node, dict):
            for key, value in node.items():
                low = str(key).lower()
                for bad in FORBIDDEN_KEY_SUBSTRINGS:
                    if bad in low:
                        errs.append(f"{case_id}: field name {key!r} at {where} looks like a "
                                    "program result (nothing in a case comes from a program run)")
                walk(value, f"{where}.{key}")
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, f"{where}[{i}]")
        elif isinstance(node, str):
            low = node.lower()
            for phrase in FORBIDDEN_VALUE_PHRASES:
                if phrase in low:
                    errs.append(f"{case_id}: text at {where} contains {phrase!r}; a case never "
                                "quotes a program run")

    walk(data, case_id)
    return errs


# --------------------------------------------------------------------------
# structure (S2): fixed, complete fields
# --------------------------------------------------------------------------
def structure_errors(case_id: str, data: dict) -> list[str]:
    errs: list[str] = []
    if set(data) != lib.CASE_KEYS:
        errs.append(f"{case_id}: case keys {sorted(set(data) ^ lib.CASE_KEYS)} differ from the "
                    "fixed set")
        return errs
    if data["case_id"] != case_id:
        errs.append(f"{case_id}: case_id field {data['case_id']!r} != file stem")
    for field in ("title", "summary", "what_it_is_worth", "prepared_by", "checked_by"):
        if not str(data[field]).strip():
            errs.append(f"{case_id}: {field} is empty")
    for name in ("facts", "sources", "what_it_does_not_establish", "change_log", "rows"):
        if not isinstance(data[name], list) or not data[name]:
            errs.append(f"{case_id}: {name} must be a non-empty list")
    for fact in data.get("facts", []):
        if set(fact) != lib.FACT_KEYS:
            errs.append(f"{case_id}: a fact's keys {sorted(fact)} != {sorted(lib.FACT_KEYS)}")
        elif not all(str(fact[k]).strip() for k in ("name", "source")):
            errs.append(f"{case_id}: a fact needs a name and a source: {fact.get('name')!r}")
    return errs


def change_log_errors(case_id: str, data: dict) -> list[str]:
    errs: list[str] = []
    log = data.get("change_log", [])
    for entry in log:
        if set(entry) != lib.CHANGE_LOG_KEYS:
            errs.append(f"{case_id}: a change-log entry's keys differ from the fixed set")
        elif not all(str(entry[k]).strip() for k in lib.CHANGE_LOG_KEYS):
            errs.append(f"{case_id}: a change-log entry has an empty field")
    if log and "creat" not in (log[0].get("summary", "").lower()):
        errs.append(f"{case_id}: the first change-log entry must record the case's creation")
    for prev, cur in zip(log, log[1:], strict=False):
        if cur["date"] < prev["date"]:
            errs.append(f"{case_id}: change-log dates are not in order ({cur['date']} < "
                        f"{prev['date']})")
    return errs


# --------------------------------------------------------------------------
# S1: every table row present under its id
# --------------------------------------------------------------------------
def coverage_errors(case_id: str, data: dict) -> list[str]:
    errs: list[str] = []
    row_ids = [r["row_id"] for r in data["rows"]]
    if len(row_ids) != len(set(row_ids)):
        errs.append(f"{case_id}: duplicate row ids")
    for base in lib.REQUIRED_BASE_IDS[case_id]:
        if not any(rid == base or rid.startswith(base + "-") for rid in row_ids):
            errs.append(f"{case_id}: the work order's row {base!r} is not present under its id")
    return errs


# --------------------------------------------------------------------------
# S6: law text tied to its capture
# --------------------------------------------------------------------------
def _strip_markup(text: str) -> str:
    return text.replace("#", "")


def citation_errors(case_id: str, row: dict) -> list[str]:
    errs: list[str] = []
    rid = row.get("row_id", "?")
    for cite in row.get("citations", []):
        if set(cite) != lib.CITATION_KEYS:
            errs.append(f"{case_id}/{rid}: a citation's keys differ from the fixed set")
            continue
        if cite["kind"] not in lib.CITATION_KINDS:
            errs.append(f"{case_id}/{rid}: citation kind {cite['kind']!r} invalid")
            continue
        if not str(cite["section"]).strip() or not str(cite["quote"]).strip():
            errs.append(f"{case_id}/{rid}: a citation needs a section and a quote")
            continue
        if cite["kind"] == "captured":
            errs += _captured_citation_errors(case_id, rid, cite)
        else:
            errs += _not_captured_citation_errors(case_id, rid, cite)
    return errs


def _captured_citation_errors(case_id: str, rid: str, cite: dict) -> list[str]:
    errs: list[str] = []
    snap_path = lib.REPO_ROOT / cite["snapshot_file"]
    if not str(cite["snapshot_id"]).strip() or not str(cite["snapshot_file"]).strip():
        errs.append(f"{case_id}/{rid}: a captured citation needs a snapshot id and file")
        return errs
    if not snap_path.is_file():
        errs.append(f"{case_id}/{rid}: capture file missing: {cite['snapshot_file']}")
        return errs
    snap = json.loads(snap_path.read_text())
    if snap["content_digest_sha256"] != cite["content_digest"]:
        errs.append(f"{case_id}/{rid}: law digest for {cite['section']} does not match the capture "
                    f"{cite['snapshot_id']} (case {cite['content_digest']} != capture "
                    f"{snap['content_digest_sha256']})")
    if snap["source"]["request_url"] != cite["official_url"]:
        errs.append(f"{case_id}/{rid}: official_url for {cite['section']} does not match the "
                    f"capture {cite['snapshot_id']}")
    quote = _strip_markup(cite["quote"])
    if quote not in _strip_markup(snap["verbatim_excerpt"]):
        errs.append(f"{case_id}/{rid}: the quoted words for {cite['section']} are not found in the "
                    f"capture {cite['snapshot_id']}")
    errs += _table_assertion_errors(case_id, rid, cite, snap)
    return errs


def _table_assertion_errors(case_id: str, rid: str, cite: dict, snap: dict) -> list[str]:
    errs: list[str] = []
    assertion = cite["table_assertion"]
    if not assertion:
        return errs
    table = snap.get("table")
    if not table:
        errs.append(f"{case_id}/{rid}: a table assertion cites {cite['snapshot_id']}, which has no "
                    "table")
        return errs
    district = assertion["district"]
    matches = [r for r in table["rows"] if district in r.get("districts", [])]
    if not matches:
        errs.append(f"{case_id}/{rid}: district {district!r} is not a row in {cite['snapshot_id']}")
        return errs
    row = matches[0]
    for field, want in assertion["fields"].items():
        if str(row.get(field)) != str(want):
            errs.append(f"{case_id}/{rid}: {cite['snapshot_id']} row {district} field {field} is "
                        f"{row.get(field)!r}, not {want!r}")
    return errs


def _not_captured_citation_errors(case_id: str, rid: str, cite: dict) -> list[str]:
    errs: list[str] = []
    if not str(cite["official_url"]).strip():
        errs.append(f"{case_id}/{rid}: a not-captured citation needs the official page url")
    if not str(cite["date_read"]).strip():
        errs.append(f"{case_id}/{rid}: a not-captured citation needs the date it was read")
    if not str(cite["status_note"]).strip():
        errs.append(f"{case_id}/{rid}: a not-captured citation needs a status note")
    for empty in ("snapshot_id", "snapshot_file", "content_digest"):
        if str(cite[empty]).strip():
            errs.append(f"{case_id}/{rid}: a not-captured citation must leave {empty} empty")
    return errs


# --------------------------------------------------------------------------
# S7: not known stays not known; a numeric row has a basis
# --------------------------------------------------------------------------
def expected_errors(case_id: str, row: dict) -> list[str]:
    errs: list[str] = []
    rid = row.get("row_id", "?")
    exp = row.get("expected", {})
    if set(exp) != lib.EXPECTED_KEYS:
        errs.append(f"{case_id}/{rid}: expected keys differ from the fixed set")
        return errs
    if exp["kind"] not in lib.EXPECTED_KINDS:
        errs.append(f"{case_id}/{rid}: expected kind {exp['kind']!r} invalid")
        return errs

    has_arithmetic = bool(row.get("arithmetic"))
    has_quoted_basis = any(str(c.get("quote", "")).strip() for c in row.get("citations", []))
    has_sourced_fact = any(str(f.get("source", "")).strip() for f in row.get("facts_used", []))

    if exp["kind"] == "not_known":
        if exp["value"] is not None:
            errs.append(f"{case_id}/{rid}: a 'not known' row carries a value {exp['value']!r}; it "
                        "must carry no number")
        if not str(exp["reason"]).strip():
            errs.append(f"{case_id}/{rid}: a 'not known' row needs a reason in plain words")
    else:  # value
        if exp["value"] is None:
            errs.append(f"{case_id}/{rid}: a value row must carry a value")
        if lib.is_numeric_value(exp["value"]) and not (has_arithmetic or has_quoted_basis):
            errs.append(f"{case_id}/{rid}: a numeric value needs arithmetic or a quoted law basis")
        if not (has_arithmetic or has_quoted_basis or has_sourced_fact):
            errs.append(f"{case_id}/{rid}: a value needs arithmetic, a quoted law basis or a "
                        "sourced fact")
    if not str(row.get("why_applies", "")).strip():
        errs.append(f"{case_id}/{rid}: the row must say why the rule applies")
    if not str(row.get("source_reference", "")).strip():
        errs.append(f"{case_id}/{rid}: the row must name where its value stands in the "
                    "independent reading")
    return errs


def facts_used_errors(case_id: str, row: dict) -> list[str]:
    errs: list[str] = []
    rid = row.get("row_id", "?")
    for fact in row.get("facts_used", []):
        if set(fact) != lib.FACT_KEYS:
            errs.append(f"{case_id}/{rid}: a fact-used entry's keys differ from the fixed set")
        elif not str(fact["source"]).strip():
            errs.append(f"{case_id}/{rid}: a fact used needs a source: {fact.get('name')!r}")
    return errs


def arithmetic_shape_errors(case_id: str, row: dict) -> list[str]:
    errs: list[str] = []
    rid = row.get("row_id", "?")
    for step in row.get("arithmetic", []):
        if set(step) != lib.ARITH_KEYS:
            errs.append(f"{case_id}/{rid}: an arithmetic step's keys differ from the fixed set")
            continue
        if step["operation"] not in lib.OPERATIONS:
            errs.append(f"{case_id}/{rid}: operation {step['operation']!r} invalid")
        if step["rounding"] not in lib.ROUNDINGS:
            errs.append(f"{case_id}/{rid}: rounding {step['rounding']!r} invalid")
        for operand in step["operands"]:
            if set(operand) != lib.OPERAND_KEYS:
                errs.append(f"{case_id}/{rid}: an operand's keys differ from the fixed set")
    return errs


# --------------------------------------------------------------------------
# S8: the README carries the rules and the not-captured list
# --------------------------------------------------------------------------
def readme_errors() -> list[str]:
    errs: list[str] = []
    path = lib.DOCS_DIR / "README.md"
    if not path.is_file():
        return [f"README.md is missing under {lib.DOCS_DIR}"]
    text = path.read_text()
    low = text.lower()
    required = [
        ("prepared by an ai helper", "it was prepared by an AI helper"),
        ("recomputed by a second ai", "it was recomputed by a second AI"),
        ("agreement", "agreement between two AI answers alone is not proof"),
        ("not professionally reviewed", "it is a draft reading, not professionally reviewed"),
        ("corrected evidence", "the change rule: corrected evidence"),
        ("corrected reading", "the change rule: a corrected reading"),
        ("change in the law", "the change rule: a change in the law"),
        ("investigated on both sides", "a disagreement with the program is investigated both ways"),
        ("step p1", "the README names step P1 (its text is now captured and worked here)"),
    ]
    for needle, what in required:
        if needle not in low:
            errs.append(f"README.md does not state: {what}")
    for cid in lib.CASE_IDS:
        if cid not in text:
            errs.append(f"README.md does not list the case {cid!r}")
    for section in NOT_CAPTURED_SECTIONS:
        if section not in text:
            errs.append(f"README.md does not name the not-captured section ZR {section}")
    return errs


# --------------------------------------------------------------------------
# provenance (S4): the two returns are present, unchanged
# --------------------------------------------------------------------------
PROVENANCE_RETURNS = {
    "return-independent-hand-calculation-1.md":
        "INDEPENDENT BLIND HAND-CALCULATION",
    "return-independent-hand-calculation-2.md":
        "FOLLOW-UP",
}

# The two step-P1 readings (task M4-T027), each saved unchanged below a short
# header. The digest pins the whole saved file so a later edit is caught (S1).
STEP_P1_READINGS = {
    "return-independent-hand-calculation-3.md": {
        "marker": "ONE-HARD-RULE COMPLIANCE",
        "digest": "8e0fb09e6d7f4fa946fdf1e4bd5ef8a2c5847fa6ff981779a84a91aff40ff64b",
    },
    "return-independent-hand-calculation-4.md": {
        "marker": "ONE HARD RULE",
        "digest": "5bf5ab28a65af7635e4ea72808e609f4559cfa1f695bcbaf2150164c03f6d639",
    },
}

# The two step-P2 commercial-overlay readings (task M4-T028), each saved unchanged
# below a short header. The digest pins the whole saved file so a later edit is
# caught (S1).
OVERLAY_READINGS = {
    "return-independent-hand-calculation-5.md": {
        "marker": "ONE HARD RULE",
        "digest": "3f7cd65e125ac4343a8a01660e549e49a38113dfc815cab053815df1beec3ff6",
    },
    "return-independent-hand-calculation-6.md": {
        "marker": "ONE-HARD-RULE COMPLIANCE",
        "digest": "2c3d3c3df850735d5a72d1e2bd1e0590dea690c48908838107173e7b5824a426",
    },
}


def provenance_errors() -> list[str]:
    errs: list[str] = []
    for name, marker in PROVENANCE_RETURNS.items():
        path = lib.PROVENANCE_DIR / name
        if not path.is_file():
            errs.append(f"provenance file missing: {name}")
            continue
        text = path.read_text()
        if marker not in text:
            errs.append(f"provenance file {name} does not carry the helper's return")
        if "END-OF-REPORT" not in text:
            errs.append(f"provenance file {name} is not the return in full (no END-OF-REPORT)")
    errs += step_p1_reading_errors()
    errs += overlay_reading_errors()
    errs += step_p3_reading_errors()
    return errs


def _reading_digest_errors(readings: dict, label: str) -> list[str]:
    """A saved reading is present unchanged: it carries its marker and its
    END-OF-REPORT, says it was made from the sealed folder, and hashes to the
    recorded digest, so any later edit to a saved reading is caught (S1)."""
    errs: list[str] = []
    for name, spec in readings.items():
        path = lib.PROVENANCE_DIR / name
        if not path.is_file():
            errs.append(f"{label} reading missing: {name}")
            continue
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        if spec["marker"] not in text:
            errs.append(f"{label} reading {name} does not carry the reading's return")
        if "END-OF-REPORT" not in text:
            errs.append(f"{label} reading {name} is not the return in full (no END-OF-REPORT)")
        if "sealed folder" not in text:
            errs.append(f"{label} reading {name} does not say it was made from the sealed folder")
        got = hashlib.sha256(raw).hexdigest()
        if got != spec["digest"]:
            errs.append(
                f"{label} reading {name} digest changed: {got} != recorded {spec['digest']} "
                "(the saved reading must stay byte-for-byte unchanged)"
            )
    return errs


def step_p1_reading_errors() -> list[str]:
    return _reading_digest_errors(STEP_P1_READINGS, "step-P1")


def overlay_reading_errors() -> list[str]:
    return _reading_digest_errors(OVERLAY_READINGS, "overlay")


def step_p3_reading_errors() -> list[str]:
    return _reading_digest_errors(step_p3.STEP_P3_READINGS, "step-P3")


# --------------------------------------------------------------------------
# S2 (step-P1 case): a value only where both readings agree on the same basis
# --------------------------------------------------------------------------
def both_readings_errors(case_id: str, row: dict) -> list[str]:
    """In a two-reading case (step P1, step P2), every row must name BOTH readings
    in its source reference, so a value rests on both and a 'not known' names both
    (S2)."""
    needed = CASE_READINGS.get(case_id)
    if not needed:
        return []
    ref = str(row.get("source_reference", ""))
    if any(name not in ref for name in needed):
        label = _READINGS_LABEL.get(case_id, "")
        return [f"{case_id}/{row.get('row_id', '?')}: source reference must name both {label} "
                "readings (a value needs both readings to agree)"]
    return []


def readings_differ_errors(case_id: str, data: dict) -> list[str]:
    """In a two-reading case, a row whose two readings disagree (or where one says
    not known) must stay 'not known': a value is recorded only where both readings
    agree on the same basis (S2). Giving such a row a value is refused."""
    differ = READINGS_DIFFER.get(case_id, set())
    errs: list[str] = []
    for row in data.get("rows", []):
        if row.get("row_id") in differ:
            kind = row.get("expected", {}).get("kind")
            if kind != "not_known":
                errs.append(
                    f"{case_id}/{row.get('row_id')}: the two readings differ here, so it must be "
                    f"'not known', not {kind!r} (a value needs both readings to agree)"
                )
    return errs


# --------------------------------------------------------------------------
# top-level validate
# --------------------------------------------------------------------------
def validate_case(case_id: str, data: dict) -> list[str]:
    errs: list[str] = []
    errs += program_result_errors(case_id, data)
    errs += structure_errors(case_id, data)
    if errs:
        return errs  # deeper checks assume the fixed shape
    errs += change_log_errors(case_id, data)
    errs += coverage_errors(case_id, data)
    errs += readings_differ_errors(case_id, data)
    errs += step_p3.must_stay_not_known_errors(case_id, data)
    for row in data["rows"]:
        missing = lib.ROW_KEYS - set(row)
        extra = set(row) - lib.ROW_KEYS - lib.OPTIONAL_ROW_KEYS
        if missing or extra:
            errs.append(f"{case_id}/{row.get('row_id', '?')}: row keys differ from the fixed set")
            continue
        errs += citation_errors(case_id, row)
        errs += facts_used_errors(case_id, row)
        errs += arithmetic_shape_errors(case_id, row)
        errs += expected_errors(case_id, row)
        errs += both_readings_errors(case_id, row)
        errs += lib.recompute_row_errors(case_id, row)
    return errs


def validate_all() -> list[str]:
    errs: list[str] = []
    for case_id in lib.CASE_IDS:
        path = lib.case_path(case_id)
        if not path.is_file():
            errs.append(f"case data file missing: {path.name}")
            continue
        errs += validate_case(case_id, lib.load_case(case_id))
    errs += readme_errors()
    errs += provenance_errors()
    errs += step_p3.pinned_coverage_errors(lib.load_case)
    errs += step_p3.superseded_by_errors(lib.load_case, lib.CASE_IDS)
    return errs
