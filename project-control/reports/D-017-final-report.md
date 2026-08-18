# D-017 final report — owner A-to-Z completion run (2026-08-18)

Produced by the orchestrator at the end of the D-017 execution. Everything
below is reconciled against git, the ledger, and CI — not conversational
memory. Companion records: `D-017-modularity-report.md` (Stage 9),
`D-016-directive-verification.json` (honest D-016 reconciliation),
`M0-T069-benchmark-report.{json,md}` (Stage 10 evidence),
`M0-T069-status-projection.{json,md}` (deterministic status view),
`docs/CONTEXT_PIPELINE_RUNBOOK.md` (operator guide).

## Tasks accepted and merged (this run)

| task | unit | PR | merge SHA | gate history |
|---|---|---|---|---|
| M0-T072 | Stage 1 external-config manifest binding | #227 | 0cfa85b | PASS |
| M0-T073 | permanent modularity enforcement (CI gate) | #228 | 954533d | PASS |
| M0-T074 | deterministic model routing | #229 | 612e094 | PASS |
| M0-T063 | A1 baseline/fingerprint/cache | #230 | 4435214 | PASS (flaky CI check cleared on rerun) |
| M0-T064 | A2 incremental index | #231 | 4954b79 | G3 FAIL→PASS (tsconfig stale-reuse fixed); 42/42 DCV |
| M0-T065 | B bounded context compiler | #232 | 1d159a8 | PASS; 27/27 DCV |
| M0-T066 | C subsystem/ontology resolver | #233 | 1ded78f | PASS; 24/24 DCV |
| M0-T067 | D memory graph | #234 | 40b530f | G3 FAIL→PASS (B1 path traversal fixed + probe regression test); 29/29 DCV round 2 |
| M0-T068 | E repository-intelligence views | #235 | cf65b78 | G3 FAIL→PASS (R024 gap + task-id traversal fixed); 27/27 DCV round 2 |
| M0-T069 | F benchmark/runbook/projection | #236 | 9bf1901 | PASS; 31/31 DCV |

Also merged earlier in the run: the D-017 capture itself (PR #226, 50c329a,
123 requirements verified at capture). **Ledger accepted count: 97.**
origin/main at report time: **9bf1901** (clean, synchronized; every task
branch deleted after merge).

Every unit followed the same lifecycle: contract packet bound at claim → G0
→ implement → submit at a frozen SHA → fresh independent adversarial review
(producer ≠ reviewer; two units failed round 1 on genuine defects and were
reworked with the reviewer's exact exploits as regression tests) → G3/G4/G5
→ independent directive-compliance verification (producer ≠ verifier; every
applicable D-013 row verified at the reviewed identity) → accept → merge on
green required checks (Tier A). One CI flake (a PyPI connection reset inside
the dependency age gate, which correctly failed closed) was cleared by rerun.

## Test totals (initiative scope, all green at their acceptance SHAs)

- A1+A2 battery: 63 passed / 1 skipped (recorded at A2 acceptance).
- B: 23 (15 context-pack incl. drift-lock + 8 index/tier). C: 21. D: 31
  (25 + 6 traversal-regression). E: 26 (23 + 3 rework-regression). F: 23
  (15 benchmark + 8 projection). **Initiative total ≈ 187 tests**, plus the
  full repository CI matrix (19 required check contexts) green on every
  merge.
- Modularity CI: 0 failures at every acceptance and at final main.

## Benchmark results (Stage 10 — committed evidence)

42 frozen-corpus cases across the five directive-named task shapes:
**42/42 byte-identical** to the clean-full reference (the unmodified builder;
independently re-executed by the Unit F reviewer, who also proved the
reference equals the real generator and the A1 baseline digest). Warm
no-change reparses **0 files** in all shapes; delete/rename leave no stale
nodes; corruption/interrupted-write/concurrent-writer cases all preserve a
valid generation. Measured runtime carries sample counts with median/p95,
labeled measurement evidence.

## Token measurements — honest statement

Provider-reported token usage was NOT available in the offline benchmark:
**provider token savings are UNMEASURED** and no combined savings number
exists anywhere. The only efficiency claims made are deterministic reuse
metrics (files parsed/reused; warm zero-reparse). Deterministic byte/token
estimates in the context pack are labeled estimates and never presented as
savings (D-013-R012/R053/R057).

## D-016 reconciliation (honest)

Independent directive-level verification recorded: **63/64 PASS, 1 honest
FAIL** (R062 — the `OVERNIGHT_RUNWAY_COMPLETE` session return was never
committed, so its contents cannot be verified from durable evidence, even
though all 12 of its required items are independently true in the ledger).
Full record: `D-016-directive-verification.json`. No green-washing.

## Remaining risks

- Reviewer observations carried as non-blocking follow-ups (recorded in each
  unit's review report): Unit C map-validation hardening (Windows
  absolute-prefix/case nuances), Unit D quarantine-write outside the writer
  lock (benign), Unit F p95-at-small-n formula and R062 status-mapping gaps.
  None affects correctness or any directive requirement; all are candidates
  for a routine follow-up task.
- The supervisor modules and legacy connectors remain the largest files
  (R082-frozen / baseline-covered; see the modularity report).
- The `exact-production-install` CI job remains sensitive to transient PyPI
  outages (fails closed by design; rerun clears).

## Owner actions still pending (not performable by the orchestrator)

1. **Stage 2 live-controller update (OWNER_ACTION_BUNDLE, owner-present):**
   stop supervisor → backup → copy the reviewed file delta → record-manifest
   binding of the external config → verify-controller/doctor → doctor --live
   probe with the verified Claude executable → supervised digest-bound A1
   start. The prepared, unexecuted runbook is
   `C:/Users/MLFLL/Downloads/nyc-zoning/CONTROLLER_UPDATE_RUNBOOK_2026-08-18.md`
   (verified read-only-produced; protected config sha 6aef12a9… and
   model_selection sha 0e2432c0… unchanged throughout, limited-auto disabled).
2. **D-013-R060 promotion decision:** the benchmark evidence and threshold
   proposal are on file; adopting the pipeline as promoted (and any future
   change of defaults) is the owner/control-plane decision.
3. Optional: closing D-016-R062 would require the owner to supply/commit the
   original `OVERNIGHT_RUNWAY_COMPLETE` return text as a durable artifact.

## Completion criteria status (D-017 final list)

- Protected config + model selection byte-identical: **yes** (never touched).
- Limited-auto disabled: **yes** (never enabled).
- M0-T063..M0-T069 implemented, accepted, merged: **yes** (table above).
- Incremental == clean full rebuild: **proven** (42/42 + unit suites).
- Cache generations crash-safe, outside the repo: **yes** (proven + tested).
- Context packs deterministic, bounded, stale-safe: **yes** (Unit B evidence).
- Ontology placement deterministic: **yes** (Unit C evidence).
- Memory links validated + quarantined: **yes** (Unit D evidence).
- Repository-intelligence queries evidence-backed: **yes** (Unit E evidence).
- Giant-file regressions prevented: **yes** (M0-T073 CI gate).
- Required CI green; origin/main clean and synchronized: **yes** (9bf1901).
- Runtime state + rollback documented; single operator guide: **yes**
  (`docs/CONTEXT_PIPELINE_RUNBOOK.md`).
- Controller updated + verified live: **NO — owner-present bundle pending**
  (item 1 above). This is the sole open completion criterion, and it is
  owner-gated by design.
