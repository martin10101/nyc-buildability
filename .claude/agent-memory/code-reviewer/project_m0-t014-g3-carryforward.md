---
name: m0-t014-g3-carryforward
description: M0-T014 CLI hardening G3+G4 PASS @3e5e6e5; carry-forwards - M0-T007/T008 empty rosters need packet amendment before their independent gates; terminal tasks now immutable (post-accept re-checks need new task ids); forged role:independent_review gate files bypass accept-time roster check (write-time only, disclosed)
metadata:
  type: project
---

M0-T014 (project-control CLI hardening) G3 PASS and G4 PASS at commit 3e5e6e5 (2026-07-17), worktree `.claude/worktrees/M0-T014`, full suite exit 0 locally (9 groups, 115 real ledger files parse) and PR #4 CI fully green (runs 29595273085 / 29595249937 + secret-scan).

**Why:** owner code-audit P0; gate classes (G2=self_check by orchestrator, G0/G7=administrative, G1/G3/G4/G5/G6=independent w/ rostered reviewer != producer), progress transition enum, four accept preconditions, path containment, atomic writes all verified adversarially with no bypass path found.

**How to apply — carry-forwards for future reviews:**
- OBS-3 (medium, operational): ledger tasks M0-T007/M0-T008 are blocked with `reviewer_agents: []` and required G3/G4/G5. After merge, their independent gates CANNOT be recorded until the orchestrator hand-amends the packet rosters (no CLI edits reviewer_agents on an existing task). Recheck when those tasks resume.
- Terminal immutability: gate records can no longer be added to accepted tasks — post-acceptance re-checks (e.g., the B-007-closure G5 re-check pattern, [[m0-t013-g3-carryforward]]) must use a new task id or checkpoint.
- Accept-time independence checks role+reviewer only; roster membership is write-time only (backcompat). A hand-forged gate file with `role: independent_review` + unrostered reviewer would satisfy accept. Disclosed by producer (assumptions #2); consistent with the procedural threat model. Flag if anyone proposes relying on accept-time validation as a forgery defense.
- Low observations: submit allowed from `claimed` (skips self_check state; G2 gate still enforced); `new-task --gates` accepts arbitrary strings (fail-closed — unrecordable gates make the task unacceptable); blocker status only `open`/missing blocks — a "reopened" status would NOT block; corrupted task JSON / NUL args exit nonzero via raw traceback (rejection, but ugly).
- Live-ledger sweep at review time: no open blocker (B-001/B-004/B-006/B-008) word-matches any pending task id; all 30 task ids match the new regex; pending deps chain (M1-T009/M2-T002 -> M2-T003 -> M2-T004) is CLI-acceptable in order.
