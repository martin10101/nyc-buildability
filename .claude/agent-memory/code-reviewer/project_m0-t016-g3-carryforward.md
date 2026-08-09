---
name: m0-t016-g3-carryforward
description: M0-T016 project-control CLI hardening G3 PASS 2026-07-17; orchestrator-roster/gates-enum/blocked-roster enforcement facts for future control-plane reviews
metadata:
  type: project
---

M0-T016 (project-control CLI hardening follow-up) G3 PASS 2026-07-17 @ debe698, closes M0-T014 D1/D2/OBS-3. Scope = tools/project_control.py + tools/test_project_control.py + own report ONLY.

**Why:** owner directive 2026-07-17 post-M0-T014 acceptance; scoped hardening without delaying active gate cycle.

**How to apply (facts to reuse when reviewing project_control.py changes):**
- `RESERVED_ORCHESTRATOR = "orchestrator"` string-literal rail. Prohibited in `new_task --reviewers` and in the INDEPENDENT_GATES branch of `gate()` (G1/G3/G4/G5/G6). CRITICAL preserved-positive: `gate()` evaluates `SELF_CHECK_GATES` (G2) and `ADMINISTRATIVE_GATES` (G0/G7) branches FIRST and REQUIRE `reviewer == "orchestrator"` — those are untouched. Verified live: orchestrator G2→role self_check, G0/G7→role administrative still pass.
- `--gates` validated against `GATE_IDS = ("G0".."G7")` in `new_task` BEFORE file write; error names only offending entries + full enum. Catches lowercase g3, G8, G10, mixed valid+invalid. Rejected authoring creates no task file.
- Blocked-roster precondition (`invalid_unblock_roster()` called in `progress()`): leaving `blocked` for any active target EXCEPT `canceled` requires producer≠"" ≠orchestrator AND ≥1 reviewer that is non-empty, ≠orchestrator, ≠producer. `blocked->canceled` exempt; message-only progress (no `--status` / `--status`==current) never gated — `progress` skips the whole block when `target` falsy.
- `progress` is the SOLE exit from blocked (claim needs ready/rework; submit needs claimed/in_progress/self_check/rework; gate PASS acts on backlog/rework/awaiting_gate). So enforcing in `progress()` fully closes the unblock path.
- All validation WRITE-time only; S7 copies real ledger (134 files) and asserts legacy records (no role field, empty reviewer_agents, backslash report paths) still parse + accept(). No retro-rejection.
- Identity is procedural/string-equality, not cryptographic (unchanged); prohibition matches exact literal, not look-alikes (orchestrator-2). Consistent with existing model.
- M0-T007/T008 live status = `blocked`, byte-unchanged in this branch (outside allowed paths) — the new precondition will gate their future unblock until packets amended with valid producer+reviewer rosters. Related: [[m0-t011-g3-carryforward]] D5 hook-order work.
- Suite: `python tools/test_project_control.py` → 10 groups green (S8 = new). Ran clean in worktree.

**LOW residuals (non-blocking; recheck at next project_control.py touch):**
1. `--gates` split does not filter empty entries (`a.gates.split(",")`) while `--reviewers` does (`if x`): `--gates "G0,G3,"` rejected with awkward-but-bounded message naming an empty offender. Fail-closed; align splits in maintenance.
2. Unblock precondition demands a producer even for a never-claimed task blocked from `backlog`; unparking to backlog forces pre-assigning a producer claim() later overwrites. Matches packet wording; friction only.
3. Module docstring BACKWARD COMPATIBILITY still says "21 accepted tasks" (written at M0-T014; ledger 25+). Cosmetic staleness, outside this diff.
4. Diff-vs-main gotcha: main advanced past the branch point during review, making `git diff main --stat` show phantom ledger deletions — always diff against merge-base (7087ee1) when auditing scope.
