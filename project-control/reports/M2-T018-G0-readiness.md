# M2-T018 — G0 administrative readiness (D-004 Step 4 pilot, lane 2)

- Recorded by: orchestrator (administrative gate). Frozen base: `84c1bf29243bb862d344c909099c9bd9a3f6a766` (post PR #125, which merged the corrected packet + D-004 amendment 7).
- Packet: merged at the frozen base; in-regime (`directive_refs` D-004:ALL); resolver derives the Step-4 conduct rows (D-004-R298, R301, R302, R303, R306) for this task; validator `--check` clean.
- Authorization: owner GO for D-004 Step 4 (source-008, 2026-07-30); pilot-task selection lanes 2+3 (D-004-R300); producer model Opus 5 ceiling (D-004-R298).
- Scope: allowed/forbidden paths recorded in the packet; disjointness against M4-T008 verified by import graph and existing ledger fences (M2-T017 forbids rules/**; M4-T007 forbids profile/api/contracts) — no shared file; scout evidence in the Step-4 evidence report lane.
- Inputs exist at the frozen base: frozen M2-T017 serializer + report; profile builder modules; connector lineage-key evidence; both source_fact schema copies; generated TS.
- Producer: backend-engineer (existing roster producer; distinct from reviewers code-reviewer + security-reviewer). Worktree/branch pre-created by the orchestrator from the frozen base: `.claude/worktrees/M2-T018-serializer-wiring` on `task/M2-T018-serializer-wiring`.
- Blockers: none referencing M2-T018. Acceptance scenarios AS-1..AS-6 recorded in the packet.

G0 result: PASS (administrative readiness).
