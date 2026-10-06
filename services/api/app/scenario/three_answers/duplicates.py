"""C-6: no duplicate options - merge or explain (task A-05; competitor-review check C-6;
directive D-090).

Slice 1 emits ONE results-v1 option per ``generate_results`` call, so duplicates arise ACROSS
the options of one study, never inside a single document. This module is pure: it takes the
emitted results-v1 documents and decides, for any set of options, whether they produce the
SAME building (merge) or DIFFERENT buildings (explain the computed difference, named by field
and value - never a template sentence).

Option identity is the building that RESULTS, not the plumbing: the three answers' values, the
floor stack, the floor-by-floor table, the geometry, the unit estimate and the shortfall.
Document identity fields (results_id, study_id, option_id, revision, computed_at, fact ids) and
measurement labels are deliberately excluded - two options are the same option when they build
the same building, whatever they are called or however the site was measured.

No results-contract change: ``merge_or_explain`` returns a plain ``dict`` record. A study/
results slot to persist the record (a merged-into / differs-from field on the option, or a
study-level duplicate report) is a Lane C concern; see the task return for the request.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

_ANSWER_NAMES = ("floor_area_allowance", "permitted_envelope", "building_option")


def _answer_values(document: Mapping[str, Any]) -> dict[str, Any]:
    """The three answers reduced to their computed VALUES (key -> [value, unit]); measurement
    labels and provenance sources are excluded so they never split an otherwise-identical
    building."""
    answers = document.get("answers") or {}
    out: dict[str, Any] = {}
    for name in _ANSWER_NAMES:
        answer = answers.get(name)
        if isinstance(answer, Mapping) and answer.get("status") == "available":
            out[name] = {
                value["key"]: [value.get("value"), value.get("unit")]
                for value in answer.get("values", [])
            }
        elif isinstance(answer, Mapping):
            out[name] = {"status": answer.get("status")}
        else:
            out[name] = None
    return out


def _geometry_shape(geometry: Any) -> Any:
    """The building-shaping parts of the geometry block (outlines, tiers, floor plates, yards,
    setbacks), excluding the measurement label."""
    if not isinstance(geometry, Mapping):
        return None
    if geometry.get("status") != "available":
        return {"status": geometry.get("status")}
    return {
        "lot_outline": geometry.get("lot_outline"),
        "envelope": geometry.get("envelope"),
        "floor_plates": geometry.get("floor_plates"),
        "yards": geometry.get("yards"),
        "setback_lines_per_level": geometry.get("setback_lines_per_level"),
    }


def _unit_fingerprint(unit_estimate: Any) -> Any:
    if not isinstance(unit_estimate, Mapping):
        return None
    if unit_estimate.get("status") != "available":
        return {"status": unit_estimate.get("status")}
    return {
        "value": unit_estimate.get("value"),
        "formula": unit_estimate.get("formula"),
        "factor": unit_estimate.get("factor"),
    }


def _building_fingerprint(document: Mapping[str, Any]) -> dict[str, Any]:
    """The building a results-v1 document produces, with identity/timestamps stripped."""
    return {
        "answer_values": _answer_values(document),
        "floor_by_floor": document.get("floor_by_floor", []),
        "floor_stack": document.get("floor_stack"),
        "geometry": _geometry_shape(document.get("geometry")),
        "unit_estimate": _unit_fingerprint(document.get("unit_estimate")),
        "shortfall": document.get("shortfall"),
    }


def option_identity_key(document: Mapping[str, Any]) -> str:
    """A canonical, hashable identity for the BUILDING ``document`` produces.

    Two options with the same key build the same building and are duplicates; the key ignores
    results/study/option ids, revision, timestamps, provenance and measurement labels."""
    return json.dumps(
        _building_fingerprint(document), sort_keys=True, separators=(",", ":"), default=str
    )


def _option_id(document: Mapping[str, Any]) -> Any:
    return document.get("option_id")


def _named_fields(document: Mapping[str, Any]) -> dict[str, Any]:
    """A flat map of human-named building fields used to EXPLAIN a difference by field and
    value. Only fields present on an available answer/block are included."""
    fields: dict[str, Any] = {}

    stack = document.get("floor_stack")
    if isinstance(stack, Mapping) and stack.get("status") == "available":
        levels = stack.get("levels") or []
        if levels:
            fields["floor_to_floor_ft"] = levels[0].get("floor_to_floor_ft")
        fields["floors_fit"] = stack.get("floors_fit")
        fields["height_limit_ft"] = stack.get("height_limit_ft")

    answers = document.get("answers") or {}
    for name in _ANSWER_NAMES:
        answer = answers.get(name)
        if isinstance(answer, Mapping) and answer.get("status") == "available":
            for value in answer.get("values", []):
                fields[value["key"]] = value.get("value")

    unit_estimate = document.get("unit_estimate")
    if isinstance(unit_estimate, Mapping) and unit_estimate.get("status") == "available":
        fields["dwelling_units"] = unit_estimate.get("value")

    shortfall = document.get("shortfall")
    if isinstance(shortfall, Mapping):
        fields["shortfall_status"] = shortfall.get("status")
        if "sq_ft" in shortfall:
            fields["shortfall_sq_ft"] = shortfall.get("sq_ft")

    geometry = document.get("geometry")
    if isinstance(geometry, Mapping) and geometry.get("status") == "available":
        # A canonical string so a pure lot-shape difference is still named (not dumped inline).
        fields["lot_outline"] = json.dumps(
            geometry.get("lot_outline"), sort_keys=True, separators=(",", ":"), default=str
        )

    return fields


def _compute_differences(group: Sequence[Mapping[str, Any]]) -> list[dict]:
    """For every named building field, the per-option values when they are not all identical.

    Each entry: ``{"field": name, "values": [{"option_id": id, "value": v}, ...]}``. A field
    absent from an option is reported as ``None`` for that option."""
    per_option = [(_option_id(doc), _named_fields(doc)) for doc in group]
    all_fields: list[str] = []
    seen: set[str] = set()
    for _, fields in per_option:
        for name in fields:
            if name not in seen:
                seen.add(name)
                all_fields.append(name)

    differences: list[dict] = []
    for name in all_fields:
        values = [fields.get(name) for _, fields in per_option]
        if len({json.dumps(v, sort_keys=True, default=str) for v in values}) > 1:
            differences.append(
                {
                    "field": name,
                    "values": [
                        {"option_id": option_id, "value": fields.get(name)}
                        for option_id, fields in per_option
                    ],
                }
            )
    return differences


def merge_record(group: Sequence[Mapping[str, Any]], reason: str) -> dict:
    """A merge record: one surviving option, the merged option ids, and the reason."""
    option_ids = [_option_id(doc) for doc in group]
    return {
        "action": "merge",
        "surviving_option_id": option_ids[0],
        "merged_option_ids": option_ids,
        "reason": reason,
    }


def merge_or_explain(group: Sequence[Mapping[str, Any]]) -> dict:
    """Decide whether the options in ``group`` build the same building.

    * Same building (one identity key) -> MERGE: one surviving option id, the merged ids and
      the reason "identical building".
    * Different buildings -> EXPLAIN: the computed differences, each named by field with every
      option's value. Never a template sentence.
    * Different keys but no field difference can be computed -> they are duplicates (MERGE).

    ``group`` must hold at least two documents."""
    if len(group) < 2:
        raise ValueError("merge_or_explain needs at least two options to compare")

    identity_keys = {option_identity_key(doc) for doc in group}
    if len(identity_keys) == 1:
        return merge_record(group, "identical building")

    differences = _compute_differences(group)
    if not differences:
        return merge_record(group, "no computable difference; treated as duplicates")
    return {
        "action": "explain",
        "option_ids": [_option_id(doc) for doc in group],
        "differences": differences,
    }


def find_duplicate_options(
    documents: Sequence[Mapping[str, Any]],
) -> list[list[Mapping[str, Any]]]:
    """Group ``documents`` by building identity and return every group that has more than one
    option (the duplicate clusters), in first-seen order. A study with no duplicates returns
    an empty list; feed each returned group to :func:`merge_or_explain` to get a merge record."""
    groups: dict[str, list[Mapping[str, Any]]] = {}
    order: list[str] = []
    for document in documents:
        key = option_identity_key(document)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(document)
    return [groups[key] for key in order if len(groups[key]) > 1]
