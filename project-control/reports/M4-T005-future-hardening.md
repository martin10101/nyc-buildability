# M4-T005 — future-hardening notes (non-blocking)

Raised by the G4 human-journey reviewer at frozen `84b50a7`. **Neither blocks acceptance** — both are marked LOW / theoretical and are recorded here for a future task, not as required corrections. All required gates (G0/G1/G3/G4/G5) passed.

- **FH-M4T005-1 (clarity, LOW):** In the spatial-uncertainty UI state, `CandidateShare` renders the point estimate alongside the range (`min–max (point estimate X)`). This is honest and the range is never collapsed, but a reader skimming could anchor on the point value. Consider de-emphasizing the point estimate relative to the range in a future UI-polish pass.
- **FH-M4T005-2 (robustness, LOW):** `classifyRuleEvaluation` (apps/web/src/lib/rule-evaluation.ts) has no explicit branch for a document whose top-level `coverage_status === "data_conflict"` unless `fail_safe`/`fail_safe_reason` is also set — it would fall through to `applicable_draft`. In practice the backend always pairs `data_conflict` with a fail-safe reason (CI-green fixtures confirm real payloads route correctly), so this is theoretical. Consider an explicit `data_conflict` classifier branch as belt-and-suspenders in a future task.

These join the existing M4 future-hardening backlog; they are not required for M4-T005 acceptance.
