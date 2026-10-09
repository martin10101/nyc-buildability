# M5-T007 PRODUCER REPORT — deterministic scenario ranking/scoring over explicit assumption-sets

- **Task:** M5-T007 — pure, deterministic, OFFLINE ranking of EXPLICITLY-declared assumption-sets for one scenario document; named objective, stable total order, transparent breakdown; never invents scenarios, never Verified.
- **Producer:** scenario-optimization-engineer · **Branch:** `task/M5-T007-ranking` · **Worktree:** `wt-m5t007` · **Run lineage:** persistent-local-23 (**REVISION 2**, per orchestrator revise directive forwarded 2026-09-08T21:58:43Z).
- **Base identity (no producer commit):** `28b45f3eece0c56d4e41e4225f109cf3fc80c261` — the working tree carries the edits; the orchestrator commits at the gate (`git rev-parse HEAD` == this SHA per the session git snapshot; producers do not commit — ADR-005).

## Changed-file inventory (complete — allowed_paths only)

| File | Change | Notes |
|---|---|---|
| `services/api/app/scenario/ranking.py` | **edited** | The two revision-2 defects fixed here (below); no public signature changed. |
| `services/api/app/scenario/__init__.py` | **edited** | Package facade that re-exports the ranking public API — `RANKING_LABEL`, `RankingKind`, `RankingObjective`, `rank_scenario_assumption_sets` (added to the imports and `__all__` when ranking was introduced under this task). Unchanged in this revision; **listed here because it is a genuinely modified file in this task's diff** and part of the reviewable surface. |
| `services/api/tests/scenario/test_scenario_ranking.py` | **edited** | +4 acceptance items this revision (2 dedicated regressions + 2 parametrized huge-int cases). |
| `project-control/reports/M5-T007-producer-report.md` | **this report** | |

**No forbidden path touched** — `builder.py` / `models.py` / `constants.py` / `contract.py` / **`derive.py`** / `packages/contracts/**` are all unmodified and consumed READ-ONLY. Explicit assumptions are preserved; only malformed *values* / non-JSON-safe *keys* are replaced by typed markers on the emitted echo.

## Revision 2 — the two defects fixed this pass

Both were latent crash / non-determinism holes in the strict-JSON-safety sanitizer added in revision 1. They refine boundary 5 (fail-closed + strict-JSON-safe) and boundary 4 (byte-identical, input-order-independent output).

### D1 — overflow marker did an UNGUARDED decimal repr of an arbitrarily large integer

**Defect.** `_unsafe_marker("overflow", value)` built its `unsafe_value_repr` as `_bounded_repr(repr(value))`. For an integer whose decimal expansion exceeds CPython's int→str conversion ceiling (4300 digits by default, CVE-2020-10735 hardening), `repr(value)` itself **raises `ValueError`** *before* truncation — crashing `rank_scenario_assumption_sets` on any path that echoes such a value. Revision 1's test used only `10**400` (401 digits), which slips under the ceiling and hid the bug. An unrecognized assumption carrying `10**5000` (≈5001 digits / 16610 bits) reaches `_json_safe` (it rides through derive's `unapplied_assumptions` and the echoed assumption-set), where `float(10**5000)` raises `OverflowError` → the `"overflow"` marker → the unguarded `repr` → crash.

**Fix.** New `_safe_scalar_repr(value)` renders scalars deterministically and *decimal-repr-safely*: `bool`/`float` via `repr` (always short); an `int` via its exact decimal `repr` only when `bit_length <= _INT_DECIMAL_SAFE_BITS` (256 bits ≈ 77 digits), otherwise a **magnitude descriptor** `int(sign=…, bit_length=…)` — so an arbitrarily large integer is *described*, never decimal-expanded, and can never trip the int→str ceiling; anything else renders as `<TypeName>` (no address). `_unsafe_marker` now uses `_bounded_repr(_safe_scalar_repr(value))`. `derive.py` is untouched (it already bounds only the assumption *key*, never the huge value).

### D2 — unsupported dict keys used an ADDRESS-BEARING (and crash-prone) repr

**Defect.** `_safe_key` fell back to `repr(key)` for any non-`str`/`None`/`bool`/finite-numeric key. For an ordinary object that is `<… object at 0x…>` — a **transient memory address** that varies run-to-run, so two identical calls produced byte-different output (violating the byte-identical determinism guarantee). For a huge-int key it hit the same int→str `ValueError` as D1.

**Fix.** New `_unsafe_key_token(key)` returns a deterministic typed token `"__unsafe_key__:" + _safe_scalar_repr(key)` — the key's **type only** for an object (never its address), its **magnitude** for a huge int (never decimal-expanded). `_safe_key` now returns that token for a non-finite/float-overflowing numeric key or any non-native key, and keeps `str`/`None`/`bool`/finite-numeric keys verbatim (json-native). `_json_safe`'s dict branch is now `_json_safe_mapping`, which additionally **de-collides** two distinct rejected keys that render to the same token with a deterministic `#N` positional suffix (insertion order preserved) — so a rejected key can never *silently overwrite* a sibling. This is the "collision-safe representation" the revise directive called for.

## What was built (design unchanged across revisions)

A pure service function `rank_scenario_assumption_sets(scenario_document, objective, assumption_sets=None) -> dict` plus its typed vocabulary (`RankingObjective`, `RankingKind`, `RANKING_LABEL`), exported from `app.scenario`. It orders the caller's EXPLICIT assumption-sets — each fed through the accepted `derive_practical_usable_range` (M5-T005/T006) READ-ONLY — into ranked candidate cards with a transparent score breakdown, for the Compare UI (M5-T004, parked). It is contract-free: a NEW object, never the canonical scenario contract, never stored/presented as Verified.

Seven hard boundaries remain enforced by `test_scenario_ranking.py`: (1) explicit-only / never-fabricates — empty sets rank the raw scenario, never an invented alternative; (2) named objective on the ranking AND every candidate; (3) score = already-surfaced numbers only (draft cap × declared factors), no hidden weight; (4) TOTAL, stable, input-order-independent ordering (content-based tie-break, not `sort_keys`); (5) fail-closed + strict-JSON-safe on every path; (6) never up-labels / never Verified (coverage capped to `conditional`; the literal `verified` objective never echoed); (7) contract-free, read-only, offline. Revision 1 hardened (4) tie-break collisions, (5) malformed-value sanitization, (6) objective suppression; revision 2 closes the two sanitizer holes above under (5)/(4).

## Evidence

- **Command (documented, run verbatim):** `python -m pytest services/api/tests/scenario` → **`173 passed in 2.92s`** (Python 3.11.9 / pytest 8.4.2, configfile `services/api/pyproject.toml`, rootdir `services/api`). **Re-confirmed at the current working tree in this bounded evidence pass: `173 passed in 2.60s`** (173 items collected; `test_scenario_ranking.py` = 49 items). See "Recorded execution results vs. unexecuted (reasoned) assertions" below.
- **Zero regression / counts:** 124 pre-existing (contract 23 + derive 70 + foundation 31) + **49 ranking items** (was 45; **+4** this revision: 2 dedicated regressions + 2 parametrized huge-int cases `10**5000`, `-(10**5000)`).
- **Pre-fix (red) behavior of the two new regressions is a REASONED assertion, not a recorded run** — no pre-fix transcript exists in this evidence set, the fixes are already applied to the working tree, and this revision makes no code change to produce a red run. Reasoning only: pre-fix the huge-int test would ERROR (`ValueError` from the unguarded `repr` of `10**5000`) and the object-key test would fail its `" at 0x" not in serialized` and byte-equality asserts (address leaked, non-deterministic). Full recorded-vs-unexecuted separation is in the dedicated section below. Note: pytest's own parametrize id-generation calls `str(val)`, which also trips the int→str ceiling, so the two huge-int cases carry explicit `pytest.param(..., id=…)`.
- **`git rev-parse HEAD`** (read-only, per snapshot) → `28b45f3eece0c56d4e41e4225f109cf3fc80c261` (no producer commit; working tree dirty for the orchestrator to commit at the gate).
- **Modularity:** `ranking.py` is now **673 physical lines** (was 599). It remains a **single cohesive responsibility** — deterministic ranking of explicit assumption-sets plus its *intrinsic* strict-JSON-safety sanitizer, which is required to *produce* strict-JSON-safe ranking output, not an unrelated concern. Physical count now crosses the 600 warn line but stays well under the 750 justify / 1000 hard thresholds; SLOC (excluding blanks/comments/docstrings — this module is docstring-dense) is materially lower. Per `docs/CODE_MODULARITY_POLICY.md`, this paragraph is the recorded cohesion rationale for growth near the warn line; the authoritative `python tools/modularity_check.py --check` is run by the orchestrator/CI at the gate (not a packet-documented producer command; not run here to avoid stalling the run under the native-tool preference). All edited lines ≤ 100 chars (repo ruff `line-length = 100`).
- **Tool discipline:** discovery via Read/Grep/Glob only; the only broker command run was the documented `python -m pytest services/api/tests/scenario`.

## EMBEDDED VERBATIM SOURCE (decisive bodies)

Quoted verbatim from the `allowed_paths` files (committed unchanged at the gate, so the gate diffs each excerpt against the committed file — the excerpt TEXT is the evidence).

### `ranking.py` — strict-JSON-safety sanitizer (D1 + D2 fixes)

```python
_INT_DECIMAL_SAFE_BITS = 256


def _safe_scalar_repr(value: Any) -> str:
    """A deterministic, bounded textual rendering of ``value`` that NEVER triggers CPython's
    integer string-conversion limit and NEVER embeds a non-deterministic object address:

    * ``bool`` / ``float`` -> ``repr`` (always short and safe: ``True``, ``nan``, ``-0.5`` ...).
    * ``int`` -> its exact decimal ``repr`` when small (``bit_length <= _INT_DECIMAL_SAFE_BITS``),
      else a magnitude descriptor ``int(sign=..., bit_length=...)`` - so an arbitrarily large
      integer is DESCRIBED, never decimal-expanded (which would be unbounded work and, past the
      interpreter's ceiling, a ``ValueError``).
    * anything else -> ``<TypeName>`` (its type only; NEVER ``repr``, whose default for an
      arbitrary object embeds a transient id and would break byte-identical determinism)."""
    if isinstance(value, bool):
        return repr(value)
    if isinstance(value, int):
        if value.bit_length() <= _INT_DECIMAL_SAFE_BITS:
            return repr(value)
        return f"int(sign={'-' if value < 0 else '+'}, bit_length={value.bit_length()})"
    if isinstance(value, float):
        return repr(value)
    return f"<{type(value).__name__}>"


def _unsafe_marker(kind: str, value: Any) -> dict:
    """A TYPED, strict-JSON-safe placeholder standing in for a malformed emitted value, so a
    caller's malformed assumption value is surfaced HONESTLY (typed) yet never echoed RAW.
    Numeric kinds carry a deterministic, bounded, decimal-repr-SAFE rendering
    (:func:`_safe_scalar_repr`, so an arbitrarily large integer is described by magnitude rather
    than decimal-expanded and can never raise CPython's int->str limit); an ``unsupported``
    object carries only its (deterministic) type name - never its ``repr``, which can embed a
    non-deterministic object id and break byte-identical determinism."""
    marker = {
        "unsafe_value_removed": True,
        "unsafe_kind": kind,
        "unsafe_value_type": type(value).__name__,
    }
    if kind != "unsupported":
        marker["unsafe_value_repr"] = _bounded_repr(_safe_scalar_repr(value))
    return marker


_UNSAFE_KEY_TOKEN_PREFIX = "__unsafe_key__"


def _unsafe_key_token(key: Any) -> str:
    """Deterministic, strict-JSON-safe replacement string for a dict key that cannot be a JSON
    object key. Built from :func:`_safe_scalar_repr`, so an arbitrary object surfaces its TYPE
    only (never its address-bearing ``repr``) and an arbitrarily large integer surfaces its
    MAGNITUDE (never an unguarded decimal expansion) - the token neither raises nor varies
    run-to-run."""
    return f"{_UNSAFE_KEY_TOKEN_PREFIX}:{_bounded_repr(_safe_scalar_repr(key))}"


def _safe_key(key: Any) -> Any:
    """A dict key guaranteed safe for ``json.dumps(..., allow_nan=False)``: a
    ``str``/``None``/``bool`` verbatim; a FINITE ``int``/``float`` verbatim (json coerces the
    latter to a string key); a non-finite / float-overflowing numeric key or ANY other type ->
    a deterministic typed :func:`_unsafe_key_token`. An arbitrary object key is therefore NEVER
    rendered through its address-bearing ``repr`` (which would leak a transient id and break
    byte-identical determinism) and an arbitrarily large integer key is NEVER decimal-expanded
    (which would raise past CPython's int->str ceiling), so no key can make ``json.dumps``
    raise or the output non-deterministic."""
    if isinstance(key, str) or key is None or isinstance(key, bool):
        return key
    if isinstance(key, int | float):
        try:
            as_float = float(key)
        except (OverflowError, ValueError):
            return _unsafe_key_token(key)
        return key if math.isfinite(as_float) else _unsafe_key_token(key)
    return _unsafe_key_token(key)


def _json_safe(value: Any) -> Any:
    """A recursive, strict-JSON-safe rendering of ``value`` (insertion order preserved): a
    NaN/+-Inf/negative/float-overflowing number or a non-JSON-serializable object becomes a
    typed :func:`_unsafe_marker`; ``dict``/``list``/``tuple`` are walked (tuples emit as
    lists); a finite non-negative number, ``bool``, ``None`` and ``str`` pass through. The
    result contains no NaN/Inf/negative number and no non-serializable value, so
    ``json.dumps(result, allow_nan=False)`` never raises. Never mutates ``value`` (it builds
    fresh containers), so the caller's input stays byte-unchanged."""
    if isinstance(value, bool):
        return value
    if isinstance(value, int | float):
        try:
            as_float = float(value)
        except (OverflowError, ValueError):
            return _unsafe_marker("overflow", value)
        if math.isnan(as_float):
            return _unsafe_marker("nan", value)
        if math.isinf(as_float):
            return _unsafe_marker("infinity", value)
        if as_float < 0.0:
            return _unsafe_marker("negative", value)
        return value
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, dict):
        return _json_safe_mapping(value)
    if isinstance(value, list | tuple):
        return [_json_safe(item) for item in value]
    return _unsafe_marker("unsupported", value)


def _json_safe_mapping(value: dict) -> dict:
    """Strict-JSON-safe rendering of a mapping (insertion order preserved): each key is made
    JSON-safe by :func:`_safe_key` and each value recursively by :func:`_json_safe`. Two
    DISTINCT source keys that collapse to the SAME safe key (e.g. two different rejected objects
    that both render to one typed token) are de-collided with a deterministic ``#N`` positional
    suffix, so a rejected key never SILENTLY overwrites another; insertion order is deterministic
    so the suffixes are deterministic too. Never raises (keys are already safe)."""
    out: dict = {}
    for key, item in value.items():
        safe_key = _safe_key(key)
        if safe_key in out:
            base = safe_key if isinstance(safe_key, str) else _unsafe_key_token(key)
            suffix = 1
            while f"{base}#{suffix}" in out:
                suffix += 1
            safe_key = f"{base}#{suffix}"
        out[safe_key] = _json_safe(item)
    return out
```

### `ranking.py` — result construction (candidate build + total ordering)

```python
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
    echo = copy.deepcopy(assumption_set)
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
```

### `ranking.py` — objective suppression (never-Verified echo)

```python
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
```

### `ranking.py` — the complete PUBLIC entry point

```python
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
        "label": RANKING_LABEL,
        "reasons": reasons,
        "invalid_reason": None,
        "empty_reason": None,
    }
    result.update(_base_lineage(scenario_document))
    return result
```

### New tests (verbatim) — the two revision-2 regressions

Fixture notes (prose, so fences stay pure source): `_preliminary_document()` builds the canonical PRELIMINARY doc (`draft_zoning_floor_area_cap_sq_ft == 15000.0`); `_factor(...)` builds one explicit assumption; `_strict_json_safe(result)` asserts `json.dumps(result, allow_nan=False)` succeeds and every emitted number is finite and ≥ 0; `OBJ = RankingObjective.MAXIMIZE_ILLUSTRATIVE_USABLE_AREA`.

```python
def test_as4_overflow_huge_int_assumption_value_is_guarded_and_deterministic():
    """Regression: an unrecognized explicit assumption whose VALUE is 10**5000 (a 16610-bit
    integer whose full decimal expansion, at ~5001 digits, exceeds CPython's int->str
    conversion ceiling and would raise ``ValueError``). The overflow marker must NOT
    decimal-expand it: it is described by magnitude (bit length), so the output stays a typed
    RANKED outcome, strict-JSON-safe, byte-bounded, and byte-identical run-to-run - never an
    unguarded decimal ``repr`` that crashes the sanitizer."""
    document = _preliminary_document()
    huge = 10**5000  # decimal repr would exceed the int->str ceiling and raise ValueError
    tainted = {
        "key": "note",
        "assumption_type": "note",  # unrecognized -> surfaced but NOT applied, candidate scorable
        "value": huge,
        "unit": "ratio",
        "rationale": "explicit but astronomically large value",
    }
    sets = [[tainted], [_factor("utilization_factor", 0.8)]]
    result = rank_scenario_assumption_sets(document, OBJ, sets)

    # Typed outcome, no crash: the huge int rides through both the echo and derived breakdown.
    assert result["ranking_kind"] == RankingKind.RANKED
    assert result["candidate_count"] == 2
    # Strict-JSON-safe: no NaN/Inf/negative/overflowing number survives anywhere.
    _strict_json_safe(result)
    serialized = json.dumps(result)
    # A typed marker stands in for the raw value; it is DESCRIBED by magnitude, not expanded.
    assert "unsafe_value_removed" in serialized
    assert "bit_length" in serialized
    # The full 5001-digit decimal expansion never appears (that would be unbounded + would have
    # required the very ValueError-raising conversion the guard avoids).
    assert "0" * 100 not in serialized
    # Repeated call is byte-identical (deterministic even with the pathological value).
    again = rank_scenario_assumption_sets(_preliminary_document(), OBJ, copy.deepcopy(sets))
    assert serialized == json.dumps(again)


def test_as4_object_dict_key_assumption_value_is_typed_and_deterministic():
    """Regression: an unrecognized explicit assumption whose VALUE is a dict keyed by an
    ORDINARY OBJECT (not a JSON-safe key). The key must NOT be rendered through its
    address-bearing ``repr`` (``<... at 0x...>``): that is non-JSON-safe context AND embeds a
    transient object id, breaking byte-identical determinism. The sanitizer must replace it
    with a deterministic typed token, keeping the output RANKED, strict-JSON-safe, and
    byte-identical run-to-run."""
    document = _preliminary_document()

    class _ObjKey:
        pass

    def _sets():
        tainted = {
            "key": "note",
            "assumption_type": "note",  # unrecognized -> surfaced but NOT applied
            "value": {_ObjKey(): "nested"},  # an ordinary object as a dict KEY
            "unit": "ratio",
            "rationale": "explicit but unserializable dict key",
        }
        return [[tainted], [_factor("utilization_factor", 0.8)]]

    result = rank_scenario_assumption_sets(document, OBJ, _sets())

    # Typed outcome, no crash; would raise on a raw object key without sanitization.
    assert result["ranking_kind"] == RankingKind.RANKED
    assert result["candidate_count"] == 2
    _strict_json_safe(result)
    serialized = json.dumps(result)
    # The object key is replaced by a deterministic typed token that names the type only ...
    assert "__unsafe_key__" in serialized
    assert "_ObjKey" in serialized
    # ... and NEVER an address-bearing repr (which would be non-deterministic run-to-run).
    assert " at 0x" not in serialized
    # A FRESH object each call still yields byte-identical output (type-only, no id leaked).
    again = rank_scenario_assumption_sets(_preliminary_document(), OBJ, _sets())
    assert serialized == json.dumps(again)
```

The revision-2 huge-int coverage is ALSO folded into the parametrized `test_as4_malformed_assumption_value_is_typed_and_json_safe`, whose `bad_value` list now includes `pytest.param(10**5000, id="pow10_5000")` and `pytest.param(-(10**5000), id="neg_pow10_5000")` (explicit ids because pytest's own id generation would otherwise `str()` them and trip the same ceiling). Revision-1 regressions (`test_as1_equal_score_reordered_key_dicts_are_input_order_independent`, `test_as4_unsupported_object_assumption_value_is_typed_and_json_safe`, `test_as5_literal_verified_objective_is_invalid_and_never_emitted`) are unchanged and still pass.

## Bounded review-coverage map — supervisor collection manifest (revision 2)

The decisive revision-2 bodies are embedded verbatim above (the D1/D2 strict-JSON-safety sanitizer,
candidate build + total ordering, objective suppression, the COMPLETE public entry point, and BOTH
dedicated revision-2 regression tests). To give the G-wave COMPLETE review coverage without
duplicating the whole module/test file in this report (packet size), the REMAINDER is not re-pasted;
its EXACT current working-tree line ranges are enumerated below so the supervisor/orchestrator can
collect digest-bound excerpts. No code changed for this map. Line numbers are the current working
tree — `ranking.py` = 673 lines, `test_scenario_ranking.py` = 639 lines — re-confirmed green by the
documented suite this pass. The embedded sanitizer excerpt above is SYMBOL-contiguous, not
byte-contiguous: the two `#:` module-doc-comment blocks (ranking.py `187–192` and `236–240`) and the
`_UNSAFE_REPR_LIMIT` / `_bounded_repr` preamble (`175–184`) were not reproduced and are in the
collect set. Digest binding is the supervisor's step over the COMMITTED bytes at the gate (ADR-005:
the producer neither commits nor hashes; the native-tool preference admits only the documented pytest
command here), so no hash value is asserted by the producer.

### `services/api/app/scenario/ranking.py` (673 lines) — per-symbol coverage

| Symbol / block | Lines | In this report? |
|---|---|---|
| Module docstring (hard-boundary contract) | 1–55 | omitted → collect |
| Imports + `__all__` | 57–73 | omitted → collect |
| `RankingObjective` | 79–92 | omitted → collect |
| `RankingKind` | 95–103 | omitted → collect |
| `NEVER_VERIFIED_COVERAGE_CEILING` | 106–107 | omitted → collect |
| `RANKING_LABEL` | 109–117 | omitted → collect |
| `CANDIDATE_LABEL` | 119–123 | omitted → collect |
| `_OBJECTIVE_LABELS` | 125–131 | omitted → collect |
| `_is_number` | 137–139 | omitted → collect |
| `_finite_float` | 142–153 | omitted → collect |
| `_non_negative_finite_float` | 156–161 | omitted → collect |
| `_positive_finite_float` | 164–169 | omitted → collect |
| `_UNSAFE_REPR_LIMIT` (comment + const) | 175–177 | omitted → collect |
| `_bounded_repr` | 180–184 | omitted → collect |
| `_INT_DECIMAL_SAFE_BITS` comment | 187–192 | omitted → collect |
| `_INT_DECIMAL_SAFE_BITS` const | 193 | EMBEDDED (§sanitizer) |
| `_safe_scalar_repr` | 196–215 | EMBEDDED |
| `_unsafe_marker` | 218–233 | EMBEDDED |
| `_UNSAFE_KEY_TOKEN_PREFIX` comment | 236–240 | omitted → collect |
| `_UNSAFE_KEY_TOKEN_PREFIX` const | 241 | EMBEDDED |
| `_unsafe_key_token` | 244–250 | EMBEDDED |
| `_safe_key` | 253–270 | EMBEDDED |
| `_json_safe` | 273–301 | EMBEDDED |
| `_json_safe_mapping` | 304–321 | EMBEDDED |
| `_bounded_coverage_status` | 327–335 | omitted → collect |
| `_base_lineage` | 338–348 | omitted → collect |
| `_normalize_objective` | 354–365 | omitted → collect |
| `_score_maximize_usable_area` | 368–392 | omitted → collect |
| `_OBJECTIVE_SCORERS` | 395–398 | omitted → collect |
| `_content_key` | 404–419 | omitted → collect |
| `_build_candidate` | 422–476 | EMBEDDED |
| `_sort_key` | 479–489 | EMBEDDED |
| `_order_candidates` | 492–499 | EMBEDDED |
| `_safe_objective_echo` | 505–515 | EMBEDDED |
| `_invalid_result` | 518–537 | omitted → collect |
| `_empty_result` | 540–557 | omitted → collect |
| `rank_scenario_assumption_sets` | 560–673 | EMBEDDED |

**Omitted contiguous ranges to collect (ranking.py):** `1–192`, `236–240`, `324–421`, `502–504`,
`518–559`. Everything else in `193–673` is embedded above.

### `services/api/tests/scenario/test_scenario_ranking.py` (639 lines) — per-test coverage

| Symbol / block | Lines | In this report? |
|---|---|---|
| Module docstring | 1–9 | omitted → collect |
| Imports (`NOT_VERIFIED_DISCLAIMER`, `build_scenario`, `derive_practical_usable_range`, `rank_scenario_assumption_sets`, …) + `OBJ` | 11–31 | omitted → collect |
| `_preliminary_document` | 39–41 | omitted → collect |
| `_factor` | 44–51 | omitted → collect |
| `_coverage_values` | 54–64 | omitted → collect |
| `_all_strings` | 67–77 | omitted → collect |
| `_all_numbers` | 80–90 | omitted → collect |
| `_strict_json_safe` | 93–98 | omitted → collect |
| AS-1 `test_as1_ordering_is_score_descending_with_stable_ranks` | 106–121 | omitted → collect |
| AS-1 `test_as1_byte_identical_across_input_reorderings_and_ties` | 124–146 | omitted → collect |
| AS-1 `test_as1_identical_input_is_byte_identical` | 149–154 | omitted → collect |
| AS-1 `test_as1_equal_score_reordered_key_dicts_are_input_order_independent` (rev-1 regression) | 157–189 | omitted → collect |
| AS-2 `test_as2_named_objective_and_transparent_components` | 197–217 | omitted → collect |
| AS-2 `test_as2_top_candidate_never_travels_without_its_objective` | 220–228 | omitted → collect |
| AS-3 `test_as3_ranks_only_supplied_sets_never_fabricates` | 236–246 | omitted → collect |
| AS-3 `test_as3_empty_sets_ranks_the_raw_scenario_not_a_fabrication` (2 params) | 249–262 | omitted → collect |
| AS-3 `test_as3_not_derivable_candidate_is_ranked_last_and_flagged` | 265–281 | omitted → collect |
| AS-4 `test_as4_unknown_or_malformed_objective_is_invalid` (7 params) | 289–305 | omitted → collect |
| AS-4 `test_as4_no_cap_document_is_typed_empty_with_reason` (3 params) | 308–323 | omitted → collect |
| AS-4 `test_as4_malformed_assumption_sets_container_is_invalid` (4 params) | 326–333 | omitted → collect |
| AS-4 `test_as4_malformed_individual_set_is_flagged_not_scorable_no_crash` (5 params) | 336–347 | omitted → collect |
| AS-4 `test_as4_degenerate_document_is_typed_no_crash` | 350–355 | omitted → collect |
| AS-4 `test_as4_mixed_key_dict_entry_does_not_crash_the_tie_break` | 358–369 | omitted → collect |
| AS-4 `test_as4_malformed_assumption_value_is_typed_and_json_safe` (8 params; **rev-2** `pow10_5000`@383, `neg_pow10_5000`@384) | 372–413 | omitted → collect |
| AS-4 `test_as4_unsupported_object_assumption_value_is_typed_and_json_safe` (rev-1 regression) | 416–439 | omitted → collect |
| AS-4 `test_as4_overflow_huge_int_assumption_value_is_guarded_and_deterministic` (**rev-2 regression**) | 442–475 | EMBEDDED (§new tests) |
| AS-4 `test_as4_object_dict_key_assumption_value_is_typed_and_deterministic` (**rev-2 regression**) | 478–514 | EMBEDDED (§new tests) |
| AS-5 `test_as5_ranking_is_never_verified_and_honestly_labelled` | 522–539 | omitted → collect |
| AS-5 `test_as5_incoming_verified_coverage_is_capped_to_conditional` | 541–548 | omitted → collect |
| AS-5 `test_as5_literal_verified_objective_is_invalid_and_never_emitted` (rev-1 regression) | 551–567 | omitted → collect |
| AS-6 `test_as6_inputs_are_byte_unchanged_and_not_aliased` | 575–592 | omitted → collect |
| AS-6 `test_as6_score_uses_only_surfaced_numbers_no_recompute` | 595–610 | omitted → collect |
| AS-7 `test_as7_ranked_output_is_strict_json_safe` | 618–626 | omitted → collect |
| AS-7 `test_as7_ranking_consumes_derive_breakdown_for_every_candidate` | 629–638 | omitted → collect |

**Omitted contiguous ranges to collect (tests):** `1–441`, `515–639`. Only `442–514` (the two
dedicated revision-2 regressions) is embedded above. AS-5 (`522–567`), AS-6 (`575–610`), and AS-7
(`618–638`) are entirely within the collect set, as are the AS-4 rev-2 parametrized huge-int
additions (`pow10_5000`/`neg_pow10_5000`, lines `383–384` inside `372–413`) and the three revision-1
regressions (`157–189`, `416–439`, `551–567`).

### Supervisor digest recipe (orchestrator-run; not executed by the producer)

After the orchestrator commits the working tree at the gate, bind each file and each range — for
example:
- Whole file: `git hash-object services/api/app/scenario/ranking.py` and `… test_scenario_ranking.py` (or `sha256sum` of each file for a content hash).
- Omitted ranking ranges: `sed -n '1,192p;236,240p;324,421p;502,504p;518,559p' services/api/app/scenario/ranking.py | sha256sum`.
- Omitted test ranges: `sed -n '1,441p;515,639p' services/api/tests/scenario/test_scenario_ranking.py | sha256sum`.
- Embedded spans (to prove the report excerpts equal the committed file): ranking `193,321p` (minus the noted `#:` comment gaps) + `422,499p` + `505,515p` + `560,673p`; tests `442,514p`.

With the embedded excerpts (report evidence) plus the enumerated ranges (committed-file evidence), the
reviewer has the FULL module and FULL test file under review with no source duplicated twice here.

## Recorded execution results vs. unexecuted (reasoned) assertions

**RECORDED (executed; transcript-backed).** The documented command
`python -m pytest services/api/tests/scenario` → **`173 passed`**: originally `173 passed in 2.92s`,
and **re-confirmed at the current working tree in this evidence pass at `173 passed in 2.60s`**
(Python 3.11.9 / pytest 8.4.2; 173 items collected; `test_scenario_ranking.py` contributes 49 items =
124 pre-existing + 49). This is the ONLY executed, transcript-backed result in this submission; it
proves the POST-fix suite — including both new revision-2 regressions and the two new `10**5000`
parametrized cases — is green at the current tree.

**UNEXECUTED / REASONED (no captured transcript).** The claim that the two new regressions FAIL on the
pre-fix code is an analytical red/green design rationale, NOT a recorded run: no pre-fix red transcript
exists in this evidence set, the D1/D2 fixes are already applied to the working tree, and this bounded
pass makes no code change to produce a red run (none is requested for truncation). Reasoning only:
pre-fix `_unsafe_marker("overflow", …)` did `repr(10**5000)` → `ValueError` (CPython int→str ceiling),
so `test_as4_overflow_huge_int_…` and the `pow10_5000`/`neg_pow10_5000` params would ERROR; pre-fix
`_safe_key` fell back to `repr(<object>)` → `<… at 0x…>`, so `test_as4_object_dict_key_…` would fail
its `" at 0x" not in serialized` and byte-equality asserts. If the gate requires a captured pre-fix red
run, that is a separate orchestrator step against the pre-fix revision, outside this bounded evidence
pass.

## Boundaries honored

- **Contract-free & read-only:** only `ranking.py`, its `__init__.py` facade export, and its test file changed; `builder.py`/`models.py`/`constants.py`/`contract.py`/**`derive.py`**/`packages/contracts/**` untouched and consumed read-only; the canonical cap is transported verbatim (never recomputed/relabelled); output never emits `verified`; `needs_review` + disclaimer lineage preserved; deterministic byte-identical output independent of input order — now proven for equal-score reordered-key dicts, huge-int values, AND ordinary object dict keys.
- **Explicit assumptions preserved:** the sanitizer is the identity on well-formed values/keys; only malformed VALUES (NaN/Inf/negative/overflow/unserializable) and non-JSON-safe KEYS (object / non-finite / huge int) are replaced by typed markers/tokens. Deep-copied inputs stay byte-unchanged and un-aliased.
- **AI-boundary honesty:** ranking orders only explicit caller assumption-sets, invents no scenario/assumption/alternative; every "best"/top card names its objective; scores are ILLUSTRATIVE from the draft cap, never Verified/feasible.
- **This producer did NOT self-accept.** Evidence is submitted for the independent G0/G1/G3/G4/G5 gate wave (code-reviewer, qa-engineer, security-reviewer); the orchestrator commits, gates, and accepts.
