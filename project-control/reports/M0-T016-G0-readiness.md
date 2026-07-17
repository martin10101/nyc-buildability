# G0 Readiness Record — M0-T016 (Project-control hardening follow-up)

- **Gate:** G0 definition-of-ready (administrative; recorded by the orchestrator)
- **Recorded:** 2026-07-17
- **Task:** M0-T016, implementation, producer backend-engineer, reviewers code-reviewer (G3) + security-reviewer (G5→recorded as required-gate set G0/G2/G3/G4 per packet; see note)

## Note on required gates

The packet's `required_gates` are `["G0","G2","G3","G4"]` with `reviewer_agents` `["code-reviewer","security-reviewer"]`. The security-reviewer participates in the G3/G4 independent review of CLI-authority hardening (this task changes reviewer-roster and gate-enum enforcement — control-plane integrity, not app security surface). No G5 is listed as required; the security-reviewer's read-only review is captured within the assigned gates. Gate assignment is unchanged from the packet.

## Readiness checklist

- **Objective unambiguous:** YES — three owner-scoped hardening items closing M0-T014 defects: (1) reject the reserved `orchestrator` identity in `reviewer_agents` at new-task authoring AND in the independent-gate branch of `gate()` (D1); (2) validate `--gates` values against the canonical G0–G7 enum with a bounded error (D2); (3) document + enforce that a blocked task with empty/invalid reviewer rosters (M0-T007/T008) cannot leave blocked until rosters are amended — WITHOUT changing those tasks' status now (OBS-3).
- **Dependencies:** none formally; builds on M0-T014 (ACCEPTED, hardened CLI at main). No mocked dependencies.
- **File scope exclusive:** `tools/project_control.py`, `tools/test_project_control.py`, own producer report. Verified NON-overlapping with the only other in-flight task M2-T003 (scope `services/api/**` + `packages/contracts/**`). No shared files with any active writer.
- **Inputs/outputs defined:** packet `project-control/tasks/M0-T016.json`. Inputs: M0-T014 G5 defects D1/D2 (verbatim), G3 OBS-3, CLI+tests as merged. Outputs: the three enforcement changes with bounded errors, negative tests per rejection, green existing suite, producer report.
- **Acceptance scenarios:** S1–S4 (orchestrator-in-roster rejected at author + gate; `--gates` enum rejection; blocked-roster precondition with M0-T007/T008 untouched in the live ledger; full suite + CI control-plane job green, no retro-rejection of stored history).
- **Source documentation available:** M0-T014 reports in-repo; the CLI enforcement model documented in its `--help` and module docstring. No external credentials.
- **Credentials:** none required. No blocker needed.
- **Gates assigned:** G0, G2 (producer self-check), G3 + G4 (code-reviewer + security-reviewer independent).
- **Execution location and disk:** producer edits `tools/*.py` in the isolated worktree `.claude/worktrees/M0-T016` (source-only, small). The control-plane test suite is pure-Python stdlib (no heavy deps) and runs both locally and in the CI `control-plane` job. No datasets, no DB, no build toolchain.
- **Low-storage budget:** respected — two Python files + tests, KB-scale. Owner PC well within budget.
- **Cleanup/cloud routing:** committed to GitHub via task branch → PR; worktree removed after merge. No local-only artifacts.
- **CRITICAL constraint verified:** the packet's `forbidden_paths` protect the live ledger, especially `M0-T007.json`/`M0-T008.json` status — the task adds enforcement + tests only and must not transition those tasks. Validation applies on write only; stored history is never retro-rejected (hardened-CLI invariant).

Result: PASS — ready to claim and dispatch. May run in parallel with M2-T003 (disjoint scope, separate producer instance, off the product critical path).
