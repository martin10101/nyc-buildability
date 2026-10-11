#!/usr/bin/env python3
"""Structural + promotion check for research evidence records (owner directive D-093).

Enforces the `research_record/v1` specification in docs/research/evidence-records/README.md:
one JSON record per research question that touches an official fact, a legal reading, a
calculation input, a result or a certainty label.

  * `--check [--records-dir DIR]` validates every `*.json` record (README.md ignored), prints
    one line per record (id, research status, code_current, review_state, requested label, and
    the fixed words "structural check only; not a professional verification"), reports code
    drift as a NOTE (never an error), and refuses any record asking for the Verified label
    while any promotion condition is unmet.
  * `--promotion OUTPUT_NAME [--label LABEL]` prints the evidence-state refusals for labelling
    one output. Only `Verified` is gated by evidence state; any other known label is allowed
    and an unknown label is refused.

It cannot say whether a reading of the law is correct; nothing it prints is a professional
verification. Per condition 6 it never promotes to Verified at all until the owner answers
question C1. Exit codes: 0 good; 1 structural error / refused Verified request / empty records
dir (never passes vacuously); 2 usage error or unreadable/invalid JSON. Stdlib only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RECORDS_DIR = REPO_ROOT / "docs" / "research" / "evidence-records"

SCHEMA = "research_record/v1"

# Condition 6: the owner has not yet answered question C1, so nothing is ever Verified.
OWNER_C1_ANSWERED = False
C1_REFUSAL = ("owner question C1 (what must be true before a result is labelled Verified) "
              "is open; nothing is labelled Verified")

VERIFICATION_DISCLAIMER = "structural check only; not a professional verification"

LOT_SCOPES = {"tax_lot", "zoning_lot", "zoning_lot_unconfirmed", "not_lot_specific"}
SITE_SCOPES = {"building", "whole_site", "not_applicable"}
TIME_SCOPES = {"current_law", "historical_approval", "both"}
EVIDENCE_KINDS = {"law_text", "dataset_record", "index_entry", "filing_record", "tax_map",
                  "gis_geometry", "recorded_instrument", "approved_plan", "survey",
                  "agency_guidance", "map_document"}
APPLIES = {"yes", "no", "conditional", "not_determined"}
QUANTITY_BASES = {"law", "deed", "survey", "printed_tax_map", "approved_plan",
                  "filing_attribute", "administrative_record", "gis", "derived"}
RESEARCH_STATUSES = {"not_researched", "searched_not_found", "access_blocked",
                     "conflicting_evidence", "interpretation_awaiting_review",
                     "answered_from_primary_source"}
SEARCH_RESULTS = {"found", "not_found", "access_blocked", "conflicting"}
VERDICTS = {"agrees", "partly_agrees", "disagrees"}
FRESHNESS_METHODS = {"live_fetch", "snapshot"}
REPORT_LABELS = {"Verified", "Provisional", "Illustrative", "Conditional",
                 "Pending verification", "Unresolved"}
# Statuses that can never support a Verified label (README promotion condition 3).
NON_PROMOTABLE_STATUSES = {"not_researched", "searched_not_found", "access_blocked",
                           "conflicting_evidence"}
# status -> the search result that must be named when the status is a dead end.
DEADEND_RESULT = {"searched_not_found": "not_found", "access_blocked": "access_blocked"}


class RecordLoadError(Exception):
    """A record directory or file could not be read / parsed (CLI maps this to exit 2)."""


# --------------------------------------------------------------------------- helpers


def _sha256_lf(path: Path) -> str:
    """sha256 of a file's bytes with CRLF/CR normalized to LF."""
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def _is_date(value) -> bool:
    return isinstance(value, str) and bool(re.match(r"^\d{4}-\d{2}-\d{2}([T ]|$)", value))


def _is_hex64(value) -> bool:
    return (isinstance(value, str) and len(value) == 64
            and all(c in "0123456789abcdef" for c in value.lower()))


def _path_escape_error(rel) -> str | None:
    """Return an error fragment if `rel` is not a safe repository-relative path, else None."""
    if not isinstance(rel, str) or not rel:
        return "must be a non-empty repository-relative path."
    if rel.startswith("/") or (len(rel) > 1 and rel[1] == ":"):
        return f"'{rel}' must be repository-relative, not absolute."
    if ".." in PurePosixPath(rel).parts:
        return f"'{rel}' must not contain '..' (a path escaping the repository root is refused)."
    return None


def _as_record(item):
    """Accept either a (path, dict) tuple (as load_records returns) or a plain dict."""
    if isinstance(item, (tuple, list)) and len(item) == 2 and isinstance(item[1], dict):
        return item[0], item[1]
    if isinstance(item, dict):
        return f"{item.get('record_id', 'rec')}-x.json", item
    return None, None


# --------------------------------------------------------------------------- loading


def load_records(records_dir):
    """Return a sorted list of (path, record_dict). Raise RecordLoadError on any unreadable
    or invalid JSON file, or a missing directory."""
    directory = Path(records_dir)
    if not directory.is_dir():
        raise RecordLoadError(f"records directory does not exist: {records_dir}")
    out = []
    for path in sorted(directory.glob("*.json")):
        try:
            raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
            record = json.loads(raw.decode("utf-8"))
        except (OSError, ValueError, UnicodeError) as exc:
            raise RecordLoadError(f"cannot read/parse evidence record {path.name}: {exc}")
        if not isinstance(record, dict):
            raise RecordLoadError(f"evidence record {path.name} is not a JSON object")
        out.append((path, record))
    return out


# --------------------------------------------------------------------------- validation


def validate_record(record, path, root) -> list[str]:
    """Return a list of structural errors (empty = structurally valid). Each error is a plain
    sentence naming the record id and the offending key."""
    root = Path(root)
    if not isinstance(record, dict):
        return ["(unknown record): the record is not a JSON object."]
    rid = record.get("record_id")
    rid = rid if isinstance(rid, str) and rid else "(unknown record)"
    errors: list[str] = []

    def err(msg: str) -> None:
        errors.append(f"{rid}: {msg}")

    def req_str(obj, key, label=None):
        label = label or f"'{key}'"
        value = obj.get(key) if isinstance(obj, dict) else None
        if not (isinstance(value, str) and value.strip()):
            err(f"key {label} is required and must be a non-empty string.")

    def req_enum(obj, key, allowed, label=None):
        label = label or f"'{key}'"
        value = obj.get(key) if isinstance(obj, dict) else None
        if value not in allowed:
            err(f"key {label} value {value!r} is not one of: {', '.join(sorted(allowed))}.")

    def req_date(obj, key, label=None):
        label = label or f"'{key}'"
        if not _is_date(obj.get(key) if isinstance(obj, dict) else None):
            err(f"key {label} must be an ISO date (YYYY-MM-DD).")

    if record.get("schema") != SCHEMA:
        err(f"key 'schema' must be '{SCHEMA}'.")
    if not (isinstance(record.get("record_id"), str) and record.get("record_id")):
        err("key 'record_id' is required and must be a non-empty string.")
    else:
        name = Path(path).name
        if not name.startswith(record["record_id"]):
            err(f"file name '{name}' must start with record_id '{record['record_id']}'.")
    req_str(record, "title")
    rev = record.get("revision")
    if not (isinstance(rev, int) and not isinstance(rev, bool) and rev >= 1):
        err("key 'revision' must be an integer >= 1.")
    req_date(record, "last_changed")

    _validate_question(record.get("question"), err, req_str, req_enum)
    status = _validate_conclusion(record.get("conclusion"), err, req_str)
    _validate_evidence(record.get("evidence"), root, err, req_str, req_enum, req_date)
    _validate_meaning(record.get("meaning_and_applicability"), err, req_str, req_enum)
    _validate_measurement(record.get("measurement_basis"), err, req_str, req_enum)
    _validate_searches(record.get("searches"), status, err, req_str, req_enum)
    _validate_implementation(record.get("implementation"), root, err, req_str)
    _validate_review(record.get("review"), record.get("revision"), err, req_str, req_enum, req_date)
    _validate_freshness(record.get("freshness"), err, req_str, req_enum, req_date)
    _validate_promotion(record.get("promotion"), err)
    return errors


def _validate_question(q, err, req_str, req_enum):
    if not isinstance(q, dict):
        err("key 'question' must be an object.")
        return
    req_str(q, "text", "'question.text'")
    prop = q.get("property")
    if not (prop == "not property-specific" or isinstance(prop, dict)):
        err("key 'question.property' must be an object or the string 'not property-specific'.")
    req_enum(q, "lot_scope", LOT_SCOPES, "'question.lot_scope'")
    req_enum(q, "site_scope", SITE_SCOPES, "'question.site_scope'")
    req_enum(q, "time_scope", TIME_SCOPES, "'question.time_scope'")


def _validate_conclusion(cc, err, req_str):
    if not isinstance(cc, dict):
        err("key 'conclusion' must be an object.")
        return None
    status = cc.get("research_status")
    if status not in RESEARCH_STATUSES:
        err(f"key 'conclusion.research_status' value {status!r} is not a known status.")
    facts = cc.get("observed_facts")
    if not isinstance(facts, list) or not facts:
        err("key 'conclusion.observed_facts' must be a non-empty list.")
    if not isinstance(cc.get("interpretation"), str):
        err("key 'conclusion.interpretation' must be a string (may be empty).")
    for key in ("conflicts", "conditions", "settled_by"):
        if not isinstance(cc.get(key), list):
            err(f"key 'conclusion.{key}' must be a list.")
    if status == "conflicting_evidence" and not cc.get("conflicts"):
        err("status 'conflicting_evidence' requires a non-empty 'conclusion.conflicts'.")
    if status == "interpretation_awaiting_review" and not (
            isinstance(cc.get("interpretation"), str) and cc["interpretation"].strip()):
        err("status 'interpretation_awaiting_review' requires a non-empty "
            "'conclusion.interpretation'.")
    return status


def _validate_evidence(ev, root, err, req_str, req_enum, req_date):
    if not isinstance(ev, list) or not ev:
        err("key 'evidence' must be a non-empty list.")
        return
    seen = set()
    for i, e in enumerate(ev):
        lab = f"evidence[{i}]"
        if not isinstance(e, dict):
            err(f"{lab} must be an object.")
            continue
        eid = e.get("id")
        if not (isinstance(eid, str) and eid):
            err(f"{lab}.id is required.")
        elif eid in seen:
            err(f"evidence id '{eid}' is duplicated (key '{lab}.id').")
        else:
            seen.add(eid)
        req_enum(e, "kind", EVIDENCE_KINDS, f"'{lab}.kind'")
        for key in ("authority", "title", "reference", "excerpt", "document_date"):
            req_str(e, key, f"'{lab}.{key}'")
        url = e.get("url")
        if not (isinstance(url, str) and (url.startswith("http://") or url.startswith("https://"))):
            err(f"key '{lab}.url' must be an http/https URL.")
        req_date(e, "retrieved", f"'{lab}.retrieved'")
        if "page" not in e:
            err(f"key '{lab}.page' is required (a value or null).")
        _validate_saved_copy(e, lab, root, err)


def _validate_saved_copy(e, lab, root, err):
    saved, sha = e.get("saved_copy"), e.get("sha256")
    if saved is None:
        if sha is not None:
            err(f"key '{lab}.sha256' must be null when saved_copy is null.")
        return
    if not isinstance(saved, str):
        err(f"key '{lab}.saved_copy' must be a repository-relative path string or null.")
        return
    escape = _path_escape_error(saved)
    if escape:
        err(f"key '{lab}.saved_copy' {escape}")
        return
    if not _is_hex64(sha):
        err(f"key '{lab}.sha256' must be 64 hex characters when saved_copy is set.")
        return
    target = root / saved
    if not target.is_file():
        err(f"'{lab}.saved_copy' '{saved}' does not exist under the repository root.")
        return
    actual = _sha256_lf(target)
    if actual != sha:
        err(f"'{lab}.saved_copy' '{saved}' sha256 does not match "
            f"(stored {sha[:12]}..., actual {actual[:12]}...).")


def _validate_meaning(ma, err, req_str, req_enum):
    if not isinstance(ma, dict):
        err("key 'meaning_and_applicability' must be an object.")
        return
    pr = ma.get("provisions_read")
    if not isinstance(pr, list) or not pr:
        err("key 'meaning_and_applicability.provisions_read' must be a non-empty list.")
    if not isinstance(ma.get("exceptions_considered"), list):
        err("key 'meaning_and_applicability.exceptions_considered' must be a list.")
    req_str(ma, "reading", "'meaning_and_applicability.reading'")
    req_enum(ma, "applies", APPLIES, "'meaning_and_applicability.applies'")


def _validate_measurement(mb, err, req_str, req_enum):
    if not isinstance(mb, dict):
        err("key 'measurement_basis' is required and must be an object.")
        return
    quantities = mb.get("quantities")
    if not isinstance(quantities, list):
        err("key 'measurement_basis.quantities' must be a list.")
    else:
        for i, qt in enumerate(quantities):
            lab = f"measurement_basis.quantities[{i}]"
            if not isinstance(qt, dict):
                err(f"{lab} must be an object.")
                continue
            for key in ("name", "units", "scope"):
                req_str(qt, key, f"'{lab}.{key}'")
            if "value" not in qt:
                err(f"key '{lab}.value' is required.")
            req_enum(qt, "basis", QUANTITY_BASES, f"'{lab}.basis'")
    req_str(mb, "double_count_risk", "'measurement_basis.double_count_risk'")


def _validate_searches(se, status, err, req_str, req_enum):
    if not isinstance(se, list):
        err("key 'searches' must be a list.")
        return
    for i, s in enumerate(se):
        lab = f"searches[{i}]"
        if not isinstance(s, dict):
            err(f"{lab} must be an object.")
            continue
        for key in ("source", "query"):
            req_str(s, key, f"'{lab}.{key}'")
        req_enum(s, "result", SEARCH_RESULTS, f"'{lab}.result'")
        for key in ("missing_item", "next_step"):
            if not isinstance(s.get(key), str):
                err(f"key '{lab}.{key}' must be a string.")
        if not isinstance(s.get("affected_outputs"), list):
            err(f"key '{lab}.affected_outputs' must be a list.")
    if status in DEADEND_RESULT:
        want = DEADEND_RESULT[status]
        ok = any(isinstance(s, dict) and s.get("result") == want
                 and isinstance(s.get("missing_item"), str) and s["missing_item"].strip()
                 and isinstance(s.get("next_step"), str) and s["next_step"].strip()
                 for s in se)
        if not ok:
            err(f"status '{status}' requires a 'searches' entry with result '{want}' "
                f"naming its missing_item and next_step.")


def _validate_implementation(im, root, err, req_str):
    if not isinstance(im, dict):
        err("key 'implementation' must be an object.")
        return
    ao = im.get("affected_outputs")
    if not isinstance(ao, list) or not ao:
        err("key 'implementation.affected_outputs' must be a non-empty list.")
    cp = im.get("code_paths")
    paths = []
    if not isinstance(cp, list):
        err("key 'implementation.code_paths' must be a list.")
    else:
        paths = [c for c in cp if isinstance(c, str)]
        for c in cp:
            if not isinstance(c, str):
                err("each 'implementation.code_paths' entry must be a string.")
                continue
            escape = _path_escape_error(c)
            if escape:
                err(f"'implementation.code_paths' entry {escape}")
            elif not (root / c).is_file():
                err(f"'implementation.code_paths' entry '{c}' does not exist under the "
                    f"repository root.")
    ci = im.get("code_identity")
    if not isinstance(ci, dict):
        err("key 'implementation.code_identity' must be an object.")
    else:
        if isinstance(cp, list) and set(ci.keys()) != set(paths):
            err("'implementation.code_identity' keys must equal 'implementation.code_paths'.")
        for key, value in ci.items():
            if not _is_hex64(value):
                err(f"'implementation.code_identity' value for '{key}' must be 64 hex "
                    f"characters.")
    we = im.get("worked_example")
    if not isinstance(we, dict):
        err("key 'implementation.worked_example' must be an object.")
    else:
        for key in ("inputs", "expected", "basis", "prepared_by"):
            if key not in we:
                err(f"key 'implementation.worked_example.{key}' is required.")
    for key in ("regression_cases", "dependency_assessment"):
        if not isinstance(im.get(key), list):
            err(f"key 'implementation.{key}' must be a list.")


def _validate_review(rv, revision, err, req_str, req_enum, req_date):
    if not isinstance(rv, dict):
        err("key 'review' must be an object.")
        return
    producer = rv.get("producer")
    if not (isinstance(producer, str) and producer):
        err("key 'review.producer' is required.")
    ars = rv.get("agent_reviews")
    if not isinstance(ars, list):
        err("key 'review.agent_reviews' must be a list.")
    else:
        for i, ar in enumerate(ars):
            lab = f"review.agent_reviews[{i}]"
            if not isinstance(ar, dict):
                err(f"{lab} must be an object.")
                continue
            reviewer = ar.get("reviewer")
            if not (isinstance(reviewer, str) and reviewer):
                err(f"key '{lab}.reviewer' is required.")
            elif isinstance(producer, str) and reviewer == producer:
                err(f"'{lab}.reviewer' must not equal the record producer '{producer}' "
                    f"(an independent reviewer is required).")
            req_date(ar, "date", f"'{lab}.date'")
            if not (isinstance(ar.get("reviewed_revision"), int)
                    and not isinstance(ar.get("reviewed_revision"), bool)):
                err(f"key '{lab}.reviewed_revision' must be an integer.")
            if not isinstance(ar.get("reviewed_code_identity"), dict):
                err(f"key '{lab}.reviewed_code_identity' must be an object.")
            req_enum(ar, "verdict", VERDICTS, f"'{lab}.verdict'")
            if not isinstance(ar.get("findings"), list):
                err(f"key '{lab}.findings' must be a list.")
            if "report" not in ar:
                err(f"key '{lab}.report' is required (a repository path or null).")
    pro = rv.get("professional_review")
    if pro is None:
        return
    if not isinstance(pro, dict):
        err("key 'review.professional_review' must be null or an object.")
        return
    for key in ("reviewer_name", "role", "date", "decision", "comments"):
        req_str(pro, key, f"'review.professional_review.{key}'")
    if not (isinstance(pro.get("reviewed_revision"), int)
            and not isinstance(pro.get("reviewed_revision"), bool)):
        err("key 'review.professional_review.reviewed_revision' must be an integer.")


def _validate_freshness(fr, err, req_str, req_enum, req_date):
    if not isinstance(fr, dict):
        err("key 'freshness' must be an object.")
        return
    req_date(fr, "checked_on", "'freshness.checked_on'")
    req_enum(fr, "method", FRESHNESS_METHODS, "'freshness.method'")
    snap = fr.get("snapshot_date")
    if snap is not None and not _is_date(snap):
        err("key 'freshness.snapshot_date' must be an ISO date or null.")
    req_str(fr, "limitation", "'freshness.limitation'")


def _validate_promotion(pm, err):
    if not isinstance(pm, dict):
        err("key 'promotion' must be an object.")
        return
    label = pm.get("requested_label")
    if label is not None and label not in REPORT_LABELS:
        err(f"key 'promotion.requested_label' value {label!r} is not a known report label "
            f"or null.")


# --------------------------------------------------------------------------- derived


def _current_code_identity(code_paths, root) -> dict:
    out = {}
    for c in code_paths:
        if not isinstance(c, str) or _path_escape_error(c):
            continue
        target = root / c
        if target.is_file():
            out[c] = _sha256_lf(target)
    return out


def derive(record, root) -> dict:
    """Return {'code_current': bool, 'review_state': 'none'|'current'|'stale'}."""
    root = Path(root)
    im = record.get("implementation") if isinstance(record, dict) else None
    im = im if isinstance(im, dict) else {}
    code_paths = [c for c in (im.get("code_paths") or []) if isinstance(c, str)]
    stored = im.get("code_identity") if isinstance(im.get("code_identity"), dict) else {}
    current = _current_code_identity(code_paths, root)
    code_current = all(stored.get(c) == current.get(c) for c in code_paths)

    rv = record.get("review") if isinstance(record, dict) else None
    rv = rv if isinstance(rv, dict) else {}
    reviews = [a for a in (rv.get("agent_reviews") or []) if isinstance(a, dict)]
    if not reviews:
        return {"code_current": code_current, "review_state": "none"}
    latest = max(enumerate(reviews), key=lambda t: (str(t[1].get("date") or ""), t[0]))[1]
    reviewed_code = latest.get("reviewed_code_identity")
    reviewed_code = reviewed_code if isinstance(reviewed_code, dict) else {}
    matches_rev = latest.get("reviewed_revision") == record.get("revision")
    matches_code = all(reviewed_code.get(c) == current.get(c) for c in code_paths)
    review_state = "current" if (matches_rev and matches_code) else "stale"
    return {"code_current": code_current, "review_state": review_state}


# --------------------------------------------------------------------------- promotion


def promotion_refusals(output_name, records, root, label="Verified") -> list[str]:
    """Return the list of reasons the output may NOT be promoted to `label` (empty = allowed).

    Only `Verified` is gated by evidence state. Any other known label is always allowed; an
    unknown label is refused. Condition 6 (owner question C1) always refuses Verified while
    OWNER_C1_ANSWERED is False."""
    root = Path(root)
    if label not in REPORT_LABELS:
        return [f"requested label {label!r} is not a known report label."]
    if label != "Verified":
        return []

    refusals: list[str] = []
    covering = []
    for item in records:
        path, rec = _as_record(item)
        if rec is None:
            continue
        outputs = (rec.get("implementation") or {}).get("affected_outputs") or []
        if output_name in outputs:
            covering.append((path, rec))

    if not covering:
        refusals.append(f"no evidence record covers the output '{output_name}'.")
    for path, rec in covering:
        rid = rec.get("record_id", "(unknown record)")
        errs = validate_record(rec, path, root)
        if errs:
            refusals.append(f"record {rid} covering '{output_name}' is not structurally valid "
                            f"({len(errs)} issue(s)).")
            continue
        conclusion = rec.get("conclusion") or {}
        status = conclusion.get("research_status")
        if status in NON_PROMOTABLE_STATUSES:
            refusals.append(f"record {rid}: research status '{status}' cannot support a "
                            f"Verified label for '{output_name}'.")
        if conclusion.get("conflicts"):
            refusals.append(f"record {rid}: open conflicts prevent a Verified label for "
                            f"'{output_name}'.")
        if conclusion.get("conditions"):
            refusals.append(f"record {rid}: open conditions prevent a Verified label for "
                            f"'{output_name}'.")
        derived = derive(rec, root)
        if derived["review_state"] != "current":
            refusals.append(f"record {rid}: the agent review is '{derived['review_state']}', "
                            f"not a current independent review, for '{output_name}'.")
        if not derived["code_current"]:
            refusals.append(f"record {rid}: the linked code changed after review (staleness) "
                            f"for '{output_name}'.")
        pro = (rec.get("review") or {}).get("professional_review")
        if not (isinstance(pro, dict) and pro.get("reviewed_revision") == rec.get("revision")):
            refusals.append(f"record {rid}: no named professional review for the current "
                            f"revision for '{output_name}'.")
    if not OWNER_C1_ANSWERED:
        refusals.append(C1_REFUSAL)
    return refusals


# --------------------------------------------------------------------------- CLI


def _derive_root(records_dir: Path) -> Path:
    """The repository root (parent of tools/). When records-dir is laid out as
    <root>/docs/research/evidence-records (the real layout and the one the tests build), the
    root is three levels up; otherwise fall back to this file's repository root."""
    resolved = records_dir.resolve()
    if resolved.parts[-3:] == ("docs", "research", "evidence-records"):
        return resolved.parents[2]
    return REPO_ROOT


def cmd_check(records_dir: Path, root: Path) -> int:
    try:
        records = load_records(records_dir)
    except RecordLoadError as exc:
        print(f"usage/JSON error: {exc}", file=sys.stderr)
        return 2
    if not records:
        print(f"ERROR: no *.json evidence records found in {records_dir} — the check never "
              f"passes vacuously.")
        return 1

    errors: list[str] = []
    print(f"# Research evidence-record check — {len(records)} record(s) in {records_dir}")
    print(VERIFICATION_DISCLAIMER)
    for path, rec in records:
        rid = rec.get("record_id", "(unknown)")
        status = (rec.get("conclusion") or {}).get("research_status")
        label = (rec.get("promotion") or {}).get("requested_label")
        derived = derive(rec, root)
        print(f"  {rid}  status={status}  code_current={derived['code_current']}  "
              f"review_state={derived['review_state']}  requested_label={label}  "
              f"- {VERIFICATION_DISCLAIMER}")
        if not derived["code_current"]:
            print(f"  NOTE {rid}: linked code changed after the record was written "
                  f"(code_current False) - recheck and revise; this is reported, not failed.")
        errors.extend(validate_record(rec, path, root))

    for path, rec in records:
        if (rec.get("promotion") or {}).get("requested_label") == "Verified":
            rid = rec.get("record_id", "(unknown)")
            for output in (rec.get("implementation") or {}).get("affected_outputs") or []:
                for reason in promotion_refusals(output, records, root, "Verified"):
                    errors.append(f"{rid}: Verified promotion of '{output}' refused: {reason}")

    if errors:
        print("\nFAIL:")
        for e in errors:
            print(f"  {e}")
        return 1
    print("\nPASS: every record is structurally valid and no record claims the Verified label "
          "without meeting every condition.")
    return 0


def cmd_promotion(output_name, records_dir: Path, root: Path, label: str) -> int:
    try:
        records = load_records(records_dir)
    except RecordLoadError as exc:
        print(f"usage/JSON error: {exc}", file=sys.stderr)
        return 2
    refusals = promotion_refusals(output_name, records, root, label)
    if refusals:
        print(f"REFUSED to label '{output_name}' as {label} ({VERIFICATION_DISCLAIMER}):")
        for reason in refusals:
            print(f"  {reason}")
        return 1
    print(f"No evidence-state refusal for labelling '{output_name}' as {label} "
          f"({VERIFICATION_DISCLAIMER}).")
    return 0


def main(argv) -> int:
    parser = argparse.ArgumentParser(
        description="Structural + promotion check for research evidence records (D-093).")
    parser.add_argument("--check", action="store_true",
                        help="validate every record in --records-dir.")
    parser.add_argument("--records-dir", default=None,
                        help="directory of *.json records (default docs/research/evidence-records).")
    parser.add_argument("--promotion", metavar="OUTPUT_NAME", default=None,
                        help="print evidence-state refusals for labelling one output.")
    parser.add_argument("--label", default="Verified",
                        help="label to test with --promotion (default Verified).")
    args = parser.parse_args(argv)

    if bool(args.check) == bool(args.promotion):
        print("usage error: pass exactly one of --check or --promotion.", file=sys.stderr)
        return 2

    records_dir = Path(args.records_dir) if args.records_dir else DEFAULT_RECORDS_DIR
    root = _derive_root(records_dir)
    if args.check:
        return cmd_check(records_dir, root)
    return cmd_promotion(args.promotion, records_dir, root, args.label)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
