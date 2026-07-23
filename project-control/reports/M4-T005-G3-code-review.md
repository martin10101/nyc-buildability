# GATE REPORT — M4-T005 (G3 code gate)

**Task:** M4-T005 — internal rule-evaluation endpoint + serializer + FH-4 + installed-wheel deployability
**Reviewed SHA (frozen):** `84b50a722d518d0ae6c233ee38affedbdaaebea3` (PR #84)
**Reviewer:** code-reviewer (read-only, independent of producer)
**Verdict:** **PASS**

## Checkout / provenance note
The `git reset --hard` requested in the packet is blocked by the read-only guard (only git *inspection* is permitted). I verified equivalence instead: worktree HEAD is `f1e6772`, two commits **after** the frozen SHA, and `git diff --stat HEAD 84b50a7` shows those two commits touch **only** `project-control/` files — **zero code deltas**. `git diff 84b50a7 -- services/api/app/rules/snapshots.py` is empty. All reviewed source is byte-identical to the frozen SHA.

## Reproducible commands & outputs
- `python -m ruff check .` (services/api) → **All checks passed!**
- `python -m pytest tests/api/test_rule_evaluation_api.py tests/contracts/test_rule_evaluation_contract.py tests/rules/test_installed_deployability.py tests/rules/test_rules_fh4_temporal_parity.py tests/rules/test_zr_snapshot_bundle.py -q` → **85 passed in 6.52s**
- `python -m pytest -q` (full services/api) → **827 passed in 25.98s**
- `cmp` + `sha256sum` bundle vs docs → **IDENTICAL** (`f43504ef…8196` both)
- `git diff --stat 9e8c22c..84b50a7` → forbidden files (`properties.py`, `evaluator.py`, `integration.py`, `property_profile.schema.json`) **absent from diff = unchanged**; `registry.py` +13, `snapshots.py` ±56.

## Per-item findings

**1. Endpoint correctness — PASS.** `rule_evaluation.py`:
- Flag checked **first**, before a correlation id is minted or input touched (`:144`); disabled path returns bare `{"detail":"Not Found"}` 404 with **no** `X-Correlation-ID` header (`:109-113`), byte-indistinguishable from an unmounted route; `include_in_schema=False` (`:131`).
- Server-side rebuild only: handler signature takes `bbl` path param + injected `fetcher`/`substrate_provider` — **no request body / no browser-supplied profile**; profile built via `build_property_profile(result, spatial_intersection=substrate)` (`:226`).
- Typed error mapping mirrors the accepted property route via single-sourced `_ERROR_STATUS`/`_DEFAULT_ERROR_STATUS` imports; BBL validation is a typed 422 with zero network I/O (`:151-168`); `no_match` is a 404 result-not-error (`:206`).
- Catch-all 500 logs **type + correlation id only** — `logger.error(... stage=fetch ...)` (`:194`) and `stage=evaluate` (`:286`); `_internal_error_500` (`:116-128`) emits generic body. No `logger.exception`, no `str(exc)`, no traceback, no `TEMP-DEBUG` (grep hits are docstring/comment text).
- Strict response validation before send (`:264`), mapped to typed internal-contract 500 on failure — an invalid 200 is impossible.
- needs-review / unsupported / fail-safe are **normal 200** documents (`:284`).

**2. Serializer — PASS.** `response.py`:
- Input **by reference**: `bbl` and `input_provenance` `pop`ped into `evaluated_input`; no property profile embedded (`:151-165`). Verified `PropertyRuleEvaluation.export()` emits neither `contract_version` nor `evaluated_input`, so the trailing `**payload` spread cannot clobber the explicit root keys (no dict-ordering bug).
- Deterministic `sha256:`-prefixed fingerprint over the canonical (sorted-key, tight-separator, `allow_nan=False`) JSON of the identifying evaluator input (`:102-124`).
- `assert_not_verified(document)` boundary at `:168`.
- Offline validation against the **bundled** schema via `importlib.resources` from `app._contract_schemas.v1` (`:197-199`).
- Maps, never recomputes: consumes `evaluation.export()` and reshapes; no calculation path.

**3. FH-4 — PASS.** `registry.py:68` — `detect_rule_conflicts` short-circuits to `None` when `as_of_date is not None and not evaluator._valid_iso_date(as_of_date)`, using the exact validator the evaluate path uses. Additive, strictly fail-closed; `None` and every real date (incl. leap `2024-02-29`) unaffected; no legal rule content touched. `test_rules_fh4_temporal_parity.py` proves both-path parity.

**4. Deployability fix — PASS.** `snapshots.py:56-77` resolves the packaged `app._zr_snapshots.v1` via `resources.files(...)` with `is_dir()`+glob guard and a docs fallback; explicit `SnapshotStore(directory=…)` override preserved. `pyproject.toml:55-75` ships all four runtime data classes. ZR bundle byte-identical to `docs/research/zr-snapshots/v1/`; `docs/research/zr-snapshots/` and `app/rules/rulesets/` not in the change diff = unmodified. `test_installed_deployability.py` pins the declarations and asserts each glob resolves to real shipped files.

**5. No regressions / forbidden changes — PASS.** `properties.py`, `evaluator.py`, `integration.py`, `property_profile.schema.json` absent from the `9e8c22c..84b50a7` diff (byte-identical). Full suite 827 passed; ruff clean; existing property route + health regression tests pass.

## Defects
None (blocking or non-blocking) found.

## Verdict: **PASS.** No required corrections.
