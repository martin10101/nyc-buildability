# M5-T011 — G5 Security/Privacy Gate RE-REVIEW (verbatim reviewer return) — PASS

Reviewer: **security-reviewer** (independent ≠ producer). Reviewed SHA `14ae88cc82d4630b8f9d9c22b2ca8857532c48f4`. **VERDICT: PASS** — supersedes the prior FAIL at `bbf3267f` (see M5-T011-G5.md for the original BLOCKING-1 finding). Transport entity-decoding applied; content otherwise verbatim.

---

# G5 Security/Privacy Gate Report (UPDATED / re-review) — M5-T011 break-even / threshold finder

- **Task:** M5-T011 — `find_scenario_threshold` (contract-free, offline)
- **Reviewed SHA:** `14ae88cc82d4630b8f9d9c22b2ca8857532c48f4` — verified `git rev-parse HEAD == 14ae88cc` on candidate/D-024-mrl-option-b (ctl24 checkout).
- **Supersedes:** prior FAIL at `bbf3267f` (BLOCKING-1: uncaught RecursionError on deeply-nested candidate).
- **Delta reviewed:** `git diff bbf3267f..14ae88cc --name-only` = exactly 2 files: breakeven.py and test_scenario_breakeven.py. No forbidden file touched.

## VERDICT: PASS

The producer applied exactly the recommended remediation and the blocking defect is reproducibly gone, with no regression and no new defect.

## Fix verification (BLOCKING-1 → resolved)

**Code delta (breakeven.py `_build_candidate`):** the recursive `echo = copy.deepcopy(generated)` at old line ~344 is removed; `echo` is now built directly from the already-fresh `_json_safe(candidate)` output (`safe_value`); the now-unused `import copy` is removed. No `sys.setrecursionlimit`. An added comment documents why the copy was redundant and harmful. Precisely the recommended fix.

**Static confirmation:** `_json_safe` returns a fresh structure that never aliases the caller and is bounded to `_MAX_JSON_SAFE_DEPTH=500`; `derive()` reads assumptions read-only (deep-copies each field internally and rejects the non-numeric factor value before touching it); the emitted row's `assumption_set` is itself a fresh re-`_json_safe` copy, independent of both the caller's domain element and the `echo` handed to derive.

**Live re-probe (14ae88cc, Python 3.11.9, default recursionlimit=1000):** the exact inputs that raised RecursionError at bbf3267f now return typed, strict-JSON-safe results:
```
deep DICT candidate(500|600|5000|10000)  kind=target_already_met  cand=2 deriv=1  json.dumps(allow_nan=False) OK
deep LIST candidate(500|600|5000|10000)  kind=target_already_met  cand=2 deriv=1  json.dumps(allow_nan=False) OK
deep candidate row: derivable=False, metric_value=None, has not_derivable_reason -> FAIL-CLOSED OK
```
(json length constant across depths — 16664 dict / 11684 list — confirming truncation at the depth bound with a `max_depth` marker: bounded and deterministic.)

**Producer's red/green test reproduced:** `test_as5_deeply_nested_candidate_is_bounded_and_json_safe` (dict/list nested 600 & 5000) → 4 passed. Closes prior LOW-1 (acceptance-pack coverage gap).

## No new defect introduced (re-verified sweep at 14ae88cc)
- Read-only / no aliasing: caller scenario_document byte-unchanged; mutating emitted `result[...]["assumption_set"]` does not reach the caller's input. Confirmed live.
- derive consumed read-only, never-Verified: normal FOUND scan unchanged (cand=4 deriv=4); tampered coverage_status="verified" → capped to "conditional" top-level and in base_lineage.
- Offline: socket-blocked scan returns a normal result; no os/socket/subprocess/requests/httpx/urllib/open/environ/supabase.
- Strict-JSON-safe / no address leak: json.dumps(result, allow_nan=False) never raised; every emitted number finite and non-negative; no ` at 0x`. Shared sanitizer still imported, not re-defined.
- Regression + modularity: pytest services/api/tests/scenario → 388 passed (384 + 4 new; 0 regression). modularity_check --check → 0 failures (breakeven.py advisory review_signal only).

## Residual (non-blocking, unchanged)
- LOW-2 (advisory, defense-in-depth): the top-level result dict is assembled from individually-sanitized parts rather than wrapped in one final `_json_safe`. No unsafe value escapes today; optional future hardening only. Not a gate blocker.

## One-line summary
PASS — remediation applied exactly; the deeply-nested-candidate RecursionError is reproducibly gone (dict & list at 500–10000 deep now yield typed fail-closed JSON-safe results), read-only/never-Verified/offline/no-leak all hold, the acceptance pack now covers the case, full suite (388) and modularity pass — M5-T011 can be accepted. Supersedes the FAIL at bbf3267f.
