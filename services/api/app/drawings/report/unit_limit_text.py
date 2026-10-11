"""The report's legal dwelling-unit limit wording (M5-T162).

Holds the "Legal apartment limit" open item and the data behind the "Legal unit
limits" coverage line, built from the results document: each withheld limit is
named by its program as not known, and a shown limit is called a conditional
ceiling for its program ONLY when the value's own state is conditional, otherwise
it is named plainly. ``readers.py`` stays a general document reader and wires this
module into its open-items list.

This module reads the document through ``readers`` primitives (``present_values``,
``withheld_values``, ``answer_block``, ``ANSWER_NAMES``). Those are imported inside
the functions that use them so there is no import cycle: ``readers`` imports this
module at module load, while this module reaches back into ``readers`` only at call
time (both modules are fully loaded by then).
"""

from __future__ import annotations

from collections.abc import Mapping

__all__ = [
    "legal_unit_limit_item",
    "shown_legal_unit_limit_programs",
    "shown_legal_unit_limits",
]

# The one plain sentence shown when NO legal dwelling-unit limit is shown.
NO_LIMIT_SENTENCE = "No legal apartment limit is shown."

# "Legal dwelling-unit limit, <program>…" is the shape of every legal dwelling-unit limit's own
# label; the program (e.g. "standard residences", "qualifying senior housing") is read from it.
_LIMIT_LABEL_PREFIX = "Legal dwelling-unit limit, "


def _limit_program(label: object) -> str | None:
    """The program a legal dwelling-unit limit is for, read from its own label
    (``"Legal dwelling-unit limit, <program>…"``) and cut before the derivation
    or number part. ``None`` when the label is absent or not in that form, so no
    program is invented for a malformed value."""
    text = str(label or "")
    if not text.startswith(_LIMIT_LABEL_PREFIX):
        return None
    rest = text[len(_LIMIT_LABEL_PREFIX):]
    for separator in (":", "("):
        index = rest.find(separator)
        if index != -1:
            rest = rest[:index]
    rest = rest.strip()
    return rest or None


def _join_programs(programs: list[str], conjunction: str) -> str:
    """Join program names as plain English: ``"a"``, ``"a or b"``, ``"a, b or c"``."""
    names = [name for name in programs if name]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + f" {conjunction} " + names[-1]


def _as_label(program: str | None, fallback: str) -> str:
    """A program as a sentence-leading label (first letter capitalised), or the
    fallback when no program could be read from the value's label."""
    if not program:
        return fallback
    return program[:1].upper() + program[1:]


def shown_legal_unit_limits(results: Mapping) -> list[dict]:
    """Each shown legal dwelling-unit limit as ``{"program", "conditional"}``, read
    only from values actually present in an answer's shown values (never a
    truthiness test on an optional block). ``conditional`` is True only when the
    value's own state (``value_states[<key>].way``) is ``"conditional"``; an
    absent, malformed or other state is not conditional, so no state is invented.
    Empty when none is shown, which includes an absent or malformed answer block."""
    from . import readers

    rows: list[dict] = []
    for name in readers.ANSWER_NAMES:
        block = readers.answer_block(results, name)
        states = block.get("value_states")
        states = states if isinstance(states, Mapping) else {}
        for row in readers.present_values(block):
            key = str(row.get("key") or "")
            program = _limit_program(row.get("label")) if "legal_unit_limit" in key else None
            if not program:
                continue
            state = states.get(key)
            way = state.get("way") if isinstance(state, Mapping) else None
            rows.append({"program": program, "conditional": way == "conditional"})
    return rows


def shown_legal_unit_limit_programs(results: Mapping) -> list[str]:
    """The program names of the shown legal dwelling-unit limits, in document order
    (see ``shown_legal_unit_limits`` for each limit's own conditional state)."""
    out: list[str] = []
    for row in shown_legal_unit_limits(results):
        if row["program"] not in out:
            out.append(row["program"])
    return out


def _withheld_legal_unit_limits(results: Mapping) -> list[dict]:
    """The withheld legal dwelling-unit limit rows across the answers, in document
    order."""
    from . import readers

    rows: list[dict] = []
    for name in readers.ANSWER_NAMES:
        for row in readers.withheld_values(readers.answer_block(results, name)):
            if "legal_unit_limit" in str(row.get("key") or ""):
                rows.append(row)
    return rows


def legal_unit_limit_item(results: Mapping) -> dict | None:
    """The 'Legal apartment limit' open item, built from the document: each
    withheld limit named by its program as not known; a shown limit called a
    conditional ceiling for its program only when its own state is conditional,
    else shown plainly (the number stays on the derivation table); the reason and
    resolver kept per program. ``NO_LIMIT_SENTENCE`` only when none is shown.
    ``None`` when none is withheld (no item)."""
    withheld = _withheld_legal_unit_limits(results)
    if not withheld:
        return None
    shown = shown_legal_unit_limits(results)
    conditional = [row["program"] for row in shown if row["conditional"]]
    plain = [row["program"] for row in shown if not row["conditional"]]
    withheld_programs = [_limit_program(row.get("label")) or row.get("label") for row in withheld]
    withheld_programs = [str(p) for p in withheld_programs if p]
    if shown:
        clauses: list[str] = []
        if conditional:
            clauses.append(
                "shown as a conditional ceiling for " + _join_programs(conditional, "and")
            )
        if plain:
            clauses.append("shown for " + _join_programs(plain, "and"))
        effect = "The legal apartment limit is " + " and is ".join(clauses)
        if withheld_programs:
            effect += "; it is not known for " + _join_programs(withheld_programs, "or")
        effect += "."
    else:
        effect = NO_LIMIT_SENTENCE
    reason_parts: list[str] = []
    resolve_parts: list[str] = []
    for row in withheld:
        label = _as_label(_limit_program(row.get("label")), "A legal dwelling-unit limit")
        reason = str(row.get("reason") or "").strip()
        resolver = str(row.get("resolved_by") or "").strip()
        reason_parts.append(f"{label}: {reason}" if reason else label)
        if resolver:
            resolve_parts.append(f"{label}: {resolver}")
    return {
        "category": "legal_unit_limit",
        "title": "Legal apartment limit",
        "effect": effect,
        "reason": " ".join(reason_parts),
        "resolves": " ".join(resolve_parts) or None,
        "status_label": withheld[0]["status_label"],
    }
