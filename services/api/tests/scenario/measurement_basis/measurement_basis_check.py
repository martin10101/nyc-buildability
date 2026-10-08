#!/usr/bin/env python3
"""Deterministic checker for the measurement-basis examples (M5-T126).

Pure stdlib. No rule math, no network, no AI call, and no import from the rule engine,
the scenario engine or any program output. It reads the authored example data files, the
captured law snapshots, the embedded official HPD quote and the hand-written record, and
returns a list of plain-text problems (empty == clean). It covers:

* S1  - each area is defined by its source before any formula (the record).
* S2  - one schedule: every component appears once with its measured area and its
  treatment under BOTH systems; the HPD rows say "mechanical and plumbing chases" and
  keep partitions inside an apartment in the unit area.
* S3  - no allowance of ZR 23-23 / exclusion of ZR 12-10 is taken unless the example
  states the condition and shows it met; nothing already out of zoning is deducted again.
* S4  - measured areas come from the stated dimensions, not from the maximum floor area.
* S5  - zoning floor area and HPD area are summed SEPARATELY from one schedule, then a
  reconciliation accounts for every square foot of the difference by component.
* S6  - arithmetic recomputes exactly (delegated to :mod:`measurement_basis_lib`).
* S7/S9 - the ratio is HPD area / residential zoning floor area; the legal cap is kept
  apart; no percentage is presented as typical.
* law text is tied to its capture (ZR) or to the embedded official HPD quote.

The per-example checkers are separate functions so the test can call them on mutated
in-memory data for the negative (mutation) cases.
"""
from __future__ import annotations

import pathlib
import sys

_HERE = pathlib.Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import json  # noqa: E402
from decimal import Decimal  # noqa: E402

import measurement_basis_fit as fit  # noqa: E402
import measurement_basis_lib as lib  # noqa: E402

# Field names / phrases that would smuggle a program result into an example.
FORBIDDEN_KEY_SUBSTRINGS = ("program", "actual", "first_screen", "firstscreen")
FORBIDDEN_VALUE_PHRASES = (
    "program today", "first screen", "the program gives", "program's answer",
    "program result", "as the program", "what the program",
)
# The HPD component vocabulary the owner required (R434): the precise term.
MECHANICAL_PLUMBING_CHASES = "mechanical and plumbing chases"


# --------------------------------------------------------------------------
# S3-adjacent: nothing from a program run
# --------------------------------------------------------------------------
def program_result_errors(example_id: str, data) -> list[str]:
    errs: list[str] = []

    def walk(node, where: str):
        if isinstance(node, dict):
            for key, value in node.items():
                low = str(key).lower()
                for bad in FORBIDDEN_KEY_SUBSTRINGS:
                    if bad in low:
                        errs.append(f"{example_id}: field name {key!r} at {where} looks like a "
                                    "program result (an example never comes from a program run)")
                walk(value, f"{where}.{key}")
        elif isinstance(node, list):
            for i, item in enumerate(node):
                walk(item, f"{where}[{i}]")
        elif isinstance(node, str):
            low = node.lower()
            for phrase in FORBIDDEN_VALUE_PHRASES:
                if phrase in low:
                    errs.append(f"{example_id}: text at {where} contains {phrase!r}; an example "
                                "never quotes a program run")

    walk(data, example_id)
    return errs


# --------------------------------------------------------------------------
# structure (S2): fixed, complete fields
# --------------------------------------------------------------------------
def structure_errors(example_id: str, data: dict) -> list[str]:
    errs: list[str] = []
    if set(data) != lib.EXAMPLE_KEYS:
        errs.append(f"{example_id}: example keys {sorted(set(data) ^ lib.EXAMPLE_KEYS)} differ "
                    "from the fixed set")
        return errs
    if data["example_id"] != example_id:
        errs.append(f"{example_id}: example_id field {data['example_id']!r} != file stem")
    if not isinstance(data["mixed_use"], bool):
        errs.append(f"{example_id}: mixed_use must be a boolean")
    for field in ("title", "made_up_note", "standing_label", "building", "assumptions_note"):
        if not str(data[field]).strip():
            errs.append(f"{example_id}: {field} is empty")
    for name in ("components", "what_it_shows", "what_it_does_not_show", "sources", "change_log"):
        if not isinstance(data[name], list) or not data[name]:
            errs.append(f"{example_id}: {name} must be a non-empty list")
    if "made up" not in data["made_up_note"].lower():
        errs.append(f"{example_id}: made_up_note must label the layout as made up")
    if "not professionally reviewed" not in data["standing_label"].lower():
        errs.append(f"{example_id}: standing_label must say it is not professionally reviewed")
    # S4: the layout is not derived from the maximum floor area the law allows.
    if "maximum" not in data["made_up_note"].lower() and "far" not in data["made_up_note"].lower():
        errs.append(f"{example_id}: made_up_note must say the areas come from the layout, not the "
                    "maximum floor area the law allows")
    return errs


def change_log_errors(example_id: str, data: dict) -> list[str]:
    errs: list[str] = []
    log = data.get("change_log", [])
    for entry in log:
        if set(entry) != lib.CHANGE_LOG_KEYS:
            errs.append(f"{example_id}: a change-log entry's keys differ from the fixed set")
        elif not all(str(entry[k]).strip() for k in lib.CHANGE_LOG_KEYS):
            errs.append(f"{example_id}: a change-log entry has an empty field")
    if log and "creat" not in (log[0].get("summary", "").lower()):
        errs.append(f"{example_id}: the first change-log entry must record the example's creation")
    for prev, cur in zip(log, log[1:], strict=False):
        if cur["date"] < prev["date"]:
            errs.append(f"{example_id}: change-log dates are not in order")
    return errs


# --------------------------------------------------------------------------
# components (S2/S3): one row per component, both treatments, conditions
# --------------------------------------------------------------------------
def component_shape_errors(example_id: str, comp: dict) -> list[str]:
    errs: list[str] = []
    cid = comp.get("component_id", "?")
    if set(comp) != lib.COMPONENT_KEYS:
        return [f"{example_id}/{cid}: component keys differ from the fixed set"]
    if comp["portion"] not in lib.PORTIONS:
        errs.append(f"{example_id}/{cid}: portion {comp['portion']!r} invalid")
    for field in ("name", "how_measured"):
        if not str(comp[field]).strip():
            errs.append(f"{example_id}/{cid}: {field} is empty")
    if not isinstance(comp["area_parts"], list) or not comp["area_parts"]:
        errs.append(f"{example_id}/{cid}: area_parts must be a non-empty list")
    for part in comp["area_parts"]:
        if set(part) != lib.AREA_PART_KEYS:
            errs.append(f"{example_id}/{cid}: an area part's keys differ from the fixed set")
        elif part["sign"] not in ("add", "subtract"):
            errs.append(f"{example_id}/{cid}: an area part sign {part['sign']!r} invalid")
    errs += zoning_shape_errors(example_id, comp)
    errs += hpd_shape_errors(example_id, comp)
    return errs


def zoning_shape_errors(example_id: str, comp: dict) -> list[str]:
    errs: list[str] = []
    cid = comp["component_id"]
    z = comp["zoning"]
    if set(z) != lib.ZONING_KEYS:
        return [f"{example_id}/{cid}: zoning keys differ from the fixed set"]
    if z["treatment"] not in lib.ZONING_TREATMENTS:
        errs.append(f"{example_id}/{cid}: zoning treatment {z['treatment']!r} invalid")
    if not isinstance(z["condition_shown"], bool):
        errs.append(f"{example_id}/{cid}: zoning.condition_shown must be a boolean")
    if not str(z["provision"]).strip():
        errs.append(f"{example_id}/{cid}: zoning needs a governing provision")
    # S3: a conditional treatment must state the condition.
    if z["treatment"] in ("exclude", "exclude_if_condition") and not str(z["condition"]).strip():
        errs.append(f"{example_id}/{cid}: a conditional zoning exclusion must state its condition")
    exclusion = z["exclusion"]
    if set(exclusion) != lib.EXCLUSION_KEYS:
        errs.append(f"{example_id}/{cid}: exclusion keys differ from the fixed set")
    elif exclusion["method"] not in lib.EXCLUSION_METHODS:
        errs.append(f"{example_id}/{cid}: exclusion method {exclusion['method']!r} invalid")
    else:
        for cand in exclusion["candidates"]:
            if set(cand) != lib.CANDIDATE_KEYS:
                errs.append(f"{example_id}/{cid}: a candidate's keys differ from the fixed set")
            elif cand["operation"] not in lib.CANDIDATE_OPERATIONS:
                errs.append(f"{example_id}/{cid}: candidate operation {cand['operation']!r} bad")
    errs += citation_errors(example_id, cid, z["citations"])
    return errs


def hpd_shape_errors(example_id: str, comp: dict) -> list[str]:
    errs: list[str] = []
    cid = comp["component_id"]
    h = comp["hpd"]
    if set(h) != lib.HPD_KEYS:
        return [f"{example_id}/{cid}: hpd keys differ from the fixed set"]
    if h["treatment"] not in lib.HPD_TREATMENTS:
        errs.append(f"{example_id}/{cid}: hpd treatment {h['treatment']!r} invalid")
    if not str(h["reason"]).strip():
        errs.append(f"{example_id}/{cid}: hpd needs a reason")
    errs += citation_errors(example_id, cid, h["citations"])
    return errs


# --------------------------------------------------------------------------
# S6-adjacent: law text tied to its capture or to the embedded HPD quote
# --------------------------------------------------------------------------
def _strip_markup(text: str) -> str:
    return text.replace("#", "")


def citation_errors(example_id: str, cid: str, citations: list) -> list[str]:
    errs: list[str] = []
    if not citations:
        errs.append(f"{example_id}/{cid}: a treatment needs at least one citation")
    for cite in citations:
        if set(cite) != lib.CITATION_KEYS:
            errs.append(f"{example_id}/{cid}: a citation's keys differ from the fixed set")
            continue
        if cite["kind"] not in lib.CITATION_KINDS:
            errs.append(f"{example_id}/{cid}: citation kind {cite['kind']!r} invalid")
            continue
        if not str(cite["quote"]).strip():
            errs.append(f"{example_id}/{cid}: a citation needs a quote")
            continue
        if cite["kind"] == "captured":
            errs += _captured_citation_errors(example_id, cid, cite)
        else:
            errs += _guideline_citation_errors(example_id, cid, cite)
    return errs


def _captured_citation_errors(example_id: str, cid: str, cite: dict) -> list[str]:
    errs: list[str] = []
    if not str(cite["section"]).strip():
        errs.append(f"{example_id}/{cid}: a captured citation needs a section")
    snap_path = lib.REPO_ROOT / cite["snapshot_file"]
    if not str(cite["snapshot_id"]).strip() or not str(cite["snapshot_file"]).strip():
        errs.append(f"{example_id}/{cid}: a captured citation needs a snapshot id and file")
        return errs
    if not snap_path.is_file():
        errs.append(f"{example_id}/{cid}: capture file missing: {cite['snapshot_file']}")
        return errs
    snap = json.loads(snap_path.read_text())
    if snap["content_digest_sha256"] != cite["content_digest"]:
        errs.append(f"{example_id}/{cid}: law digest for {cite['section']} does not match the "
                    f"capture {cite['snapshot_id']}")
    if snap["source"]["request_url"] != cite["official_url"]:
        errs.append(f"{example_id}/{cid}: official_url for {cite['section']} does not match the "
                    f"capture {cite['snapshot_id']}")
    if _strip_markup(cite["quote"]) not in _strip_markup(snap["verbatim_excerpt"]):
        errs.append(f"{example_id}/{cid}: the quoted words for {cite['section']} are not found in "
                    f"the capture {cite['snapshot_id']}")
    for empty in ("edition", "date_read", "status_note"):
        if str(cite[empty]).strip():
            errs.append(f"{example_id}/{cid}: a captured citation must leave {empty} empty")
    return errs


def _guideline_citation_errors(example_id: str, cid: str, cite: dict) -> list[str]:
    errs: list[str] = []
    if cite["quote"] not in lib.HPD_UNIT_AREA_CALCULATION:
        errs.append(f"{example_id}/{cid}: the HPD quote is not found in the embedded official "
                    "UNIT AREA CALCULATION text (read 2026-10-07)")
    if cite["official_url"] != lib.HPD_SOURCE["official_url"]:
        errs.append(f"{example_id}/{cid}: the HPD citation url does not match the official source")
    if str(cite["edition"]).strip() != lib.HPD_SOURCE["edition"]:
        errs.append(f"{example_id}/{cid}: the HPD citation must record the 2026 edition")
    if str(cite["date_read"]).strip() != lib.HPD_SOURCE["date_read"]:
        errs.append(f"{example_id}/{cid}: the HPD citation must record the date read")
    if "guideline" not in str(cite["status_note"]).lower():
        errs.append(f"{example_id}/{cid}: the HPD citation must say it is a guideline, not law")
    for empty in ("snapshot_id", "snapshot_file", "content_digest"):
        if str(cite[empty]).strip():
            errs.append(f"{example_id}/{cid}: an HPD (guideline) citation must leave {empty} empty")
    return errs


# --------------------------------------------------------------------------
# S2/S3/S5: areas, stored fields and the reconciliation recompute exactly
# --------------------------------------------------------------------------
def arithmetic_errors(example_id: str, comp: dict) -> list[str]:
    """Recompute a component's measured area, its zoning exclusion and its HPD counted
    area from the stated dimensions, and compare with the stored values. A changed
    dimension is caught here and names the example and the component."""
    errs: list[str] = []
    cid = comp["component_id"]
    measured = lib.component_area(comp)
    if measured != Decimal(str(comp["measured_area"])):
        errs.append(f"{example_id}/{cid}: measured_area recomputes to {measured} but the example "
                    f"records {comp['measured_area']}")
    try:
        excluded = lib.zoning_excluded(comp)
    except (ValueError, ArithmeticError) as exc:
        return errs + [f"{example_id}/{cid}: zoning exclusion did not compute: {exc}"]
    if excluded != Decimal(str(comp["zoning"]["excluded_area"])):
        errs.append(f"{example_id}/{cid}: zoning excluded_area recomputes to {excluded} but the "
                    f"example records {comp['zoning']['excluded_area']}")
    # S3: an allowance not shown must take nothing; a capped allowance never exceeds measured.
    if not comp["zoning"]["condition_shown"] and excluded != 0:
        errs.append(f"{example_id}/{cid}: the condition is not shown, so no area may be excluded")
    if excluded > measured:
        errs.append(f"{example_id}/{cid}: zoning excluded_area {excluded} exceeds the measured "
                    f"area {measured} (a space cannot be deducted beyond itself)")
    hpd = lib.hpd_counted(comp)
    if hpd != Decimal(str(comp["hpd"]["counted_area"])):
        errs.append(f"{example_id}/{cid}: hpd counted_area recomputes to {hpd} but the example "
                    f"records {comp['hpd']['counted_area']}")
    return errs


def reconciliation_errors(example_id: str, data: dict) -> list[str]:
    """Recompute both totals SEPARATELY from the schedule and check the bridge accounts
    for every square foot of the difference by component, with nothing deducted twice."""
    errs: list[str] = []
    recon = data["reconciliation"]
    if set(recon) != lib.RECON_KEYS:
        return [f"{example_id}: reconciliation keys differ from the fixed set"]
    zoning = lib.residential_zoning_floor_area(data)
    hpd = lib.total_hpd_dwelling_unit_area(data)
    if zoning != Decimal(str(recon["residential_zoning_floor_area"])):
        errs.append(f"{example_id}: residential zoning floor area recomputes to {zoning} but the "
                    f"example records {recon['residential_zoning_floor_area']}")
    if hpd != Decimal(str(recon["total_hpd_dwelling_unit_area"])):
        errs.append(f"{example_id}: total HPD dwelling-unit area recomputes to {hpd} but the "
                    f"example records {recon['total_hpd_dwelling_unit_area']}")
    errs += bridge_errors(example_id, data, zoning, hpd)
    errs += ratio_errors(example_id, data, zoning, hpd)
    return errs


def bridge_errors(example_id: str, data: dict, zoning: Decimal, hpd: Decimal) -> list[str]:
    """The bridge must list exactly the components whose zoning and HPD contributions
    differ, each once, with the right amount; walking it from zoning reaches HPD. A step
    for a component already out of zoning (contribution 0) is a double deduction."""
    errs: list[str] = []
    recon = data["reconciliation"]
    derived = {
        c["component_id"]: lib.bridge_contribution(c)
        for c in data["components"]
        if lib.bridge_contribution(c) != 0
    }
    seen: set[str] = set()
    walked = zoning
    for step in recon["bridge"]:
        if set(step) != lib.BRIDGE_KEYS:
            errs.append(f"{example_id}: a bridge step's keys differ from the fixed set")
            continue
        comp_id = step["component_id"]
        if comp_id in seen:
            errs.append(f"{example_id}: component {comp_id!r} appears twice in the bridge "
                        "(deducted twice)")
            continue
        seen.add(comp_id)
        if step["direction"] not in lib.BRIDGE_DIRECTIONS:
            errs.append(f"{example_id}: bridge direction {step['direction']!r} invalid")
            continue
        area = Decimal(str(step["area"]))
        if comp_id not in derived:
            errs.append(f"{example_id}: bridge step for {comp_id!r} deducts area that is not in "
                        "the residential zoning floor area (nothing already excluded may be "
                        "deducted again)")
            continue
        want = derived[comp_id]
        signed = area if step["direction"] == "subtract" else -area
        if signed != want:
            errs.append(f"{example_id}: bridge step for {comp_id!r} is {step['direction']} {area} "
                        f"but the schedule gives {want}")
        walked -= signed
    missing = set(derived) - seen
    if missing:
        errs.append(f"{example_id}: the bridge omits component(s) {sorted(missing)} whose zoning "
                    "and HPD treatments differ")
    if not errs and walked != hpd:
        errs.append(f"{example_id}: walking the bridge from zoning reaches {walked}, not the HPD "
                    f"total {hpd}")
    return errs


def ratio_errors(example_id: str, data: dict, zoning: Decimal, hpd: Decimal) -> list[str]:
    errs: list[str] = []
    ratio = data["reconciliation"]["ratio"]
    if set(ratio) != lib.RATIO_KEYS:
        return [f"{example_id}: ratio keys differ from the fixed set"]
    if Decimal(str(ratio["numerator"])) != hpd:
        errs.append(f"{example_id}: ratio numerator must be the HPD dwelling-unit area {hpd}")
    if Decimal(str(ratio["denominator"])) != zoning:
        errs.append(f"{example_id}: ratio denominator must be the residential zoning floor area "
                    f"{zoning}")
    want = lib.ratio_value(data)
    if Decimal(str(ratio["value"])) != want:
        errs.append(f"{example_id}: ratio value recomputes to {want} but the example records "
                    f"{ratio['value']}")
    return errs


# --------------------------------------------------------------------------
# S9: the legal unit cap is a separate figure
# --------------------------------------------------------------------------
def legal_cap_errors(example_id: str, data: dict) -> list[str]:
    errs: list[str] = []
    cap = data["legal_unit_cap"]
    if set(cap) != lib.LEGAL_CAP_KEYS:
        return [f"{example_id}: legal_unit_cap keys differ from the fixed set"]
    if str(cap["factor"]) != "680":
        errs.append(f"{example_id}: the dwelling-unit factor should be 680 (ZR 23-52)")
    units = lib.legal_unit_cap_units(cap)
    if int(cap["units_cap"]) != units:
        errs.append(f"{example_id}: the legal unit cap recomputes to {units} but the example "
                    f"records {cap['units_cap']}")
    note = str(cap["note"]).lower()
    if "separate" not in note and "not derived" not in note:
        errs.append(f"{example_id}: the legal cap note must say it is a separate figure, not "
                    "derived from the physical estimate")
    errs += citation_errors(example_id, "legal_unit_cap", cap["citations"])
    return errs


# --------------------------------------------------------------------------
# top-level validate
# --------------------------------------------------------------------------
def validate_example(example_id: str, data: dict) -> list[str]:
    errs: list[str] = []
    errs += program_result_errors(example_id, data)
    errs += structure_errors(example_id, data)
    if errs:
        return errs  # deeper checks assume the fixed shape
    errs += change_log_errors(example_id, data)
    ids = [c["component_id"] for c in data["components"]]
    if len(ids) != len(set(ids)):
        errs.append(f"{example_id}: duplicate component ids")
    for comp in data["components"]:
        shape = component_shape_errors(example_id, comp)
        errs += shape
        if not shape:
            errs += arithmetic_errors(example_id, comp)
    if not errs:
        errs += reconciliation_errors(example_id, data)
        errs += legal_cap_errors(example_id, data)
        errs += fit.fit_errors(example_id, data)  # M5-T133: every floor must fit
    return errs


def validate_all() -> list[str]:
    errs: list[str] = []
    for example_id in lib.EXAMPLE_IDS:
        path = lib.example_path(example_id)
        if not path.is_file():
            errs.append(f"example data file missing: {path.name}")
            continue
        errs += validate_example(example_id, lib.load_example(example_id))
    errs += record_errors()
    return errs


# --------------------------------------------------------------------------
# S1/S7/S10: the record states the definitions, the ratio and the open points
# --------------------------------------------------------------------------
def record_errors() -> list[str]:
    errs: list[str] = []
    if not lib.RECORD_PATH.is_file():
        return [f"MEASUREMENT_BASIS.md is missing under {lib.DOCS_DIR}"]
    text = lib.RECORD_PATH.read_text()
    low = text.lower()
    required = [
        ("not professionally reviewed", "it is a draft AI reading, not professionally reviewed"),
        ("floor area", "the ZR 12-10 floor-area definition"),
        ("23-23", "the conditional allowances of ZR 23-23"),
        ("unit area calculation", "HPD's UNIT AREA CALCULATION subsection"),
        ("mechanical and plumbing chases", "the precise HPD term mechanical and plumbing chases"),
        ("deducted twice", "that nothing is deducted twice"),
        ("not known", "what stays not known without a layout"),
        ("700", "that 700 sq ft stays an unapproved assumption"),
        ("25", "that 25 percent stays an unapproved assumption"),
        ("open points", "the open points for the owner"),
        ("legal unit", "that the legal unit cap stays separate"),
        ("total hpd-measured dwelling-unit area", "the ratio's exact definition"),
        # M5-T133 C1 to C7
        ("apartment-area ratio", "the estimate's formula in words (C1)"),
        ("maximum permitted floor area", "that the maximum permitted floor area stays apart (C1)"),
        ("sensitivity range", "that 0.60 to 0.75 is only a chosen sensitivity range (C2)"),
        ("23-20", "the shared-floor-area attribution of ZR 23-20 (C3)"),
        ("shared by multiple uses", "the ZR 23-20 shared-floor-area sentence (C3)"),
        ("not captured yet", "what is not captured yet (C3, C5)"),
        ("fully electrified", "the energy exclusion's definitions, not captured yet (C5)"),
        ("ultra low energy", "the energy exclusion's definitions, not captured yet (C5)"),
        ("23-432", "the R6B base/building height table for unequal floors (C6)"),
        ("23-433", "the setback provision for unequal floors (C6)"),
        ("choices for the owner", "section 8's first list, the owner's choices (C7)"),
        ("questions of law", "section 8's second list, the questions of law (C7)"),
        ("preliminary capacity estimate", "the name for the result once a shape exists (C7)"),
    ]
    for needle, what in required:
        if needle not in low:
            errs.append(f"MEASUREMENT_BASIS.md does not state: {what}")
    # S1: definitions come before the ratio formula.
    ratio_at = low.find("total hpd-measured dwelling-unit area")
    def_at = low.find("floor area")
    if 0 <= ratio_at < def_at:
        errs.append("MEASUREMENT_BASIS.md states the ratio before the definitions (S1)")
    for example_id in lib.EXAMPLE_IDS:
        if example_id not in text:
            errs.append(f"MEASUREMENT_BASIS.md does not list the example {example_id!r}")
    return errs
