# M4-T008 — G0 administrative readiness (D-004 Step 4 pilot, lane 3)

- Recorded by: orchestrator (administrative gate). Frozen base: `84c1bf29243bb862d344c909099c9bd9a3f6a766` (post PR #125, which merged the corrected packet + D-004 amendment 7).
- Packet: merged at the frozen base; in-regime (`directive_refs` D-004:ALL); resolver derives the Step-4 conduct rows (D-004-R298, R301, R302, R303, R306) for this task; validator `--check` clean.
- Authorization: owner GO for D-004 Step 4 (source-008, 2026-07-30); pilot-task selection lanes 2+3 (D-004-R300); producer model Opus 5 ceiling (D-004-R298).
- Scope: allowed/forbidden paths recorded in the packet (rules/** + tests/rules/** only; contract schemas explicitly forbidden with a needs_split escape). Disjointness against M2-T018 verified — no shared file.
- Defect basis exists at the frozen base: DF-6 (WHOLE-SYSTEM-TRUST-REPLAN-2026-07-23 defect table); `_apply_exceptions` fail-open path, `_predicate_input_names` helper, and the existing three-valued required/applicability precedent all present in `services/api/app/rules/evaluator.py`.
- Producer: rules-engineer (existing roster producer; distinct from reviewers code-reviewer + security-reviewer). Worktree/branch pre-created by the orchestrator from the frozen base: `.claude/worktrees/M4-T008-df6-exceptions` on `task/M4-T008-df6-exceptions`.
- Note: M4 acceptance-chain G6 (qualified-human legal approval) blocks M4-T001..T006 acceptance, not this deterministic fail-closed hardening; DF-6 work was owner-directed via D-003-R023 and D-004-R300.
- Blockers: none referencing M4-T008. Acceptance scenarios AS-1..AS-6 recorded in the packet.

G0 result: PASS (administrative readiness).
