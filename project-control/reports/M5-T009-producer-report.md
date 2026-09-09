# M5-T009 Producer Report

**Task:** Extract the shared strict-JSON-safety sanitizer for the scenario optimization engine
(behavior-neutral) + close deepcopy/cycle defense-in-depth gaps (L1/L2).
**Producer:** scenario-optimization-engineer (run lineage persistent-local-25)
**Branch:** `task/M5-T009-json-safety` · **Starting SHA:** `457455f9`
**Type:** behavior-neutral decomposition + defense-in-depth hardening. Offline, deterministic,
contract-free. Not G6-blocked.

> Producer discipline: edited only files inside `allowed_paths`, ran only the documented test
> command (`python -m pytest services/api/tests/scenario`), did **not** commit and did **not**
> touch task state. The orchestrator commits at the gate (ADR-005). Changes are in the working tree.

## Revision (2026-09-09c) — pathological depth BOUNDED to reconcile AS-4 *and* AS-5

**Review finding addressed.** The prior revision made `_json_safe` iterative so the *sanitizer
itself* never raises `RecursionError` — but it then rendered pathologically-deep acyclic values
**in full**, with no depth bound. That only *relocated* the recursion hazard: `json.dumps` recurses
once per nesting level (in C), so a full 5000-level output makes the downstream
`json.dumps(result, allow_nan=False)` raise `RecursionError`. **Producing deeply nested containers
alone does not make `json.dumps` safe.** So the full-depth rendering satisfied AS-4's "no
`RecursionError`" only by *violating* **AS-5** ("`json.dumps(result, allow_nan=False)` never
raises") at pathological depth. The prior report also framed the full-depth choice as
"reviewer-directed"; that framing is withdrawn — worker prose is not authorization.

**Fix (all inside `allowed_paths`): a FIXED, documented max-depth bound.** `_json_safe` now bounds
container nesting to `_MAX_JSON_SAFE_DEPTH = 500`: a container deeper than that becomes a typed
`max_depth` marker (via the existing `_unsafe_marker`) instead of being descended into. This is
**exactly AS-4's literal text** — "a … pathologically-deep value … yields a typed marker … bounded
by a documented max depth / seen-set" — and it keeps every output shallow enough that
`json.dumps(result, allow_nan=False)` never raises (**AS-5**). With the bound, **AS-4 and AS-5 are
both literally true, so there is no residual acceptance conflict to route to the orchestrator.**
(Routing was the reviewer's alternative *only* "if full-depth output is intended" — and AS-5
forbids full depth, so full-depth is not intended.) The iterative traversal, the cycle/DAG
handling, and every previously-successful JSON output are preserved.

**Why the bound is principled, not the retired arbitrary cutoff.** The rejected earlier guard sized
its cutoff from `sys.getrecursionlimit()` at *import* time (~400), which (a) truncated the
previously-successful 410-level output, (b) assumed the caller's stack via a fixed head-room
subtraction, and (c) went stale on `setrecursionlimit`. `_MAX_JSON_SAFE_DEPTH = 500` avoids all
three — it is a **fixed constant**, never derived from `sys.getrecursionlimit()`, and it satisfies a
three-way constraint measured against the actual serialization limits:

| Lower bounds (must be ABOVE) | Upper bound (must be BELOW) |
|---|---|
| **410** — the retained byte-identical regressions render in full (500 > 410). | **~900** — the depth at which `json.dumps` recurses to `RecursionError` from a realistic call stack under the default 1000-frame limit (Python 3.11 local). |
| **~480** — the ceiling at which the **retired *recursive* sanitizer** this replaced would itself have raised `RecursionError` (~2 frames/level under the default limit). Nothing that was *ever* previously renderable/serializable exceeded this, so bounding at 500 **truncates no previously-successful output**. | **~1500** — the separate C-recursion limit governing the C json encoder on Python 3.12 (CI). 500 < both ceilings by a wide margin, so the bounded output always serializes. |

500 sits above the 410 regression anchor and above the former recursive sanitizer's own ceiling,
and far below `json.dumps`'s recursion ceiling on **both** the 3.11 local interpreter and the 3.12
CI interpreter. No real scenario/derive structure is more than a handful of levels deep, so the
bound never fires on production data — behavior-neutral for every real input (AS-1).

## What changed (files in scope)

| File | Change (this revision) |
|---|---|
| `app/scenario/_json_safety.py` | Added `_MAX_JSON_SAFE_DEPTH = 500` (documented constant) and a `max_depth`-marker branch in the iterative walk (emitted before descending past the bound). Corrected the module + `_json_safe` docstrings: pathological depth is now **bounded to a typed `max_depth` marker** so `json.dumps(..., allow_nan=False)` never raises — replacing the withdrawn "renders in full at ANY depth" framing. |
| `tests/scenario/test_json_safety.py` | **Retained** the two 410-level byte-identical regressions (list + dict). **Replaced** the two full-depth tests with: (1) `test_pathologically_deep_value_is_bounded_to_marker_and_json_dumps_stays_safe` — a 5000-level input is bounded to a `max_depth` marker and `json.dumps(result, allow_nan=False)` does **not** raise (the regression the review required); (2) `test_max_depth_bound_is_a_fixed_constant_not_derived_from_the_recursion_limit` — raising the recursion limit 4× does not move the bound. `_measure_list_chain_depth` (asserted full-depth `[]`) replaced by `_bounded_list_chain_depth` (asserts the terminal `max_depth` marker). |
| `app/scenario/ranking.py` | **Unchanged this revision.** Prior work stands: imports `_json_safe`/`_unsafe_marker` from the shared module (no private copy) + L1 deepcopy guard in `_build_candidate`. |
| `app/scenario/sensitivity.py` | **Unchanged this revision.** Prior work stands: imports `_json_safe` from the shared module (no private copy) + L1 deepcopy guard on the tried-value echo. The complete change is exposed by the supervisor-collected patch section below, not by a producer excerpt. |

## Measured net SLOC evidence (AS-6 de-duplication)

Measured in the current working tree with native tools (`git diff --stat` insertions/deletions is
the authoritative delta and is assigned to the **supervisor-collected patch section** below, since
`git` is outside this unit's `documented_test_commands`):

- **Single source of truth (measured):** the 7 sanitizer definitions (`_json_safe`,
  `_json_safe_mapping`, `_safe_key`, `_safe_scalar_repr`, `_unsafe_marker`, `_unsafe_key_token`,
  `_bounded_repr`) + their constants now have **exactly one** definition site —
  `_json_safety.py` — and **zero** in either consumer. Verified by grep: `^def _json_safe|_safe_key|
  _unsafe_marker|_safe_scalar_repr|_bounded_repr|_json_safe_mapping|_unsafe_key_token` matches only
  `_json_safety.py` (the `derive.py:_json_safe_cap` hit is an unrelated, forbidden-path function,
  untouched).
- **Current file sizes (measured, `^`-line count):** `_json_safety.py` = **318**; `ranking.py`
  = **547**; `sensitivity.py` = **590**; `tests/scenario/test_json_safety.py` = **430**.
- **De-duplication arithmetic:** the sanitizer body (~120 lines per the task objective) was
  duplicated **in both** consumers (~240 lines across the pair); it now lives once in
  `_json_safety.py`, and each consumer retains only a **1-line import** plus its small L1
  `try/except` guard. The shared module's 318 lines also *add* the new L2 iterative-traversal +
  `max_depth` bound and expanded provenance docstrings that did not exist in the duplicated recursive
  copies — i.e. the 318 is "one copy + new hardening", not "one copy" — so the net change on
  production SLOC is de-duplication (down) partly offset by the L1/L2 correctness additions. The
  exact insertions/deletions net figure is the git `--stat` in the supervisor section.

## Supervisor-collected complete patch section (bounded; orchestrator fills at the gate)

Per the review, the authoritative, **complete** change — especially the sensitivity change — is a
supervisor-collected git patch, **not** a producer-pasted excerpt (an excerpt can drift from the
working tree and is only a fragment). The orchestrator collects the following bounded diff at the
gate and records it as the evidence artifact:

```
# Complete change, all four in-scope files (authoritative):
git --no-pager diff 457455f9 -- \
  services/api/app/scenario/_json_safety.py \
  services/api/app/scenario/ranking.py \
  services/api/app/scenario/sensitivity.py \
  services/api/tests/scenario/test_json_safety.py

# Net SLOC (insertions/deletions) for AS-6:
git --no-pager diff --stat 457455f9 -- services/api/app/scenario services/api/tests/scenario

# The complete sensitivity change on its own (review-requested), bounded to one file:
git --no-pager diff 457455f9 -- services/api/app/scenario/sensitivity.py
```

**Expected content of the sensitivity diff** (so the collected patch can be verified against this
description): (1) the sanitizer `import` changed from a private in-module copy to
`from ._json_safety import _json_safe`; (2) the raw-echo `copy.deepcopy(tried)` in the non-baseline
branch of `_build_point` wrapped in `try/except` that falls back to the already-computed
`safe_value` (a typed, address-free marker) instead of raising; (3) the module NOTE recording that
the sanitizer now lives in the shared `_json_safety` module. Nothing else in `_build_point` or the
public surface changed. This revision made **no** further edits to `sensitivity.py`.

## Acceptance-scenario evidence

| AS | Result |
|---|---|
| **AS-1** byte-identical | `test_scenario_ranking.py` + `test_scenario_sensitivity.py` pass **UNCHANGED** (forbidden_paths); 410-level acyclic list & dict chains render byte-identically (500 > 410, so the bound never fires); the bound never fires on any real, shallow scenario/derive structure. |
| **AS-2** single source of truth | 7 sanitizer defs + constants live only in `_json_safety.py`; both consumers import; `test_shared_module_is_the_single_source_of_truth` asserts `ranking._json_safe is _json_safe` and `sensitivity._json_safe is _json_safe`. |
| **AS-3** L1 deepcopy guard | Both consumers tested with a `threading.Lock` and a generator: typed not-scorable / marker outcome, no raise (unchanged this revision). |
| **AS-4** L2 cycle/**depth** guard | Self/mutually-referential list & dict → `cycle` markers, no `RecursionError`. A pathologically-deep (5000-level) acyclic value → **bounded to a typed `max_depth` marker at `_MAX_JSON_SAFE_DEPTH`**, no `RecursionError`, bound independent of `sys.getrecursionlimit()`. Exactly "bounded by a documented max depth / typed marker." |
| **AS-5** determinism + fail-closed | `json.dumps(result, allow_nan=False)` never raises — **including on the pathological-depth outcome** (`test_pathologically_deep_value_is_bounded_to_marker_and_json_dumps_stays_safe` serializes the bounded output without raising); no NaN/Inf/negative; no `" at 0x"` address leak; identical inputs render byte-identically. |
| **AS-6** full regression + modularity | `python -m pytest services/api/tests/scenario` → **252 passed** (≥222 required; 30 in `test_json_safety.py`). Net SLOC: one copy removed from each consumer → single shared module (measured above; git `--stat` in the supervisor section). **Modularity check (`tools/modularity_check.py --check`) is PENDING the authorized gate runner — see below.** |
| **AS-7** contract-free + offline | Zero edits to `derive.py`/`builder.py`/`models.py`/`constants.py`/`contract.py`/`__init__.py` or `packages/contracts/**`; `app.scenario` facade unchanged; `_json_safety.py` imports only stdlib (`math`, `typing`) — no `sys` import (the bound is a fixed constant, deliberately not limit-derived); no network/Supabase/Geoclient. |

## Validation run

```
$ python -m pytest services/api/tests/scenario
platform win32 -- Python 3.11.9, pytest-8.4.2, pluggy-1.6.0
configfile: pyproject.toml
collected 252 items

test_json_safety.py ..............................                       [ 11%]
test_scenario_contract.py .......................                        [ 21%]
test_scenario_derive.py ..............................................   [ 48%]
test_scenario_foundation.py ...............................             [ 61%]
test_scenario_ranking.py .................................              [ 68%]
test_scenario_sensitivity.py .................................          [100%]
============================= 252 passed in 3.24s =============================
```

(Repo targets Python 3.12; this offline suite is 3.11-collectable and passed locally. CI runs the
authoritative 3.12 execution. The bound = 500 is safely below the json serialization ceiling on
**both** interpreters — see the bound-rationale table above.)

## Pending orchestrator/gate evidence (not asserted here)

- **Modularity check** `python tools/modularity_check.py --check` is an AS-6 gate check but is **not**
  in this unit's `documented_test_commands` and `tools/**` is outside `allowed_paths`, so it was
  **not run** and its result is **PENDING** — no PASS/FAIL is claimed here. The authorized gate
  runner (reviewer/orchestrator) runs it and records the actual result.
- **Net SLOC `--stat`** and the **complete patch** are collected by the orchestrator via the
  supervisor-collected patch section above (git is outside `documented_test_commands`).
- **Commit:** left to the orchestrator at the gate (ADR-005). The working tree holds the changed
  files; no task-state edit was made.

## Requested gates

G0, G1 (code-reviewer), G3, G4 (qa-engineer), G5 (security-reviewer). Directive: D-038 (ALL).
