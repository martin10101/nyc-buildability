# GATE REPORT — M5-T006 (G3 QA, independent)

_Reviewer-returned content, preserved verbatim (transport entity-decoding only). Reviewer: qa-engineer (independent, read-only, producer ≠ reviewer)._

**Verdict: PASS**

**Reviewed identity:** branch `task/M5-T006-derive-hardening` @ `817815cc9f8205fba152d3e4b684b0b036ab56f0` — HEAD confirmed == frozen reviewed SHA; working tree clean. Worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t006`.

## 1. Reproduction
`cd C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t006/services/api && python -m pytest tests/scenario -q` → **124 passed in 0.58s**. Delta vs M5-T005 baseline (102): **+22 new tests** (keyword `m5t006`), other 102 still green — **no regression**. `derive.py` 490 lines, single-responsibility, `__all__` intact.

## 2. Mutation testing — new tests are load-bearing (non-destructive, runtime monkeypatch from scratchpad; repo untouched). All 6 mutants CAUGHT:
| Mutant (guard reverted) | Effect | Test that catches it |
|---|---|---|
| M1 `_json_safe_cap`→identity (LOW-1) | canonical_cap_sq_ft=nan; json.dumps(allow_nan=False) raises | test_m5t006_low1_* |
| M2 `_copy_assumption`→shallow alias (LOW-2) | derived value IS input; input mutated | test_m5t006_low2_* |
| M3 `_bounded_echo`→identity (LOW-3 per-value) | reason grows to 100,152 chars, no marker | test_m5t006_low3_scenario_kind/factor_value/unapplied_key_* |
| M4 `_bounded_key_list_echo`→unbounded join (LOW-3 aggregate) | reason grows to 360,092 chars | test_m5t006_low3_many_unapplied_keys_* |
| M5 `_base_document` needs_review→False (DERIVED drift) | golden equality breaks | test_m5t006_as2_*_golden_baseline |
| M6 `_bounded_coverage_status`→passthrough (never-Verified) | `verified` leaks into output | test_m5t006_as5_never_verified_* |

## 3. Per-AS coverage — ALL COVERED
- **AS-1** strict-JSON-safe malformed cap: parametrized NaN/±Inf/−5/−0.5/10**400 → canonical_cap_sq_ft None + "MALFORMED CAP" reason + json.dumps(allow_nan=False) succeeds + all numbers finite/≥0; direct-call variant proves pipeline-independent; zero cap boundary transported verbatim (not nulled). Mutant M1 caught.
- **AS-2** DERIVED path unchanged / no regression (STRONG): two **full-output golden baselines** (no-assumptions + single-factor) pin the whole object AND json.dumps byte-for-byte; plus cap-transport-unchanged + RT-1/RT-2 precise-cap tests. Mutant M5 confirms golden strictness.
- **AS-3** no-alias: `unapplied["value"] is not document[...]["value"]` (explicit `is`); mutating derived leaves input == snapshot; APPLIED-path rationale also `is not`. Mutant M2 caught.
- **AS-4** bounded echo (both dimensions): per-value bound on all 3 echo sites (100k → reason <2,000 with "truncated"); aggregate count bound (20,000 keys stay under a FIXED bound). Mutants M3+M4 caught.
- **AS-5** cap value + never-Verified: −Inf cap + incoming `verified` → no `verified` anywhere, coverage_status conditional, needs_review True, disclaimer preserved. Mutant M6 caught.
- **AS-6** determinism + full regression: 4 hardened paths byte-identical across builds; 124/124 green.

## 4. Provenance / modularity
Defense-in-depth; DERIVED happy path unchanged except deepcopy (scalar fields JSON-identical) + bounded-key echo (identical to plain join for ≤12 keys); byte-equivalence substantiated by goldens. Never-Verified intact; no NaN/Inf/negative emittable; cap never mutated on fail-closed paths. derive.py 490 lines, cohesive; public `__all__` unchanged.

## 5. Advisory (non-blocking)
The two golden-baseline tests reference the module's own constant strings on the expected side, so a drift in those constant STRINGS would move both sides together. Mitigated: AS-6 independently pins substrings of DERIVED_RANGE_LABEL. No action required.

**Result: PASS** — all 6 AS covered by load-bearing tests (every mutant caught), full suite green with 22 new tests + 0 regression, DERIVED path pinned byte-for-byte.
