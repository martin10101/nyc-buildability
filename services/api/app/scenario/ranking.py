"""Deterministic OFFLINE ranking of EXPLICIT assumption-sets for one scenario (M5-T007).

Second optimization-side brick under M5: fills the Compare UI's "ranked scenario cards +
score breakdown" with an honest, explicit-assumption-only ordering. It consumes the accepted
:func:`app.scenario.derive_practical_usable_range` (M5-T005/M5-T006) and the ``scenario``
document READ-ONLY, and produces a NEW ranking object. It is contract-free: it is NOT the
canonical scenario contract and must never be stored or presented as Verified.

Hard boundaries (AI-boundary + honesty; also enforced by
``tests/scenario/test_scenario_ranking.py``):

* Ranks ONLY the caller-provided explicit assumption-sets - each fed through
  ``derive_practical_usable_range`` to get an illustrative range - and NEVER invents,
  fabricates, or adds a scenario / assumption / alternative. Empty ``assumption_sets`` ->
  a single-candidate ranking of the RAW scenario (the scenario itself, no factor applied),
  never a fabricated alternative.
* The OBJECTIVE is an EXPLICIT caller input (:class:`RankingObjective`, defined here -
  contract-free). A "best" / top candidate is NEVER emitted without NAMING that objective:
  every candidate carries the named objective, its score, and the transparent score
  COMPONENTS (which already-surfaced numbers produced it).
* Scores are computed ONLY from already-surfaced numbers (the derived range point and the
  canonical draft cap transported verbatim by ``derive``) - never a recomputed legal value,
  never a hidden weight. The scoring function is a documented function of the surfaced
  numbers only.
* TOTAL, STABLE ordering: identical (scenario document, objective, assumption-sets) ->
  byte-identical ordered output, INDEPENDENT of the order the assumption-sets are supplied
  in. Ties (equal score) are broken by a deterministic CONTENT key - the EXACT
  insertion-order-preserving serialization of the emitted assumption-set echo (the very
  bytes that candidate contributes to the output), never by transient input position - so
  two equal-score candidates reorder only when their emitted echoes actually differ, and
  reordering the inputs never changes the output. (``sort_keys`` is deliberately NOT used
  for the tie-break: it would collapse two dicts that differ only in key insertion order to
  a single key even though their emitted echoes differ, so a stable sort would then leak the
  caller's transient input position.)
* Fail closed: an unknown / malformed / non-finite objective, or a malformed
  ``assumption_sets`` container -> a typed ``invalid`` outcome; a scenario document that
  surfaces no positive draft cap (no_scenario / unsupported / malformed) -> a typed ``empty``
  outcome with a visible reason. A single malformed assumption-set among good ones -> that
  candidate is flagged not-scorable and ranked LAST (derive's own fail-closed guard), never
  given a fabricated score. Every emitted echo (the assumption-set AND the transported
  ``derived`` breakdown) is passed through a strict-JSON-safety sanitizer: a malformed
  assumption VALUE - NaN, +-Inf, a negative or float-overflowing number, or a
  non-JSON-serializable object - is replaced by a TYPED, bounded placeholder marker, never
  echoed raw. No crash; strict-JSON-safe (``json.dumps(out, allow_nan=False)`` never raises;
  no NaN / Inf / negative number is ever emitted).
* Never Verified: ``coverage_status`` can never be ``verified`` on ANY outcome (an incoming
  ``verified`` is capped to ``conditional``) and a caller ``objective`` equal to the Verified
  token (any case) is never echoed on the ``invalid`` outcome, so the never-Verified token
  can never enter the output through ANY field; ``needs_review`` and the
  ``not_verified_disclaimer`` are preserved end-to-end; scores are ILLUSTRATIVE (from the
  draft cap), never a Verified / feasible ranking.
* Read-only: the scenario document and each assumption-set are consumed without mutation and
  without aliasing - the ranking echoes DEEP COPIES, so the caller's inputs are byte-unchanged
  after ranking.
"""

from __future__ import annotations

import copy
import json
import math
from enum import Enum
from typing import Any

from ._json_safety import _json_safe, _unsafe_marker
from .constants import NOT_VERIFIED_DISCLAIMER
from .derive import (
    DerivedRangeKind,
    _cap_section_reference,
    derive_practical_usable_range,
)

__all__ = [
    "RANKING_LABEL",
    "RankingKind",
    "RankingObjective",
    "rank_scenario_assumption_sets",
]


# --- Typed vocabulary + honest labels (all CONSTANTS; nothing computed at runtime). ---


class RankingObjective(str, Enum):
    """The EXPLICIT, caller-chosen ranking objective (string-valued so it serializes straight
    into the ranking object). A top candidate is never surfaced without naming this.

    Only one meaningful optimization dimension exists for a SINGLE scenario document: the
    canonical draft cap is constant across the candidates, so the value that varies is the
    illustrative usable area produced by each assumption-set's declared reduction factors.
    ``MAXIMIZE_ILLUSTRATIVE_USABLE_AREA`` orders the explicit assumption-sets by that
    already-surfaced number. Additional objectives register in ``_OBJECTIVE_SCORERS`` /
    ``_OBJECTIVE_LABELS`` below without changing any caller contract.
    """

    #: Order candidates by the illustrative usable-area point (higher = better).
    MAXIMIZE_ILLUSTRATIVE_USABLE_AREA = "maximize_illustrative_usable_area"


class RankingKind:
    """Typed outcome of a ranking (string values serialize straight into the object)."""

    #: At least one candidate was produced; candidates are ordered by the named objective.
    RANKED = "ranked_scenario_assumption_sets"
    #: The scenario document surfaces no positive draft cap -> nothing to rank (visible reason).
    EMPTY = "empty_no_rankable_cap"
    #: Fail-closed on an unknown/malformed objective or a malformed assumption-sets container.
    INVALID = "invalid_ranking_request"


# Never-Verified ceiling: an incoming ``verified`` is capped to this on EVERY outcome.
NEVER_VERIFIED_COVERAGE_CEILING = "conditional"

# Mandatory honest label on a ranking (illustrative / from the draft cap, never Verified).
#
# D-059-R003 (M5-T028): the Zoning Resolution section named MUST be derived from the rule
# ACTUALLY evaluated for the subject property (the R6-R12 family cites ZR 23-22, not the R1-R5
# families' 23-21), never hardcoded. ``_ranking_label`` builds the label from whatever section
# the scenario document's own ``cap_provenance`` citation names.
def _ranking_label(section_reference: str | None) -> str:
    """The mandatory ranking label, with the Zoning Resolution section clause built from the
    ACTUAL evaluated rule's citation (``section_reference``) rather than a hardcoded section
    number. Falls back to a section-agnostic clause (never invents a section) when no citation is
    available."""
    section_clause = (
        f"under ZR {section_reference}"
        if isinstance(section_reference, str) and section_reference
        else "under the cited Zoning Resolution bulk-regulation section (see "
        "cap_provenance.citations for the exact section)"
    )
    return (
        "ILLUSTRATIVE ranked scenario cards: the caller's EXPLICITLY-declared assumption-sets "
        "ordered by a NAMED objective, each scored ONLY from already-surfaced numbers (the "
        f"DRAFT residential zoning-floor-area cap {section_clause} x explicitly-declared typed "
        "factors). NOT gross, net, sellable, or feasible floor area; NOT a buildable envelope; "
        "NOT an optimization over invented alternatives. Draft (needs_review); requires "
        "professional review; NOT Verified."
    )


# Backward-compatible module constant (D-059-R003) for the small set of consumers OUTSIDE this
# task's allowed_paths that import ``RANKING_LABEL`` directly (scenario/__init__.py's
# re-export). Byte-identical to ``_ranking_label("23-21")`` - the R5 canonical rule_evaluation
# fixture's own citation - so this stays a harmless, literally-correct legacy alias, NOT a
# universal label: the live path below calls ``_ranking_label`` with the real per-request
# citation for every district family.
RANKING_LABEL = _ranking_label("23-21")

# Mandatory honest label on every candidate card.
CANDIDATE_LABEL = (
    "ILLUSTRATIVE candidate: one explicitly-declared assumption-set scored against the named "
    "objective from already-surfaced numbers only. NOT Verified; requires professional review."
)

# Human label naming each objective (so a "best" card can never travel without its objective).
_OBJECTIVE_LABELS: dict[RankingObjective, str] = {
    RankingObjective.MAXIMIZE_ILLUSTRATIVE_USABLE_AREA: (
        "Maximize illustrative usable area: rank the explicit assumption-sets by the derived "
        "illustrative usable-area point (draft cap x declared factors) descending."
    ),
}


# --- Numeric guards (fail-closed): reject bool / non-numeric / NaN / +-inf / negative. ---


def _is_number(value: Any) -> bool:
    """True only for a real numeric (int/float), never a bool."""
    return isinstance(value, int | float) and not isinstance(value, bool)


def _finite_float(value: Any) -> float | None:
    """``value`` as a finite float, or ``None`` when not usable (bool / non-numeric / NaN /
    +-inf / int too large for a finite float). Never raises."""
    if not _is_number(value):
        return None
    try:
        as_float = float(value)
    except (OverflowError, ValueError):
        return None
    if not math.isfinite(as_float):
        return None
    return as_float


def _non_negative_finite_float(value: Any) -> float | None:
    """Finite float greater than or equal to zero, else ``None`` (a score is never negative)."""
    result = _finite_float(value)
    if result is None or result < 0.0:
        return None
    return result


def _positive_finite_float(value: Any) -> float | None:
    """Finite float strictly greater than zero, else ``None``."""
    result = _finite_float(value)
    if result is None or result <= 0.0:
        return None
    return result


# --- Never-Verified lineage carried onto every outcome ---


def _bounded_coverage_status(scenario_document: Any) -> str | None:
    """Coverage status carried onto an outcome, never-Verified enforced: an incoming
    ``verified`` (any case) -> ``conditional``; a non-string is not fabricated (``None``)."""
    coverage_status = (
        scenario_document.get("coverage_status") if isinstance(scenario_document, dict) else None
    )
    if not isinstance(coverage_status, str):
        return None
    if coverage_status.strip().lower() == "verified":
        return NEVER_VERIFIED_COVERAGE_CEILING
    return coverage_status


def _base_lineage(scenario_document: Any) -> dict:
    """Lineage every outcome carries: bounded (never-Verified) coverage_status, needs_review,
    and the preserved not_verified_disclaimer."""
    disclaimer = (
        scenario_document.get("not_verified_disclaimer")
        if isinstance(scenario_document, dict)
        else None
    )
    return {
        "coverage_status": _bounded_coverage_status(scenario_document),
        "needs_review": True,
        "not_verified_disclaimer": (
            disclaimer if isinstance(disclaimer, str) else NOT_VERIFIED_DISCLAIMER
        ),
    }


# --- Objective normalization + scoring (documented function of surfaced numbers only) ---


def _normalize_objective(objective: Any) -> RankingObjective | None:
    """The caller-supplied objective as a :class:`RankingObjective`, or ``None`` when it is
    unknown / malformed / non-finite. Accepts the enum member itself or its string value; any
    other type (including a non-finite float) is rejected fail-closed."""
    if isinstance(objective, RankingObjective):
        return objective
    if isinstance(objective, str):
        try:
            return RankingObjective(objective)
        except ValueError:
            return None
    return None


def _score_maximize_usable_area(derived: dict) -> tuple[float | None, dict | None]:
    """Score for ``MAXIMIZE_ILLUSTRATIVE_USABLE_AREA``: the derived illustrative usable-area
    point (already surfaced by ``derive`` as draft cap x product(applied factors)). Returns
    ``(score, components)`` or ``(None, None)`` when the derived range is absent or not a
    non-negative finite number (fail-closed: no fabricated score)."""
    usable_range = derived.get("practical_usable_range")
    if not isinstance(usable_range, dict):
        return None, None
    score = _non_negative_finite_float(usable_range.get("point"))
    if score is None:
        return None, None
    components = {
        "objective": RankingObjective.MAXIMIZE_ILLUSTRATIVE_USABLE_AREA.value,
        "illustrative_usable_area_sq_ft": usable_range.get("point"),
        "canonical_cap_sq_ft": derived.get("canonical_cap_sq_ft"),
        "factor_product": derived.get("factor_product"),
        "applied_factor_count": len(derived.get("applied_factors") or []),
        "formula": (
            "score = illustrative_usable_area_sq_ft = canonical draft zoning-floor-area cap "
            "x product(applied factors). Higher is better for "
            "maximize_illustrative_usable_area. No hidden weight; the score is exactly the "
            "already-surfaced derived point."
        ),
    }
    return score, components


# Registry: objective -> scoring function. Adding an objective is a local, contract-free change.
_OBJECTIVE_SCORERS = {
    RankingObjective.MAXIMIZE_ILLUSTRATIVE_USABLE_AREA: _score_maximize_usable_area,
}


# --- Candidate construction + ordering ---


def _content_key(assumption_set_echo: Any) -> str:
    """Deterministic tie-break secondary key: the EXACT (insertion-order-preserving) JSON
    serialization of the already-sanitized assumption-set echo - i.e. the very bytes this
    candidate contributes to the output. Ordering by these bytes makes the ranked output a
    pure function of the SET of emitted candidates, INDEPENDENT of the transient input
    position: two candidates compare equal here ONLY when their emitted echoes are
    byte-identical (hence interchangeable). ``sort_keys`` is deliberately NOT used - it would
    collapse two dicts that differ only in key insertion order to a single key even though
    their emitted echoes differ, so a stable sort would then leak the caller's input order
    (the very tie-break collision this key guards against). Never raises: the echo is already
    strict-JSON-safe, and any residual falls back through ``default=repr`` / a deterministic
    ``repr``."""
    try:
        return json.dumps(assumption_set_echo, ensure_ascii=True, default=repr)
    except TypeError:
        return "repr:" + repr(assumption_set_echo)


def _build_candidate(
    scenario_document: dict, objective: RankingObjective, assumption_set: Any
) -> dict:
    """Build ONE candidate core (rank assigned later) from a single explicit assumption-set.

    The assumption-set is DEEP-COPIED (no aliasing / caller input byte-unchanged) and fed
    through ``derive_practical_usable_range`` on a shallow scenario-document copy whose
    ``assumptions`` is that set - so ``derive`` scores exactly the caller's explicit set. A
    derive outcome that is not a DERIVED range (not_derivable / invalid_assumption) yields a
    not-scorable candidate flagged with derive's own reason, never a fabricated score.

    The RAW deep copy is what ``derive`` scores (so its fail-closed guards see the true
    values), but everything this candidate EMITS - the echoed assumption-set AND the
    transported ``derived`` breakdown - is passed through :func:`_json_safe`, so a malformed
    assumption VALUE (NaN/+-Inf/negative/float-overflowing/non-serializable) is surfaced as a
    typed marker and never echoed raw. The returned core is therefore already strict-JSON-safe
    (and its ``assumption_set`` is exactly the bytes the tie-break key will order on)."""
    try:
        echo = copy.deepcopy(assumption_set)
    except Exception:
        # L1 defense-in-depth: a non-deepcopyable assumption value (e.g. a lock or generator,
        # whose deepcopy raises TypeError/RuntimeError) fails CLOSED to a typed not-scorable
        # candidate instead of crashing the ranking. The echo is a typed, address-free marker
        # (never the raw value); derive is not called (it needs a usable copy). Strict-JSON-safe
        # and deterministic like every other candidate.
        return _json_safe(
            {
                "objective": objective.value,
                "objective_label": _OBJECTIVE_LABELS[objective],
                "assumption_set": _unsafe_marker("undeepcopyable", assumption_set),
                "scorable": False,
                "score": None,
                "score_components": None,
                "derived_kind": None,
                "not_scorable_reason": (
                    "The assumption-set could not be safely copied (a non-deepcopyable value, "
                    "e.g. a lock or generator); flagged not-scorable and ranked LAST "
                    "(fail-closed, no fabricated score)."
                ),
                "label": CANDIDATE_LABEL,
                "derived": None,
            }
        )
    candidate_document = {**scenario_document, "assumptions": echo}
    derived = derive_practical_usable_range(candidate_document)

    scorable = False
    score: float | None = None
    components: dict | None = None
    not_scorable_reason: str | None = None
    if derived.get("derived_kind") == DerivedRangeKind.DERIVED:
        scorer = _OBJECTIVE_SCORERS[objective]
        score, components = scorer(derived)
        if score is None:
            not_scorable_reason = (
                "The derived range carried no non-negative finite usable-area point; scored "
                "as not-rankable (fail-closed, no fabricated score)."
            )
        else:
            scorable = True
    else:
        not_scorable_reason = derived.get("not_derivable_reason") or (
            "This assumption-set did not produce a derived illustrative range "
            f"(derived_kind={derived.get('derived_kind')!r}); ranked last, no fabricated score."
        )

    return _json_safe(
        {
            "objective": objective.value,
            "objective_label": _OBJECTIVE_LABELS[objective],
            "assumption_set": echo,
            "scorable": scorable,
            "score": score,
            "score_components": components,
            "derived_kind": derived.get("derived_kind"),
            "not_scorable_reason": not_scorable_reason,
            "label": CANDIDATE_LABEL,
            "derived": derived,
        }
    )


def _sort_key(candidate_core: dict, content_key: str) -> tuple:
    """Total, deterministic sort key: scorable candidates first, then by score DESCENDING,
    then by the content key ASCENDING (a total tie-break independent of input order). Equal
    keys occur only for byte-identical candidates, which are interchangeable."""
    scorable = candidate_core["scorable"]
    score = candidate_core["score"]
    return (
        0 if scorable else 1,
        -score if (scorable and score is not None) else 0.0,
        content_key,
    )


def _order_candidates(candidate_cores: list[dict]) -> list[dict]:
    """Order candidate cores by the total deterministic key and assign a 1-based ``rank``."""
    keyed = [
        (_sort_key(core, _content_key(core["assumption_set"])), core)
        for core in candidate_cores
    ]
    keyed.sort(key=lambda pair: pair[0])
    return [{"rank": index + 1, **pair[1]} for index, pair in enumerate(keyed)]


# --- Typed-outcome assemblers ---


def _safe_objective_echo(objective: Any) -> str | None:
    """The caller objective echoed on an ``invalid`` outcome, kept strict-JSON-safe AND
    never-Verified: a non-string objective is never echoed (``None`` keeps the output
    strict-JSON-safe), and a string equal to the Verified token (any case) is never echoed
    either (``None``), so a caller can neither make the output non-JSON-safe nor inject the
    never-Verified token into the output through the objective field."""
    if not isinstance(objective, str):
        return None
    if objective.strip().lower() == "verified":
        return None
    return objective


def _invalid_result(scenario_document: Any, objective: Any, reason: str) -> dict:
    """Fail-closed ``invalid`` outcome (unknown/malformed objective or malformed container).
    The objective is echoed only when it is a plain string that is NOT the Verified token (a
    non-finite/exotic objective, or the ``verified`` token, is surfaced as ``None`` so the
    output stays strict-JSON-safe and never emits the never-Verified token)."""
    result = {
        "ranking_kind": RankingKind.INVALID,
        "objective": _safe_objective_echo(objective),
        "objective_label": None,
        "ranked": False,
        "candidate_count": 0,
        "scorable_count": 0,
        "candidates": [],
        "label": _ranking_label(_cap_section_reference(scenario_document)),
        "reasons": [reason],
        "invalid_reason": reason,
        "empty_reason": None,
    }
    result.update(_base_lineage(scenario_document))
    return result


def _empty_result(scenario_document: Any, objective: RankingObjective, reason: str) -> dict:
    """Typed ``empty`` outcome: the scenario document surfaces no positive draft cap, so there
    is nothing to rank. Empty ranking + a visible reason, never a fabricated candidate."""
    result = {
        "ranking_kind": RankingKind.EMPTY,
        "objective": objective.value,
        "objective_label": _OBJECTIVE_LABELS[objective],
        "ranked": False,
        "candidate_count": 0,
        "scorable_count": 0,
        "candidates": [],
        "label": _ranking_label(_cap_section_reference(scenario_document)),
        "reasons": [reason],
        "invalid_reason": None,
        "empty_reason": reason,
    }
    result.update(_base_lineage(scenario_document))
    return result


def rank_scenario_assumption_sets(
    scenario_document: Any,
    objective: Any,
    assumption_sets: Any = None,
) -> dict:
    """Rank a set of EXPLICITLY-declared assumption-sets for ONE scenario document.

    The scenario document and every assumption-set are consumed READ-ONLY (never mutated,
    never aliased into the output). Returns a NEW, separate ranking object (contract-free); it
    is NOT the canonical scenario contract and must never be stored or presented as Verified.

    * ``objective`` is the EXPLICIT caller objective (:class:`RankingObjective` or its string
      value). An unknown / malformed / non-finite objective -> typed ``invalid`` outcome.
    * ``assumption_sets`` is a list of explicit assumption-sets (each a list of assumption
      dicts). ``None`` / empty -> a single-candidate ranking of the RAW scenario (no factor
      applied), never a fabricated alternative. A non-list (and non-None) container -> typed
      ``invalid`` outcome.
    * A scenario document that surfaces no positive ``draft_zoning_floor_area_cap_sq_ft``
      (no_scenario / unsupported / malformed) -> typed ``empty`` outcome with a visible reason.
    * Each assumption-set is run through ``derive_practical_usable_range`` and scored by the
      named objective from already-surfaced numbers only. A set whose derivation fails closed
      is flagged not-scorable and ranked LAST, never given a fabricated score.

    The result is deterministic and strict-JSON-safe: identical inputs (in any assumption-set
    order) yield byte-identical output, and ``json.dumps(result, allow_nan=False)`` never
    raises (no NaN / Inf / negative number is emitted).
    """
    normalized_objective = _normalize_objective(objective)
    if normalized_objective is None:
        return _invalid_result(
            scenario_document,
            objective,
            (
                "FAIL-CLOSED: the ranking objective is unknown, malformed, or non-finite "
                f"(recognized objectives: {sorted(o.value for o in RankingObjective)}). No "
                "candidate is ranked and no score is fabricated."
            ),
        )

    if _positive_finite_float(
        scenario_document.get("draft_zoning_floor_area_cap_sq_ft")
        if isinstance(scenario_document, dict)
        else None
    ) is None:
        return _empty_result(
            scenario_document,
            normalized_objective,
            (
                "EMPTY: the scenario document surfaces no positive canonical "
                "draft_zoning_floor_area_cap_sq_ft (no_scenario / unsupported / malformed); "
                "there is no illustrative usable area to rank and no candidate is fabricated."
            ),
        )

    # Absent container = "rank the raw scenario" (legitimate); present-but-non-list =
    # malformed -> fail closed. A single-candidate ranking of the raw scenario is the
    # scenario itself (an empty assumption-set), never an invented alternative.
    if assumption_sets is None:
        sets_to_rank: list = [[]]
    elif isinstance(assumption_sets, list):
        sets_to_rank = assumption_sets if assumption_sets else [[]]
    else:
        return _invalid_result(
            scenario_document,
            objective,
            (
                "FAIL-CLOSED: the assumption_sets container is malformed (expected a list of "
                f"assumption-sets, got {type(assumption_sets).__name__}); no candidate is "
                "ranked and no score is fabricated."
            ),
        )

    candidate_cores = [
        _build_candidate(scenario_document, normalized_objective, assumption_set)
        for assumption_set in sets_to_rank
    ]
    candidates = _order_candidates(candidate_cores)
    scorable_count = sum(1 for candidate in candidates if candidate["scorable"])

    reasons = [
        (
            "RANKED (illustrative): the caller's explicitly-declared assumption-sets ordered "
            "by the named objective. Each score is a documented function of already-surfaced "
            "numbers (the derived illustrative usable-area point = draft cap x declared "
            "factors); no alternative is invented and no legal value is recomputed."
        )
    ]
    if assumption_sets in (None, []) or (isinstance(assumption_sets, list) and not assumption_sets):
        reasons.append(
            "No explicit assumption-sets were supplied; the RAW scenario (no factor applied) "
            "is ranked as the single candidate - never a fabricated alternative."
        )
    if scorable_count < len(candidates):
        reasons.append(
            "One or more assumption-sets did not produce a derived illustrative range; those "
            "candidates are flagged not-scorable and ranked LAST, never given a fabricated "
            "score."
        )

    result = {
        "ranking_kind": RankingKind.RANKED,
        "objective": normalized_objective.value,
        "objective_label": _OBJECTIVE_LABELS[normalized_objective],
        "ranked": True,
        "candidate_count": len(candidates),
        "scorable_count": scorable_count,
        "candidates": candidates,
        "label": _ranking_label(_cap_section_reference(scenario_document)),
        "reasons": reasons,
        "invalid_reason": None,
        "empty_reason": None,
    }
    result.update(_base_lineage(scenario_document))
    return result
