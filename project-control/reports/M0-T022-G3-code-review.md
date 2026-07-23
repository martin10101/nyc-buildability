# G3 Gate Report — M0-T022 (Owner Mission-Control dashboard, read-only engine)

_Verbatim independent reviewer return (code-reviewer); transport entities decoded only._

VERDICT: PASS

- Gate: G3 (code-reviewer — engine correctness + code quality)
- Task: M0-T022
- Frozen review SHA: 7ea8b0d22a8300938f85452be19b85f8a8cc8e3a (== 6c501aa)
- Scope reviewed: `apps/web/src/lib/dashboard/**` + co-located tests, cross-checked against `tools/project_control.py`, `tools/current_state.py`, `tools/validate_product_map.py`, and `project-control/product-map.json`.
- Method: static review + reproduction of every hand-computed expectation in `apps/web/src/lib/dashboard/__tests__/engine.test.ts` against `apps/web/src/test-support/dashboard/fixtures.ts`. Web build/vitest/Playwright not run locally (thin-client); relied on CI run 29976490909 GREEN on all 11 jobs as corroborating evidence.

## What I verified (all correct)

Engineering % math (progress.ts:47-89, 91-143) — `Σ eng_weight × clamp01(Σ progress_percent / (100 × max(contracted, planned)))`. Reproduced on the fixture: sys_a `(100+90)/(100×2)=0.95`, sys_b `(100+0)/200=0.5`; `50×0.95 + 50×0.5 = 72.5 → percentWhole 73`. Matches AS-5. `clamp01` applied; division-by-zero guarded by the `expectedCount === 0 → null` branch (progress.ts:61).

Launch % math + cap logic (progress.ts:70-82) — `Σ launch_weight × clamp01(accepted / max(contracted, planned))` then reduced by `capStillApplies`. Reproduced: sys_a `1/2=0.5` (no cap); sys_b `1/2=0.5` capped to 0.15 because `readinessCap.onTask=M1-T001` has no G6 PASS; `50×0.5 + 50×0.15 = 32.5 → 33`. Matches AS-6, and launch < engineering (AS-6). `capStillApplies` is correctly conservative: no cap object → false; unknown target task → cap applies; target present without the gate in `passedGates` → cap applies (progress.ts:36-45).

UNKNOWN never coerced to 0 (progress.ts:60-67, 105-136) — a member task with an unrecognized status makes the whole system `engCompletion/launchReadiness = null` with `dataQuality:'unknown'`; the aggregate accumulates its weight into `unverifiedWeight` (not as 0), sets overall `dataQuality:'partial'`, and returns `percentWhole = null` (headline shown only when `dataQuality === 'ok'`). Verified against the AS-18/AS-16 tests (`unverifiedWeight === 50`, `percentWhole` null). Note the correct distinction: a not-started system with `plannedCount>0` legitimately contributes a real `0` (verifiable), while an unverifiable system contributes `null`.

Gate state + acceptance-eligibility (model.ts:121-155) — faithfully reproduces `accept()` in project_control.py:540-605: per-task gate PASS requires a record with `result==='PASS'` and, for independent gates (G1/G3/G4/G5/G6), an independent role, `reviewer!=='orchestrator'`, and `reviewer!==producer`; eligibility requires `awaiting_gate`, all required gates met, all deps `accepted`, and no open blocker referencing the task. Confirmed against M0-T009 producer-recorded-PASS test (correctly not counted) and the awaiting_gate-eligible / blocked-ineligible cases.

`_blocker_references` parity (model.ts:29-34) — the JS regex `(?<![A-Za-z0-9])ID(?!\d)` with metachar escaping mirrors project_control.py:525-537 exactly, including base-id-matches-rework-mention behavior. Only `status:open` (or empty) blockers surface (parse.ts... model.ts:100), matching AS-8.

Roster-vs-status contradiction (model.ts:159-174) — `state.json accepted_tasks` vs the task file's own status flagged both directions (error / warn), satisfying AS-18; test confirms the M0-T002 case.

parse.ts defensiveness — never throws; `coerceStatus` handles non-strings (falls to `unknown` + Issue), `ownerStatusFor` falls back to `UNKNOWN`, all coercions (`isRecord/asString/asFiniteNumber/asStringArray`) are safe; malformed product-map yields structured Issues, not exceptions (AS-3, AS-12).

health.ts independent of completion — `systemHealth`/`overallHealth` degrade on blocked tasks, open blockers, failed CI, error-severity issues, and stale/unavailable GitHub, without touching progress. Verified by the "failed CI degrades health without changing completion" and "accepted task can still be RED" tests (AS-17). progress.ts imports no GitHub input, so completion is provably file-only.

currentWork/activity/launch/membership — Current Work derives from `ACTIVE_STATUSES` lifecycle only with a deterministic primary/next ordering (currentWork.ts); activity is a control-plane event model from ledger timestamps with no raw-commit kinds and a deterministic injected `today` (activity.ts); launch blockers are derived (critical systems below readiness + open blockers), deterministically ranked (launch.ts); `membership.ts` `(from_ms − exclude) | include` exactly mirrors `validate_product_map.py` resolve_membership (line 80), with runtime orphan/duplicate anomalies surfaced as Issues rather than silently dropped.

GitHub isolation + read-only discipline — github.ts is pure parsing; githubClient.ts does unauthenticated public-repo GETs with AbortController timeout, 45s cache, and last-known-marked-STALE fallback (never fabricated; `headSha` retained on failure, AS-11); server.ts/loader.server.ts only read files (fs read/readdir/stat) and never write or invoke the CLI; assemble.ts is pure. A grep for write/mutation/secret patterns across the engine returned only the `TRUE_TOKENS` visibility constant — no `writeFile`, POST/PUT/DELETE, child_process, token/secret, or localStorage. Route (page.tsx) is a Server Component gated by `dashboardEnabled()` (non-`NEXT_PUBLIC_` flag, fail-safe off) → 404 when disabled.

Determinism/types — CI typecheck is GREEN (strict), sorts use stable id/timestamp tie-breakers, and no `any` leaks; the single `contribution as number` cast (progress.ts:110) is guarded by the preceding null-branch.

## Findings (all NON-BLOCKING)

- non-blocking · progress.ts:73-74 — the guard `if (capped !== launchReadiness || launchReadiness <= maxReadinessFraction)` is a tautology (always true whenever `capStillApplies`), so `capApplied` is always recorded when a cap is in force. Behavior is correct and intentional (transparency: show the cap even when it isn't currently reducing readiness), but the condition is dead/confusing and should be simplified to unconditionally set `capApplied`.
- non-blocking · model.ts:128 — independence check `rec.role !== 'self_check'` is slightly more lenient than `accept()`'s `role is not None and role != 'independent_review'`: a stored independent-gate record with some other non-null role (e.g. `administrative`) would count as PASS here but be rejected by the CLI. Cannot occur with real data — the CLI always writes `role='independent_review'` for G1/G3/G4/G5/G6 (project_control.py:482) — so this is a theoretical fidelity edge only.
- non-blocking · model.ts:128 — the added `rec.reviewer !== 'orchestrator'` clause is stricter than `accept()` (which relies on write-time rejection at project_control.py:468). This is fail-closed and consistent with the write-time invariant; noted for completeness, not a defect.
- non-blocking · progress.ts:135-142 — the aggregated headline percent is not clamped to [0,100]; correctness depends on the product-map invariant that `eng_weight`/`launch_weight` each sum to 100. That invariant is enforced by `validate_product_map.py` + the additive CI job (G1), so it holds in practice; a defensive clamp/assert would harden against future drift.
- non-blocking · github.ts:48 — when filtering CI runs by `headSha`, a run lacking `head_sha` is included (short-circuit on `&& asString(r.head_sha)`). Defensive and low-impact for a public-repo supplemental view.
- non-blocking · model.ts:253 / ledgerCounts — an unrecognized status is counted under `unknown` here vs its raw string in `status()`, and tasks lacking a `task_id` are skipped. For the real, valid ledger the counts reproduce `project_control.py status` and `current_state.py` rollups exactly (AS-2); the divergence only manifests on corrupt data, which is the intended UNKNOWN-surfacing behavior.

## Conclusion

The two progress numbers are deterministic, auditable, and reproducible from repository state alone; each exposes a full breakdown (weights, denominators, contributing tasks, applied caps) with whole-% headlines only when fully verifiable. Gate/acceptance/blocker/membership semantics faithfully reproduce the control-plane reference algorithms read-only, with no duplicate write path and no second source of truth. UNKNOWN/DEGRADED is never coerced to 0/complete/healthy; health is computed independently of completion; GitHub is supplemental, isolated, cached, and stale-safe. No blocking defects found. The six items above are quality/hardening notes for optional follow-up and do not affect correctness.

VERDICT: PASS

---

## Delta re-review @ b2de479 — PASS (condensed by orchestrator; full verbatim in the reviewer transcript)

The code-reviewer re-reviewed the honesty-correction delta (3 files: model.ts accepted-task short-circuit, engine.test.ts new test, fixtures.ts cap-target M1-T001→M1-T002) at frozen SHA b2de479 (CI run 29977738748 green, 11 jobs). Verified: (1) `const accepted` hoisted before the gate loop; accepted → passedGates = requiredGates, unmetGates = []; non-accepted path byte-identical to the prior strict independence rule. (2) No acceptanceEligible false-positive (`&& !accepted` forces false for accepted tasks). (3) Semantically sound vs accept() (accept() only sets accepted after all required gates PASS, tolerating legacy records). (4) **Load-bearing real-world check:** the only real readiness_cap (rules_engine, on_task M4-T001, until G6) is unaffected — M4-T001 is awaiting_gate (not accepted) with G6 required and no G6 record, so capStillApplies stays true and Launch Readiness stays capped at 0.15. No blocking defects; prior six non-blocking notes unchanged (one narrowed). **VERDICT: PASS at b2de479.**
