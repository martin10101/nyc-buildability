# G5 SECURITY/ROBUSTNESS GATE REPORT — M5-T005

_Reviewer-returned content, preserved verbatim (transport entity-decoding only). Reviewer: security-reviewer (independent, read-only, producer ≠ reviewer)._

- **Gate ID:** G5 (security/robustness)
- **Task ID:** M5-T005
- **Reviewer:** security-reviewer (read-only, independent; producer = scenario-optimization-engineer)
- **Result: PASS** (3 LOW hardening findings, none blocking, none reachable via the trusted pipeline)
- **Reviewed identity:** frozen worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m5t005`, HEAD `cdd7165d3fef6b43ca72f48f6bd5427cce0e2103`, clean.

## Summary

This is a **pure deterministic offline service function** (no I/O, network, auth, DB, storage, secrets, or LLM), so classic web-security checks are N/A by construction. Independently reproduced at cdd7165d: untrusted-input handling (every field guarded via `_as_dict`/`.get()`; adversarial None/list/int/str/float/bool/object top-level → typed `not_derivable`, no crash); fail-closed on all factor classes (NaN/±Inf/neg/zero/>1/non-numeric/bool/None/nested/huge-int → typed `invalid_assumption`, strict-JSON-safe); underflow discipline (RT-6 subnormal survives, RT-7 not_derivable — no misleading successful 0.0); no injection sink; no input mutation, canonical cap (immutable scalar) never aliased; no new dependency, no eval/exec/file/net/env; determinism incl. order-independence; never-Verified enforced on every outcome. `python -m pytest tests/scenario -q` → 102 passed. Producer commit touches only the 4 allowed_paths files.

## LOW findings (defense-in-depth; non-blocking; NOT reachable via build_scenario)

**LOW-1 — Non-finite/negative cap transported verbatim into `canonical_cap_sq_ft`, making output not strict-JSON-safe.** `derive.py:159-176` (`_not_derivable`) and `:216-227` set `canonical_cap_sq_ft = cap_raw` verbatim even when `cap_raw` is NaN/±Inf/negative. `derive({"draft_zoning_floor_area_cap_sq_ft": float('nan')})` → `not_derivable` with `canonical_cap_sq_ft = nan`; `json.dumps(out, allow_nan=False)` (the FastAPI JSONResponse mode) raises. **Reachability: NOT reachable via `build_scenario`** — the builder computes `_positive_finite_float(cap_raw)` and routes malformed/non-finite/negative caps to a fail-closed branch with `cap_value=None` (`builder.py:390-392,433-437`); end-to-end proof: cap=`None`, output strict-JSON-safe, for NaN/Inf/−5. AS-3/RT-3/RT-4 strict-JSON-safety only exercise factor/container paths (cap fixed 15000.0), so a malformed-cap path is uncovered. **Remediation (recommended, non-blocking):** transport the cap only when finite (else `None` + reason), or document the `build_scenario`-produced precondition; add a strict-JSON-safety test over a non-finite/negative injected cap.

**LOW-2 — `_copy_assumption` shallow-copies `value`/`unit`/`rationale`; a nested-mutable value in an *unapplied* assumption is aliased to the input.** `derive.py:120-129`. Docstring claims "never aliases the input," but an unapplied assumption with `value={"nested":[...]}` yields `derived["unapplied_assumptions"][0]["value"] is document["assumptions"][0]["value"]` → True. **Scope-limiting:** applied factors are always scalar floats; the canonical cap is immutable scalar and never aliased; derive() never mutates. **Remediation (recommended):** `copy.deepcopy` value/unit/rationale, or narrow the docstring claim to "scalar fields."

**LOW-3 (informational) — Unbounded `repr()`/`str()` echo of raw input into reason strings.** `derive.py:224,274,373`. A 100k-char value yields a ~100k-char reason. Values are repr()/str()-escaped (no injection sink). Only risk is log/UI bloat. **Remediation (optional):** truncate echoed raw input.

## Conclusion

**PASS.** At cdd7165d, `derive_practical_usable_range` is pure, deterministic, offline, fail-closed on all adversarial numeric input (confirmed live), read-only with the canonical cap never mutated/aliased, never-Verified, no new dependency, no eval/exec/file/network/env. The three LOW findings are defense-in-depth hardening, none reachable through the trusted `build_scenario` pipeline (proven end-to-end) and none causing a crash. No rework required for PASS; LOW-1/LOW-2 recommended as fast one-line follow-up hardening.
