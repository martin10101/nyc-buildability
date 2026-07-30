# M0-T028 — G0 definition-of-ready (administrative)

**Task:** M0-T028 — B-015: teammate read-only confinement — diagnose, fix, and regression-test the
PreToolUse guard (D-004 Step 3).
**Reviewer:** orchestrator (administrative G0). **Result:** PASS (ready to claim).
**Run against the CORRECTED packet** (post PR #120, D-004 amendment 5/source-006) at frozen main
`4a4bf2d572edce963a355d9d997a2e05833c1dbf` — a FRESH G0 per source-006 Phase 3 item 1; no earlier
readiness assessment is reused.

## Readiness checklist (per `/start-controlled-task` and docs/GATES_AND_CHECKPOINTS.md G0)

- **Objective unambiguous:** diagnose B-015 with primary evidence (H1: PreToolUse never fires for
  Agent Teams teammates vs H2: it fires without a recognized `agent_type`/`agentType` identity),
  fix prevention ONLY if H2-repairable inside allowed paths (H1/detection-only = STOP for a new
  owner decision, D-004-R241/R243/R248), plus the R100 path-quoting and R101 gitignore ride-alongs
  and the R144 index correction (already handled at amendment capture — producer confirms, no
  re-edit needed). ✓
- **Requirement identifiers named:** D-004-R139..R145 (amendment-4 scope), R100/R101 (ride-alongs),
  R168..R286 (amendment-5 GO, staged phases, stop conditions); binding via `directive_refs`
  D-004:ALL (regime 1.0); the resolver derives 177 applicable rows, recorded pending in
  verification.json. ✓
- **Dependencies accepted or explicitly handled:** `dependencies: []` after the owner-mandated
  deadlock correction (source-006 Phase 1; PR #120). M0-T027 is preserved as causal predecessor via
  inputs (pilot reports) and requirement references — NOT an acceptance prerequisite; no replacement
  dependency (none genuinely required by the control model or primary evidence). ✓
- **Exclusive file scope:** allowed_paths = the guard hook, `.claude/settings.json`, `.gitignore`,
  `tools/test_readonly_agent_guard.py`, `project-control/directives/index.json`, the two M0-T028
  report files, own packet (CLI lifecycle), and the B-015 blocker record (orchestrator resolution
  path). Overlap scan across every open/claimed/awaiting/blocked task packet: ZERO overlaps. The
  uncommitted local `.gitignore` security-hardening block in the primary checkout (owner-side
  security-audit tooling, 2026-07-27) is noted: implementation happens in a clean worktree from the
  frozen SHA, so it cannot contaminate the task diff. ✓
- **Inputs and outputs defined:** packet inputs 1–8 (blocker, both pilot reports, guard, settings,
  test suite, D-004 registry, rules); outputs = fixed guard, settings (only if diagnosis requires,
  incl. R100), .gitignore (R101), extended tests, index correction lane, producer report, payload
  evidence report. ✓
- **Acceptance scenarios exist:** AS-1..AS-10 in the packet (primary-evidence H1-vs-H2; Step-1
  tool-unavailability reconciliation; guard-denied sentinel with independent `test -e`; full
  regression suite incl. teammate payload shape + fail-closed; R100 space-safe proof; R101
  `git check-ignore -v` proof; R144; validator/tests/secret scan; containment; orchestrator-only
  B-015 closure). Sentinel clarification (source-006): Write/Edit tool-unavailability is reported
  honestly as tool-unavailability; the Bash redirection is the load-bearing PreToolUse test and must
  be denied by `readonly_agent_guard.py` itself; AS-3's final proof runs ONLY in the mandatory fresh
  session (Phases 7–8). ✓
- **Required source documentation available:** AGENT-TEAMS-PILOT-1.md, AGENT-TEAMS-PILOT-2-PROBE.md
  (byte-preserved, read-only inputs), D-004 sources 001–006, B-015 record, hook docstring. ✓
- **Credentials:** none required (local hooks/tests only; no cloud resources). ✓
- **Gates + independent reviewers assigned:** G0 (this record), G2 (producer self-check through the
  orchestrator-controlled route), G3 code-reviewer, G5 security-reviewer, plus control-plane-verifier
  and directive-compliance-verifier — all four reviewers distinct from producer backend-engineer. ✓
- **Producer assignment (source-006 Phase 1 items 6–7):** backend-engineer — existing role, qualified
  (accepted M0-T030/M0-T031 deterministic Python tooling lane), distinct from every reviewer;
  single-writer; dispatched as a background subagent in an isolated worktree, NOT an Agent Teams
  teammate while B-015 is open (Phase 3 item 6). Diagnostic teammate probes, if needed, are
  no-Write/Edit, bounded, explicit-model spawns (Fable 5 for gate-class reviewer roles per
  D-004-R161; dirt sweep before/after each probe per R235-range rows). ✓
- **Execution location and disk:** fresh worktree `.claude/worktrees/M0-T028-readonly-guard`, branch
  `task/M0-T028-readonly-guard`, from frozen `4a4bf2d5`; text-only edits, negligible disk (thin-client
  policy respected; no datasets, no Docker, no local DB). ✓
- **Stop conditions loaded:** packet stop_conditions + source-006 STOP CONDITIONS list (14 items)
  bind the whole execution; two-session boundary — B-015 closure/acceptance FORBIDDEN this session;
  fresh-session sentinel rerun mandatory. ✓

Reviewed at main = `4a4bf2d572edce963a355d9d997a2e05833c1dbf` (post-PR #120: D-004 amendment 5 +
corrected M0-T028 packet). PR #120 checks: 28/28 pass; main push CI green (run confirmed before this
gate was recorded).
