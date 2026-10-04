"""Map the engine's COMPUTED building-option notes into the results contract's
``building_option_note`` shape, and name the version the populated slot binds (task
D-090-R132; results contract 1.2.0).

The building option carries its minimum-base-height note on the engine object
(:attr:`BuildingOptionResult.compliance_notes`) in a note shape that is close to, but not
identical with, the results schema's ``building_option_note``:

- the engine note's ``values`` is a LIST of ``{name, value, unit}`` records; the contract's
  ``values`` is an OBJECT keyed by name (the face reads the numbers by name, never a typed
  figure), so this module RESHAPES the array into that object (dropping the display ``unit``,
  which is not part of the contract note);
- the engine note carries no ``kind`` and no ``register``; this module supplies both. The
  ``register`` is the schema's fixed draft-register const - the not-free guard that keeps the
  text a DRAFT reading pending qualified review (CLAUDE.md principle 1; D-090-R010/R118). The
  ``kind`` is the single closed-enum value :data:`MINIMUM_BASE_HEIGHT_KIND`: the engine's
  :func:`compliance_notes` emits exactly the minimum-base-height note (its docstring and the
  closed schema enum), so every note it produces is that one kind. A new engine note kind is
  an append-only contract change that must extend BOTH the schema enum and this mapper.

``text``, ``computed_from``, ``zr_sections``, ``snapshot_ids`` and ``draft`` are carried
through unchanged - the note text, the sections and the pinned snapshots are exactly the
engine's computed values, never restated here (C-11).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

# The fixed draft-register string, byte-exact with the results schema's
# building_option_note.register const (D-090-R118). Together with draft=True it marks the note
# a draft reading of the captured text pending qualified review, never a legal determination.
BUILDING_OPTION_NOTE_REGISTER = "draft reading of the captured text"

# The single closed-enum note kind the engine emits (results schema building_option_note.kind).
MINIMUM_BASE_HEIGHT_KIND = "minimum_base_height"

# A non-empty building-option notes array binds this results contract version (D-090-R132).
RESULTS_CONTRACT_VERSION_WITH_NOTES = "1.2.0"


def _map_note(note: Mapping) -> dict:
    """One engine note -> the contract ``building_option_note`` shape."""
    return {
        "text": note["text"],
        "kind": MINIMUM_BASE_HEIGHT_KIND,
        "computed_from": list(note["computed_from"]),
        "values": {entry["name"]: entry["value"] for entry in note["values"]},
        "zr_sections": list(note["zr_sections"]),
        "snapshot_ids": list(note["snapshot_ids"]),
        "draft": note["draft"],
        "register": BUILDING_OPTION_NOTE_REGISTER,
    }


def map_building_option_notes(engine_notes: Sequence[Mapping]) -> list[dict]:
    """Map the engine's computed building-option notes into the contract note shape.

    Returns a list in the engine's order. An empty input yields an empty list, so the caller
    leaves the optional ``notes`` slot off entirely (keeping the 1.0.0/1.1.0 output
    byte-identical) and never bumps the version."""
    return [_map_note(note) for note in engine_notes]
