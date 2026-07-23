# M4-T005 — G0 Definition-of-Ready

**Task:** Rules-evaluation ↔ property-analysis endpoint + property-screen draft-result surface (new v1 `rule_evaluation` contract; FH-4)
**Recorded by:** orchestrator (administrative gate)
**Branch/worktree:** `task/M4-T005-rule-eval` / `.claude/worktrees/M4-T005-rule-eval` (from clean main `9e8c22c`)

## Readiness checklist (docs/GATES_AND_CHECKPOINTS.md §G0)

| Criterion | Status |
|---|---|
| Objective unambiguous | ✅ Full objective + owner refinements captured in packet |
| Dependencies accepted or mocked behind contracts | ✅ M2-T013 **accepted**; M4-T004 rules engine **merged & code-available on main** (`9e8c22c`). Formal acceptance of M4-T004 is G6-held, but owner directive 2026-07-21/22 authorizes continued engineering on `needs_review` rules — the code dependency (evaluator/integration/registry) is physically present and consumed read-only |
| File scope exclusive | ✅ 29 allowed / 29 forbidden non-overlapping paths; **no concurrent task** (M4-T004 merged) |
| Inputs and outputs defined | ✅ 18 inputs / 11 outputs enumerated with paths |
| Acceptance scenarios exist | ✅ 14 scenarios (contract, API, security prod-disable, does-not-apply, missing-evidence, conflict, spatial-uncertainty, FH-4, error-handling, UI failure/recovery, a11y, honesty, regression) |
| Required source documentation available | ✅ product-flow, acceptance-standard, FH report, contracts README all present |
| Credentials available or blocker recorded | ✅ None required — endpoint is internal/flag-gated and tests run on recorded-official fixtures; no Supabase/Render/Geoclient secret needed for this slice (no auth added) |
| Required gates assigned | ✅ G0, G1 (data-contract), G3 (code), G4 (integration/UI + a11y), G5 (security) with distinct reviewers ≠ producers |
| Execution location + disk documented | ✅ Worktree + CI authority for web; thin-client, text-only, python-stdlib typegen + pytest locally; **no local npm** |
| Low-storage PC within budget | ✅ Negligible disk (source + JSON fixtures); no datasets/caches/node_modules added locally |
| Temp-file cleanup + durable routing defined | ✅ Scratchpad-only temp; no large/persistent artifacts on owner PC |

## Holds honored
Nothing Published/Verified; no rule accepted; no G6 manufactured; M4-T001 stays unaccepted; endpoint **disabled by default in production** (not anonymously exposed); PR #64, CP-0032, expansion/GDS holds untouched; `property_profile` 1.4.0 and existing `/properties/{bbl}` contract unchanged.

**Verdict: PASS** — task is ready to claim.
