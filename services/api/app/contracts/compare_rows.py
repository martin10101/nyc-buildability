"""Compare backend: the identical row set for any two options of one study
(task C-09, plan docs/PRODUCT_PLAN_CURRENT_2026-09-28.md M1-18 'Compare options
side by side ... Identical rows; plans at a common scale'; directive D-090;
feeds Lane D's D-10).

Pure, offline, library-only (no route in this slice; the route and the UI are
later). :func:`build_compare_rows` takes the per-option results-v1 documents of
ONE study at ONE revision and returns a validated ``compare_rows`` v1 document:
the SAME ordered metric rows for every option, each row carrying exactly one cell
per option, plus a ``common_scale`` block for the lot plans and the A-05 duplicate
record(s) for options that are identical.

HARD BOUNDARIES (also what the tests pin):

- The ONLY numbers this module computes are the plan SCALE EXTENTS (each option's
  lot-outline bounding-box width and height, and their per-dimension maximum). Every
  ROW value is a STRAIGHT COPY out of the results document. No legal value is
  recomputed; no number carries a caution label.
- Every metric row is present for every option, and every cell is available (a value)
  or not_available (the results document's OWN reason and reason_kind, copied
  verbatim) - never missing, never blank, never a value or a sentence invented here
  (plan section 5 'Not available - reason').
- Fail closed (a typed :class:`CompareRowsError`, EvaluatorInputs-style) on: fewer than
  two options; a results document from a different study or revision; a repeated
  option_id; an 'available' answer that is missing the headline metric this row reads
  (a structural defect in the input, surfaced, never papered over); a duplicate record
  naming an option that is not in the comparison.

A-05 DUPLICATE RECORD. The 'merge or explain' record that marks two options identical
is A-05's (plan A-05 'No duplicate options (merge or explain)'); A-05 lives in
app.scenario.three_answers and owns the identity key. At the C-09 integration head that
module is NOT yet in the tree (docs/lanes/RECONCILIATION.md: 'No merge-or-explain'), so
per the task's named fallback the record is carried as an OPAQUE dict produced by the
CALLER: :func:`build_compare_rows` takes ``duplicate_records`` (default none), validates
only that each names option_ids present in the comparison, and carries each through
verbatim. When A-05 lands, its records drop straight in; this module never recomputes the
identity. (The Lane C -> Lane A import boundary itself is open - evaluator_inputs.py C-07
already imports app.scenario.three_answers read-only - so the fallback is forced by A-05's
absence, not by a layering rule.)
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from app.contracts.study_contracts import (
    validate_compare_rows_document,
    validate_results_document,
)

__all__ = [
    "CONTRACT_VERSION",
    "CompareRowsError",
    "ROW_CATALOGUE",
    "build_compare_rows",
]

CONTRACT_VERSION = "1.0.0"

# The status-strip chip separator the plan itself uses (section 5a item 1 example
# 'Zoning maximum · approximate measurements · lots you selected'). The status
# row joins the chip texts with it verbatim - no text is invented.
_STATUS_SEPARATOR = " · "


class CompareRowsError(Exception):
    """A set of results documents could not be turned into a valid comparison table.
    Raised server-side: an ambiguous or incoherent comparison is surfaced, never
    guessed (CLAUDE.md principle 3, fail closed; principle 4, conflicts stay visible)."""


# ---------------------------------------------------------------------------
# Cell builders. Each reads ONE metric out of a results document and returns a
# compare_rows cell: an available cell (a straight copy of the value) or the
# results document's own not_available block, copied verbatim.
# ---------------------------------------------------------------------------


def _not_available_copy(block: Mapping[str, Any]) -> dict:
    """A results not_available block copied verbatim as a cell (never reworded)."""
    return {
        "status": "not_available",
        "reason": block["reason"],
        "reason_kind": block["reason_kind"],
    }


def _available_cell(
    *,
    value: Any,
    unit: str | None,
    label: str,
    measurement: Mapping[str, str] | None = None,
    zr_sections: Sequence[str] | None = None,
    sources: Sequence[Mapping[str, Any]] | None = None,
    note: str | None = None,
) -> dict:
    """An available cell with only the fields the source actually carried (so an
    additional-properties-closed contract validates)."""
    cell: dict[str, Any] = {
        "status": "available",
        "value": value,
        "unit": unit,
        "label": label,
    }
    if measurement is not None:
        cell["measurement"] = dict(measurement)
    if zr_sections is not None:
        cell["zr_sections"] = list(zr_sections)
    if sources is not None:
        cell["sources"] = [dict(source) for source in sources]
    if note is not None:
        cell["note"] = note
    return cell


def _answer_value(answer: Mapping[str, Any], value_key: str) -> dict | None:
    """The answer value with ``value_key`` from an available answer, or None."""
    for value in answer["values"]:
        if value["key"] == value_key:
            return value
    return None


def _answer_value_cell(results: Mapping[str, Any], answer_key: str, value_key: str) -> dict:
    """Cell for one value of one of the three answers (results.answers[answer_key]).
    A not_available answer carries its reason; an available answer contributes the
    named value with its unit, label, measurement, Zoning Resolution sections and
    sources. An available answer missing ``value_key`` is a structural defect in the
    input and is raised, never papered over with an invented cell."""
    answer = results["answers"][answer_key]
    if answer["status"] == "not_available":
        return _not_available_copy(answer)
    value = _answer_value(answer, value_key)
    if value is None:
        raise CompareRowsError(
            f"results {results['results_id']!r} answer {answer_key!r} is available but "
            f"carries no {value_key!r} value; the comparison never invents a cell."
        )
    return _available_cell(
        value=value["value"],
        unit=value["unit"],
        label=value["label"],
        measurement=answer.get("measurement"),
        zr_sections=value["zr_sections"],
        sources=value["sources"],
    )


def _shortfall_cell(results: Mapping[str, Any]) -> dict:
    """Cell for the shortfall. 'none' is the honest 0 sq ft (the option reaches the
    allowance); 'shortfall' carries its sq_ft; not_available carries its reason."""
    shortfall = results["shortfall"]
    status = shortfall["status"]
    if status == "none":
        return _available_cell(value=0.0, unit="square_feet", label="Shortfall")
    if status == "shortfall":
        return _available_cell(
            value=shortfall["sq_ft"], unit="square_feet", label="Shortfall"
        )
    return _not_available_copy(shortfall)


def _unit_estimate_cell(results: Mapping[str, Any]) -> dict:
    estimate = results["unit_estimate"]
    if estimate["status"] == "not_available":
        return _not_available_copy(estimate)
    return _available_cell(
        value=estimate["value"],
        unit="dwelling_units",
        label="Dwelling-unit estimate",
        zr_sections=estimate["zr_sections"],
    )


def _floors_fit_cell(results: Mapping[str, Any]) -> dict:
    stack = results["floor_stack"]
    if stack["status"] == "not_available":
        return _not_available_copy(stack)
    return _available_cell(
        value=stack["floors_fit"],
        unit="stories",
        label="Floors that fit under the height limit",
        zr_sections=stack["zr_sections"],
    )


def _floor_to_floor_cell(results: Mapping[str, Any]) -> dict:
    """Cell for the floor-to-floor height assumption. A straight copy of the floor-to-
    floor shared by the floor-stack levels; when levels disagree (per-floor overrides)
    the most common value is taken (ties -> the smallest value), so the cell is always
    one existing level value, never an average."""
    stack = results["floor_stack"]
    if stack["status"] == "not_available":
        return _not_available_copy(stack)
    heights = [level["floor_to_floor_ft"] for level in stack["levels"]]
    typical = max(sorted(set(heights)), key=lambda h: (heights.count(h), -h))
    return _available_cell(
        value=typical, unit="feet", label="Floor-to-floor height (assumed)"
    )


def _status_cell(results: Mapping[str, Any]) -> dict:
    """Cell for the status strip: the chip texts joined with the plan's own separator.
    The strip is required and non-empty in the results contract, so this is always
    available."""
    texts = [item["text"] for item in results["status_strip"]]
    return _available_cell(
        value=_STATUS_SEPARATOR.join(texts), unit=None, label="Status"
    )


def _out_of_date_cell(results: Mapping[str, Any]) -> dict:
    """Cell for the out-of-date flag: the boolean itself, with the results document's
    own out_of_date_reason carried as the note (null when current)."""
    return _available_cell(
        value=results["out_of_date"],
        unit=None,
        label="Out of date",
        note=results["out_of_date_reason"],
    )


# The fixed row catalogue, in display order. Each entry: (key, label, cell builder).
# Keys and sources are documented in the C-09 producer report.
ROW_CATALOGUE: tuple[tuple[str, str, Any], ...] = (
    (
        "floor_area_allowance",
        "Floor-area allowance (residential)",
        lambda r: _answer_value_cell(r, "floor_area_allowance", "max_residential_floor_area"),
    ),
    (
        "permitted_building_height",
        "Permitted building height",
        lambda r: _answer_value_cell(r, "permitted_envelope", "max_building_height"),
    ),
    (
        "building_option_floor_area",
        "Building-option floor area",
        lambda r: _answer_value_cell(r, "building_option", "achieved_zoning_floor_area"),
    ),
    (
        "building_option_floors",
        "Building-option floors",
        lambda r: _answer_value_cell(r, "building_option", "building_floors"),
    ),
    ("shortfall", "Shortfall vs allowance", _shortfall_cell),
    ("unit_estimate", "Dwelling-unit estimate", _unit_estimate_cell),
    ("floors_fit", "Floors that fit under the height limit", _floors_fit_cell),
    ("floor_to_floor_ft", "Floor-to-floor height (assumed)", _floor_to_floor_cell),
    ("status", "Status", _status_cell),
    ("out_of_date", "Out of date", _out_of_date_cell),
)


# ---------------------------------------------------------------------------
# Common scale (the only numbers the comparison itself computes: extents).
# ---------------------------------------------------------------------------


def _lot_extent(geometry: Mapping[str, Any]) -> tuple[float, float]:
    """The lot-outline bounding-box width and height, in feet. The lot outline is always
    present on available geometry (results contract), so this is defined whenever geometry
    is available."""
    xs: list[float] = []
    ys: list[float] = []
    for ring in geometry["lot_outline"]:
        for x, y in ring:
            xs.append(x)
            ys.append(y)
    return (max(xs) - min(xs), max(ys) - min(ys))


def _common_scale(options: Sequence[Mapping[str, Any]], results_by_option: dict) -> dict:
    """The one scale at which every option's lot plan fits. not_available (with the first
    offending option's reason_kind) when ANY option's geometry is not_available."""
    per_option: list[dict] = []
    for option in options:
        option_id = option["option_id"]
        geometry = results_by_option[option_id]["geometry"]
        if geometry["status"] == "not_available":
            return {
                "status": "not_available",
                "reason": (
                    f"Option {option_id!r} has no geometry "
                    f"({geometry['reason']}); a common scale needs every option's lot plan."
                ),
                "reason_kind": geometry["reason_kind"],
            }
        width_ft, height_ft = _lot_extent(geometry)
        per_option.append(
            {
                "option_id": option_id,
                "crs": geometry["crs"],
                "width_ft": width_ft,
                "height_ft": height_ft,
            }
        )
    return {
        "status": "available",
        "units": "feet",
        "fits_extent": {
            "width_ft": max(entry["width_ft"] for entry in per_option),
            "height_ft": max(entry["height_ft"] for entry in per_option),
        },
        "per_option": per_option,
    }


# ---------------------------------------------------------------------------
# Public builder.
# ---------------------------------------------------------------------------


def build_compare_rows(
    results_documents: Sequence[Mapping[str, Any]],
    *,
    study_id: str,
    revision: int,
    duplicate_records: Sequence[Mapping[str, Any]] = (),
) -> dict:
    """Build and validate the compare_rows v1 document for the options of ONE study.

    ``results_documents`` are the per-option results-v1 documents, in the order the
    columns should appear. Each is re-validated against the results contract (fail
    closed). Every document must declare ``study_id`` and ``revision``; a document from
    another study or revision, a repeated option_id, or fewer than two documents raises
    :class:`CompareRowsError`. ``duplicate_records`` are A-05 'merge or explain' records
    produced by the caller (opaque; default none): each must name option_ids that are all
    in the comparison, and is carried through verbatim.

    Rows are emitted in the fixed :data:`ROW_CATALOGUE` order; options (and every row's
    cells) follow the caller's order. The output is validated against the compare_rows
    contract before it is returned."""
    if len(results_documents) < 2:
        raise CompareRowsError(
            f"a comparison needs at least two options; got {len(results_documents)}."
        )

    options: list[dict] = []
    results_by_option: dict[str, Mapping[str, Any]] = {}
    for results in results_documents:
        validate_results_document(results)
        if results["study_id"] != study_id:
            raise CompareRowsError(
                f"results {results['results_id']!r} is for study "
                f"{results['study_id']!r}, not {study_id!r}; a comparison is within one study."
            )
        if results["revision"] != revision:
            raise CompareRowsError(
                f"results {results['results_id']!r} is for revision {results['revision']}, "
                f"not {revision}; a comparison is within one revision."
            )
        option_id = results["option_id"]
        if option_id in results_by_option:
            raise CompareRowsError(
                f"option {option_id!r} appears more than once; each option is one column."
            )
        results_by_option[option_id] = results
        options.append(
            {
                "option_id": option_id,
                "revision": results["revision"],
                "results_id": results["results_id"],
                "computed_at": results["computed_at"],
            }
        )

    rows: list[dict] = []
    for order, (key, label, build_cell) in enumerate(ROW_CATALOGUE):
        rows.append(
            {
                "key": key,
                "label": label,
                "catalogue_order": order,
                "cells": [build_cell(results_by_option[option["option_id"]]) for option in options],
            }
        )

    known_option_ids = set(results_by_option)
    duplicates: list[dict] = []
    for record in duplicate_records:
        if "option_ids" not in record:
            raise CompareRowsError(
                "a duplicate record must name the option_ids it ties together."
            )
        missing = [oid for oid in record["option_ids"] if oid not in known_option_ids]
        if missing:
            raise CompareRowsError(
                f"duplicate record names option(s) {missing} that are not in this "
                "comparison; it cannot be tied to a column."
            )
        duplicates.append(dict(record))

    document = {
        "contract_version": CONTRACT_VERSION,
        "study_id": study_id,
        "revision": revision,
        "options": options,
        "rows": rows,
        "common_scale": _common_scale(options, results_by_option),
        "duplicates": duplicates,
    }
    validate_compare_rows_document(document)
    return document
