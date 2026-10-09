"""Bridge a study-read ``study_setup`` document to a persistable ``study`` document
(task C-07 adapter gap; journey plan docs/plans/JOURNEY_215_16_NORTHERN_2026-10-04.md
link 4 'Smallest task (C-07 adapter)', wave 1 item 6; directive D-090 R109).

``GET /api/v1/properties/{bbl}/study`` (app.api.v1.study_read) returns a
``study_setup`` document: the lot-choice + site-facts SETUP half of a study, shaped
to the ``study`` contract's ``property`` / ``lots`` / ``lot_selection`` / ``site``
sub-objects but carrying two read-only markers (``document_kind`` and a top-level
``bbl``) and NONE of a persisted study's ``options`` / ``selected_option_id`` /
``revision`` / ``study_id`` / ``origin``. So ``build_evaluator_inputs`` (C-07) fails
closed on it with ``StudyContractError: Additional properties are not allowed
('bbl', 'document_kind' were unexpected)`` (walkthrough
docs/walkthroughs/2026-10-04-215-16-northern-blvd.md section 4).

:func:`study_from_study_setup` closes that SHAPE gap. It takes a validated
``study_setup`` read document plus ONE explicit option and returns a document that
validates against the ``study`` contract:

- ``property`` / ``lots`` / ``lot_selection`` / ``site`` are carried VERBATIM
  (deep-copied, so the result does not alias the read): every site fact travels with
  its value, unit, measurement rank, label, source and ``blocks`` untouched - no fact
  invented, none dropped, ranks untouched (CLAUDE.md principle 2 provenance).
- the two read-only markers (``document_kind``, top-level ``bbl``) are dropped - they
  are not study fields; ``bbl`` is already carried inside ``property.bbl`` and is
  cross-checked against it before being dropped (a mismatch is a defect, raised).
- ``options`` is ``[option]`` and ``selected_option_id`` is the option's id: NOTHING
  is pre-selected, the option is an explicit input (plan M1-06 'no example data in
  real work'; the study store takes option inputs from its caller, never invents
  them). ``study_id`` and ``revision`` are explicit caller inputs for the same reason
  (a ``revision.created_at`` is never invented here).
- ``origin`` is ``{"kind": "new", "export_id": null}``: a study bridged from a LIVE
  read is a NEW study, not an export restore (``copied_from_export`` is the historical
  -export path, a different flow; study.schema.json ``origin``).

The output is re-validated against the ``study`` contract before return (fail closed):
an invalid bridge is a defect, never emitted. If the ``study_setup`` carries a
top-level field the ``study`` contract cannot carry, the bridge STOPS and names it
rather than silently dropping it (a contract change is its own task).

Pure, offline, library-only: no network, no route, no mutation of the input.
"""

from __future__ import annotations

import copy
from typing import Any

from app.contracts.study_contracts import validate_study_document

__all__ = [
    "STUDY_CONTRACT_VERSION",
    "StudySetupBridgeError",
    "study_from_study_setup",
]

# The study.schema.json contract version this bridge emits (its enum's only value).
STUDY_CONTRACT_VERSION = "1.0.0"

# The document_kind every study_read document carries (app.api.v1.study_read).
_STUDY_SETUP_DOCUMENT_KIND = "study_setup"

# study_setup sub-objects carried VERBATIM into the study (the study fields a setup
# document already holds; same names, same shapes).
_CARRIED_KEYS = ("property", "lots", "lot_selection", "site")

# study_setup top-level markers dropped on the way in (not study fields): the read's
# document_kind and the redundant top-level bbl (also inside property.bbl).
_DROPPED_KEYS = ("document_kind", "bbl")

# Every top-level key a study_setup may legitimately carry. A key outside this set is
# one the study contract cannot carry without a schema change: STOP and report it.
_KNOWN_SETUP_KEYS = frozenset((*_CARRIED_KEYS, *_DROPPED_KEYS))


class StudySetupBridgeError(Exception):
    """A ``study_setup`` read document could not be bridged to a ``study`` document.
    Raised server-side (fail closed): a malformed setup, an unmappable field, or a
    missing explicit input is a defect, surfaced rather than papered over."""


def study_from_study_setup(
    study_setup: dict, option: dict, *, study_id: str, revision: dict
) -> dict:
    """Bridge a ``study_setup`` read document + ONE explicit option to a ``study``.

    ``study_setup`` is a validated study-read document (``document_kind``
    ``study_setup``, as ``GET /api/v1/properties/{bbl}/study`` returns it). ``option``
    is ONE study option (study.schema.json ``#/$defs/option``); it becomes the study's
    only option and its ``option_id`` becomes ``selected_option_id`` - nothing is
    pre-selected. ``study_id`` and ``revision`` (the full
    ``{number, created_at, parent}`` revision object) are explicit caller inputs so no
    identity or timestamp is invented.

    Returns a document that validates against the ``study`` contract (re-validated
    before return). Raises :class:`StudySetupBridgeError` when ``study_setup`` is not a
    study-setup document, is missing a carried sub-object, carries a top-level field the
    study contract cannot carry (STOP and report), or has a top-level ``bbl`` that
    disagrees with ``property.bbl``; or when ``option`` is not a mapping with a
    non-empty ``option_id``. Propagates :class:`StudyContractError` if the bridged
    document fails the study contract."""
    if not isinstance(study_setup, dict):
        raise StudySetupBridgeError(
            f"study_setup must be a JSON object, got {type(study_setup).__name__}"
        )
    kind = study_setup.get("document_kind")
    if kind != _STUDY_SETUP_DOCUMENT_KIND:
        raise StudySetupBridgeError(
            f"study_setup document_kind must be {_STUDY_SETUP_DOCUMENT_KIND!r}, "
            f"got {kind!r}; this is not a study-read document"
        )

    unexpected = sorted(set(study_setup) - _KNOWN_SETUP_KEYS)
    if unexpected:
        raise StudySetupBridgeError(
            f"study_setup carries top-level field(s) {unexpected} the study contract "
            "cannot carry without a schema change; a contract change is its own task "
            "(do not silently drop a field)"
        )
    missing = [key for key in _CARRIED_KEYS if key not in study_setup]
    if missing:
        raise StudySetupBridgeError(
            f"study_setup is missing required sub-object(s) {missing}; it is not a "
            "complete study-read document"
        )

    # Drop the redundant top-level bbl only after confirming it agrees with the bbl
    # carried inside property (a disagreement is a defect, not silently resolved).
    property_bbl = _property_bbl(study_setup["property"])
    top_bbl = study_setup.get("bbl")
    if top_bbl is not None and top_bbl != property_bbl:
        raise StudySetupBridgeError(
            "study_setup top-level bbl does not match property.bbl "
            f"({top_bbl!r} vs {property_bbl!r}); refusing to drop a conflicting marker"
        )

    option_id = _option_id(option)

    study = {
        "contract_version": STUDY_CONTRACT_VERSION,
        "study_id": study_id,
        # Carried VERBATIM (deep-copied so the study never aliases the read).
        "property": copy.deepcopy(study_setup["property"]),
        "lots": copy.deepcopy(study_setup["lots"]),
        "lot_selection": copy.deepcopy(study_setup["lot_selection"]),
        "site": copy.deepcopy(study_setup["site"]),
        # The explicit option; nothing pre-selected beyond the one given.
        "options": [copy.deepcopy(option)],
        "selected_option_id": option_id,
        "revision": copy.deepcopy(revision),
        # A live-read bridge is a new study, never an export restore.
        "origin": {"kind": "new", "export_id": None},
    }
    # Fail closed: an invalid bridge is a defect, never emitted.
    validate_study_document(study)
    return study


def _property_bbl(property_obj: Any) -> Any:
    if not isinstance(property_obj, dict) or "bbl" not in property_obj:
        raise StudySetupBridgeError(
            "study_setup.property must be an object carrying a bbl"
        )
    return property_obj["bbl"]


def _option_id(option: Any) -> str:
    if not isinstance(option, dict):
        raise StudySetupBridgeError(
            f"option must be a JSON object, got {type(option).__name__}"
        )
    option_id = option.get("option_id")
    if not isinstance(option_id, str) or not option_id:
        raise StudySetupBridgeError(
            "option must carry a non-empty string option_id "
            "(study.schema.json #/$defs/option)"
        )
    return option_id
