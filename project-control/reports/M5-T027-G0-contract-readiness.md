# M5-T027 G0 — contract readiness (orchestrator)

- Task: M5-T027 — Dependable answers 1 (D-059): unused-floor-area semantics + zero-with-buildings fail-closed + evaluation-derived labels
- Gate: G0 (contract readiness) · Reviewer: orchestrator · Result: **PASS**
- Date: 2026-09-14 · Directive refs: `D-059:R001,R002,R003,R011;D-046:R001,R002`

## Readiness checks

1. **Findings verified in code before contracting, not taken on faith.** Orchestrator confirmed
   at the live head: `unused_floor_area.py` `_nonnegative_finite_float` accepts 0 as usable with
   an explicit "vacant lot" comment and the module never consults `numbldgs` (R002 reproduced by
   the reviewer against the pure function); `constants.py` carries the hardcoded
   "draft max residential zoning floor area (R5)" wording (line ~183), "non-R5" (line ~202), and
   the universal "ZR 23-21" cap labels (lines ~29/49) while the R6–R12 rules cite ZR 23-22
   (R003); the labels call the number a zoning-floor-area difference while the input is PLUTO
   recorded gross building area (R001).
2. **Contract-schema boundary pre-scoped.** `scenario.schema.json` enum for
   `not_computable_reason` is closed (`missing_existing_building_area`,
   `existing_building_area_unusable`, `no_draft_far_cap`) — the fix routes zero-with-buildings
   through the EXISTING `existing_building_area_unusable` reason with the basis traceable in
   inputs/assumptions, so `packages/**` stays untouched (forbidden path). Schema-prose framing
   is recorded as a candidate follow-up in path_notes, not silently included.
3. **numbldgs availability confirmed.** The PLUTO connector types `numbldgs` (pluto_soda.py
   ~:170, consumed at ~:784 for the numfloors rule) — the profile carries the fact family the
   fix needs; the producer locates the exact fact path.
4. **Scope disjoint under D-046.** Scenario-layer files only; zero overlap with the concurrent
   M4-T021 loop packet (connectors) or any other open task. Concurrency 2 ≤ 3.
5. **Directive binding verified.** `evaluate_task_refs(M5-T027)` → ok, applicable == cited ==
   the six IDs; digests resynced (D-059 2d46f9d5→9bceb56c, D-046 40e99052→5b0706d4) with
   audit_log entries in this same seam commit (c14).
6. **No placeholder seeding needed.** Six of seven allowed files already exist and are tracked;
   the producer report is the only new file.
7. **Scenarios executable and fail-closed-shaped.** S1 is a red-on-old row reproducing the
   reviewer's exact case; S2 splits established vacancy from unknown; S5 pins schema
   byte-compatibility (contracts-typegen/schema-bundle CI jobs).

## Verdict

**PASS** — contract ready for claim and producer dispatch.
