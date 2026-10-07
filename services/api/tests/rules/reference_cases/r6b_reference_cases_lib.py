#!/usr/bin/env python3
"""Shared library for the R6B reference cases (work-order step R0; M4-T024).

Test support, NOT program code. It loads the authored case data files, recomputes
their arithmetic with exact decimal arithmetic, and offers a tiny loader that
later [LAW] tests use to read a row's expected value by its id. It imports
NOTHING from the rule engine, the scenario engine or any program output: a
reference case must never carry a value that came from a program run, and this
library must never fetch one. Pure stdlib.

Layout it knows about::

    docs/reference-cases/R6B/README.md           overview (hand-written)
    docs/reference-cases/R6B/cases/<case>.json   the four authored data files
    docs/reference-cases/R6B/<case>.md           one page per case (rendered)
    docs/reference-cases/R6B/provenance/         the helper's two returns, unchanged

The arithmetic engine (:func:`compute_step`, :func:`recompute_row_errors`) is the
only place a number is recomputed; the checker and the test call it so a changed
operand is caught and names its row.
"""
from __future__ import annotations

import json
import pathlib
from decimal import ROUND_HALF_UP, Decimal

HERE = pathlib.Path(__file__).resolve().parent
# reference_cases / rules / tests / api / services / <repo root>
REPO_ROOT = HERE.parents[4]
DOCS_DIR = REPO_ROOT / "docs" / "reference-cases" / "R6B"
CASES_DIR = DOCS_DIR / "cases"
PROVENANCE_DIR = DOCS_DIR / "provenance"
SNAPSHOT_DIR = REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1"

# The cases, by the file stem of their data file and rendered page. The fifth
# case (step-p1-worked) holds the rows worked from the step-P1 captures (M4-T027).
CASE_IDS = ("real-lot", "interior-lots", "corner-reach", "suffix", "step-p1-worked")

# The base ids every one of the work order's table rows must appear under (S1).
# A base id is "present" when a row's id equals it or starts with it + "-".
REQUIRED_BASE_IDS = {
    "real-lot": [f"L{i}" for i in range(1, 16)],
    "interior-lots": ["P1", "P3", "P4", "P5", "interior-coverage"],
    "corner-reach": ["real-lot", "C1", "C2", "C3"],
    "suffix": ["23-362", "23-52", "23-344", "23-22", "23-432"],
    "step-p1-worked": [
        "lot-area", "corner-100x100", "corner-150x100", "corner-200x120",
        "interior-40x100", "through-40x200", "special-density",
    ],
}

EXPECTED_KINDS = ("value", "not_known")
CITATION_KINDS = ("captured", "not_captured")
OPERATIONS = ("multiply", "divide", "subtract", "hypotenuse")
ROUNDINGS = ("none", "dwelling_unit_three_quarters", "round_half_up_2dp")

# Fixed key sets (strict, like the review-register pattern: a stray or missing
# field is a defect, not a silent pass).
CASE_KEYS = {
    "case_id", "title", "work_order_table", "summary", "what_it_is_worth",
    "what_it_does_not_establish", "prepared_by", "checked_by", "sources",
    "facts", "change_log", "rows",
}
ROW_KEYS = {
    "row_id", "quantity", "facts_used", "citations", "why_applies",
    "arithmetic", "expected", "source_reference", "does_not_establish",
}
EXPECTED_KEYS = {"kind", "value", "unit", "reason"}
CITATION_KEYS = {
    "kind", "section", "title", "quote", "snapshot_id", "snapshot_file",
    "content_digest", "official_url", "captured_on", "last_amended",
    "date_read", "status_note", "table_assertion",
}
FACT_KEYS = {"name", "value", "source"}
ARITH_KEYS = {"label", "operands", "operation", "rounding", "result"}
OPERAND_KEYS = {"name", "value"}
CHANGE_LOG_KEYS = {"date", "summary", "by"}


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------
def case_path(case_id: str) -> pathlib.Path:
    return CASES_DIR / f"{case_id}.json"


def page_path(case_id: str) -> pathlib.Path:
    return DOCS_DIR / f"{case_id}.md"


def load_case(case_id: str) -> dict:
    """Load one authored case data file."""
    return json.loads(case_path(case_id).read_text())


def load_all() -> dict[str, dict]:
    return {cid: load_case(cid) for cid in CASE_IDS}


def iter_rows():
    """Yield (case_id, row) for every row of every case."""
    for cid in CASE_IDS:
        for row in load_case(cid)["rows"]:
            yield cid, row


# --------------------------------------------------------------------------
# the loader later [LAW] tests use (S11)
# --------------------------------------------------------------------------
class RowNotFound(KeyError):
    """Raised when a reference-case row is asked for by an id that does not exist."""


def find_row_or_none(case_id: str, row_id: str) -> dict | None:
    """Return the full row dict for an id, or None. Used by the mutation tests,
    which deep-copy the row before changing it (no committed file is touched)."""
    for row in load_case(case_id)["rows"]:
        if row["row_id"] == row_id:
            return row
    return None


def load_row(case_id: str, row_id: str) -> dict:
    """Return a row's expected value, its kind and its source reference, by id.

    A later [LAW] test asks for ``load_row("real-lot", "L1")`` and reads the
    expected value and kind from it; it never reads a program run. Asking for a
    row (or a case) that does not exist fails loudly with :class:`RowNotFound`.
    """
    if case_id not in CASE_IDS:
        raise RowNotFound(f"no reference case {case_id!r} (have: {', '.join(CASE_IDS)})")
    for row in load_case(case_id)["rows"]:
        if row["row_id"] == row_id:
            exp = row["expected"]
            return {
                "case_id": case_id,
                "row_id": row_id,
                "quantity": row["quantity"],
                "kind": exp["kind"],
                "value": exp["value"],
                "unit": exp["unit"],
                "reason": exp["reason"],
                "source_reference": row["source_reference"],
            }
    raise RowNotFound(f"no row {row_id!r} in reference case {case_id!r}")


# --------------------------------------------------------------------------
# the arithmetic engine (exact decimal; the only place a number is recomputed)
# --------------------------------------------------------------------------
def _operand_values(step: dict) -> list[Decimal]:
    return [Decimal(str(op["value"])) for op in step["operands"]]


def dwelling_units(floor_area: Decimal, factor: Decimal = Decimal("680")) -> int:
    """ZR 23-52: divide the floor area by the factor; a fraction equal to or
    greater than three-quarters counts as one dwelling unit, otherwise it is
    dropped."""
    quotient = floor_area / factor
    whole = int(quotient)  # floor for a positive quotient
    fraction = quotient - whole
    return whole + (1 if fraction >= Decimal("0.75") else 0)


def compute_step(step: dict) -> Decimal:
    """Recompute one arithmetic step from its operands, operation and rounding.

    Returns a :class:`~decimal.Decimal`. Raises ``ValueError`` on an unknown
    operation or rounding so a malformed step can never pass silently.
    """
    operation = step["operation"]
    rounding = step["rounding"]
    values = _operand_values(step)
    if operation == "multiply":
        raw = values[0]
        for value in values[1:]:
            raw *= value
    elif operation == "subtract":
        raw = values[0] - values[1]
    elif operation == "divide":
        raw = values[0] / values[1]
    elif operation == "hypotenuse":
        raw = (values[0] ** 2 + values[1] ** 2).sqrt()
    else:
        raise ValueError(f"unknown operation {operation!r}")

    if rounding == "none":
        return raw
    if rounding == "dwelling_unit_three_quarters":
        return Decimal(dwelling_units(values[0], values[1]))
    if rounding == "round_half_up_2dp":
        return raw.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    raise ValueError(f"unknown rounding {rounding!r}")


def raw_quotient(step: dict) -> Decimal:
    """The un-rounded quotient of a divide step, for display only."""
    values = _operand_values(step)
    return values[0] / values[1]


def recompute_row_errors(case_id: str, row: dict) -> list[str]:
    """Recompute every arithmetic step of a row and compare with the recorded
    result. The last step's result must equal the row's numeric expected value
    (when that value is numeric). Each message names the case and the row so a
    changed operand is caught and attributed."""
    errs: list[str] = []
    rid = row.get("row_id", "?")
    steps = row.get("arithmetic", [])
    for index, step in enumerate(steps, start=1):
        try:
            got = compute_step(step)
        except (ValueError, ArithmeticError, KeyError) as exc:
            errs.append(f"{case_id}/{rid}: arithmetic step {index} did not compute: {exc}")
            continue
        recorded = Decimal(str(step["result"]))
        if got != recorded:
            errs.append(
                f"{case_id}/{rid}: arithmetic step {index} ({step.get('label', '')!r}) "
                f"recomputes to {got} but the case records {recorded}"
            )
    # A numeric expected value must equal the last step's recorded result.
    exp = row.get("expected", {})
    if exp.get("kind") == "value" and steps:
        number = _as_decimal(exp.get("value"))
        if number is not None:
            last = Decimal(str(steps[-1]["result"]))
            if number != last:
                errs.append(
                    f"{case_id}/{rid}: expected value {exp['value']} does not equal the last "
                    f"arithmetic result {last}"
                )
    return errs


def _as_decimal(value) -> Decimal | None:
    """Return a Decimal if ``value`` is a number (or a plain numeric string),
    else None (a prose value such as 'corner' or '100 percent')."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    if isinstance(value, str):
        try:
            return Decimal(value)
        except Exception:  # noqa: BLE001 - a non-numeric string is expected here
            return None
    return None


def is_numeric_value(value) -> bool:
    return _as_decimal(value) is not None
