"""DB-034(a)/(b) input gate for the proposed-massing validator (task M5-T053).

The accepted semantic validator :func:`app.scenario.proposal.validate_proposed_massing`
(M5-T048, phase B0) is owned by the LIVE M5-T051 lane and is FORBIDDEN to edit here
(D-072 disjointness). This module is the input GATE the editor-input route calls: it
enforces the two untrusted-edge hardening PRECONDITIONS that DB-034 binds to the first
packet wiring editor input to the validator, THEN delegates to the accepted validator
UNCHANGED. A follow-up MAY fold the gate inward once M5-T051 lands, if reviewers prefer;
the wrapper is the disjointness-correct home today and a legitimate boundary (input-gate
vs semantic-validation responsibilities).

Two preconditions, both fail-closed and cheap (O(1)/O(n), no geometry), enforced BEFORE the
quadratic simplicity test the validator runs per outline:

(a) GLOBAL vertex budget :data:`MAX_TOTAL_VERTICES` across the base outline PLUS every
    per-level outline, summed. The B0 validator caps each SINGLE outline at
    ``MAX_OUTLINE_VERTICES`` (1000) with an O(1) length check before any quadratic work,
    but it runs its O(n^2) simplicity test once PER outline for up to ``MAX_LEVELS`` (500)
    per-level outlines, so the per-outline ceilings alone leave a ~2.5e8-segment-test worst
    case (~minutes CPU; M5-T048 G5 finding 1). A single O(number-of-outlines) pre-count of
    the summed positions, refused before delegation, closes it: with each single outline
    still capped at 1000, a summed budget of 5000 bounds the total simplicity work at
    <= 5 * 1000^2 = 5e6 segment tests (``sum(m_i^2)`` under ``sum(m_i) <= 5000`` with each
    ``m_i <= 1000`` is maximised by the fewest, largest outlines), a firm sub-second bound.

(b) MAX_STRING_LEN ceiling on every user-authored string field - ``provenance.author``,
    ``provenance.editor_version``, ``provenance.parent_scenario_id`` and every
    ``exterior_walls[].id`` - plus BOUNDED-REPR (the DB-023c cap + explicit truncation
    marker) on any user value this gate embeds in a refusal message, so an attacker-length
    wall id is never echoed unbounded (M5-T048 G5 finding 2; the B0 ``non_empty_string``
    $ref carries minLength but no maxLength).

MONOTONE by construction: the gate only ADDS refusals. It never turns a value the validator
would reject into an acceptance, and it always delegates to the unchanged validator last, so
``validate_proposed_massing_input(block)`` accepts iff the budget is met AND the string
ceilings hold AND ``validate_proposed_massing(block)`` accepts. The counting and ceiling
checks are fully defensive - they act only on the expected shapes and otherwise fall through
to the validator's own typed field error - so a malformed block still earns its precise B0
refusal unchanged.
"""

from __future__ import annotations

from app.scenario.proposal import ProposedMassingError, validate_proposed_massing

__all__ = [
    "MAX_STRING_LEN",
    "MAX_TOTAL_VERTICES",
    "ProposedMassingInputError",
    "validate_proposed_massing_input",
]

# (a) Global vertex budget across the base outline + all per-level outlines (positions,
# each outline's count INCLUDING its repeated closing vertex - the cheap O(1) ``len``).
# See the module docstring for the worst-case arithmetic (bounds the summed simplicity work
# at <= 5e6 segment tests, vs the ~2.5e8 the per-outline ceilings alone admit).
MAX_TOTAL_VERTICES = 5000

# (b) Ceiling on every user-authored string field. Generous for a real author / editor
# version / scenario id / wall id, far below any length that is a paste or injection payload
# rather than editor input.
MAX_STRING_LEN = 512

# Bounded-repr display cap (DB-023c): a user value embedded in a refusal message is shown at
# most this many characters of its ``repr``, then an explicit truncation marker naming the
# true length - never the full attacker-supplied value.
_REPR_DISPLAY_CAP = 80


class ProposedMassingInputError(ProposedMassingError):
    """A ``proposed_massing`` block refused by the DB-034(a)/(b) INPUT GATE - the global
    vertex budget or a string ceiling - before the semantic validator ran.

    A subclass of :class:`ProposedMassingError` so a caller catches gate and semantic
    refusals with one ``except`` and reads ``.field`` uniformly, while the type still
    distinguishes an input-boundary refusal from a semantic one.
    """


def _bounded_repr(value: object) -> str:
    """The DB-023c bounded-repr: ``repr(value)`` capped at :data:`_REPR_DISPLAY_CAP`
    characters with an explicit truncation marker naming the true ``repr`` length. ``repr``
    also renders any unpaired surrogate as an ASCII escape, so the result is always encodable
    text safe to embed in a refusal message and a JSON response."""
    text = repr(value)
    if len(text) <= _REPR_DISPLAY_CAP:
        return text
    return f"{text[:_REPR_DISPLAY_CAP]}...<truncated; {len(text)} chars total>"


def _outline_position_count(outline: object) -> int:
    """The number of positions in an outline's ``vertices`` array, or 0 when the outline is
    absent or not the expected shape (a wrong shape is left for the validator's own typed
    field error). O(1): a bare ``len`` on the already-parsed list, no geometry."""
    if isinstance(outline, dict):
        vertices = outline.get("vertices")
        if isinstance(vertices, list):
            return len(vertices)
    return 0


def _total_position_count(block: dict) -> int:
    """Sum the positions of the base outline and every present per-level outline. Walks the
    levels once (O(number of outlines)); each outline contributes an O(1) ``len``. No
    coordinate is examined and no simplicity test runs, so this precedes all quadratic
    work."""
    total = _outline_position_count(block.get("outline"))
    levels = block.get("levels")
    if isinstance(levels, list):
        for level in levels:
            if isinstance(level, dict):
                total += _outline_position_count(level.get("outline"))
    return total


def _check_string_ceiling(value: object, field: str) -> None:
    """Refuse a user-authored string that exceeds :data:`MAX_STRING_LEN`, naming the exact
    ``field`` and embedding ONLY the bounded-repr of the value. A non-string is left for the
    validator (which owns the type refusal); only an over-length string is the gate's
    concern."""
    if isinstance(value, str) and len(value) > MAX_STRING_LEN:
        raise ProposedMassingInputError(
            f"{field} exceeds MAX_STRING_LEN ({MAX_STRING_LEN}); got {len(value)} "
            f"characters ({_bounded_repr(value)})",
            field=field,
        )


def _check_string_ceilings(block: dict) -> None:
    """Apply the MAX_STRING_LEN ceiling to every user-authored string field: the three
    provenance strings and every wall id. Fully defensive - it acts only on the expected
    shapes; any other defect flows to the validator's typed field error."""
    provenance = block.get("provenance")
    if isinstance(provenance, dict):
        _check_string_ceiling(
            provenance.get("author"), "proposed_massing.provenance.author"
        )
        _check_string_ceiling(
            provenance.get("editor_version"),
            "proposed_massing.provenance.editor_version",
        )
        _check_string_ceiling(
            provenance.get("parent_scenario_id"),
            "proposed_massing.provenance.parent_scenario_id",
        )
    walls = block.get("exterior_walls")
    if isinstance(walls, list):
        for pos, wall in enumerate(walls):
            if isinstance(wall, dict):
                _check_string_ceiling(
                    wall.get("id"), f"proposed_massing.exterior_walls[{pos}].id"
                )


def validate_proposed_massing_input(block: object) -> None:
    """Gate an untrusted ``proposed_massing`` block, then delegate to the accepted validator.

    Enforces the DB-034(a) global vertex budget and the DB-034(b) string ceilings FIRST -
    both cheap and fail-closed, before any quadratic simplicity test - then calls
    :func:`app.scenario.proposal.validate_proposed_massing` UNCHANGED. Returns ``None`` when
    the block is valid; raises :class:`ProposedMassingInputError` for a gate refusal or the
    validator's own :class:`ProposedMassingError` for a semantic refusal - both name the
    exact ``field``. Does not mutate ``block``.
    """
    if isinstance(block, dict):
        total_positions = _total_position_count(block)
        if total_positions > MAX_TOTAL_VERTICES:
            raise ProposedMassingInputError(
                f"proposed_massing total outline vertices exceed MAX_TOTAL_VERTICES "
                f"({MAX_TOTAL_VERTICES}); the base outline plus every per-level outline sum "
                f"to {total_positions} positions",
                field="proposed_massing",
            )
        _check_string_ceilings(block)

    # Delegate to the accepted semantic validator UNCHANGED. A non-dict block, or any defect
    # the gate deliberately did not pre-empt, earns the validator's precise typed field error
    # here (monotone: the gate only added refusals above).
    validate_proposed_massing(block)
