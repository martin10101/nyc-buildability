# G0 Readiness Record — M0-T017 (control-plane S7 live-ledger coupling defect fix)

- **Gate:** G0 definition-of-ready (administrative; recorded by the orchestrator)
- **Recorded:** 2026-07-17
- **Task:** M0-T017, defect_fix, producer backend-engineer, reviewer code-reviewer (G3/G4)

## Defect evidence

CI `control-plane` job failure on PR #20/#21 merge-preview runs (job 87990690868): `test_s7_backward_compatibility` line ~808 `assert backlog, "expected at least one backlog task in the ledger copy"` — the assertion couples the suite to mutable live-ledger composition. Claiming M2-T002 + M1-T009 (dispatch PR #19) legitimately emptied the backlog; the suite then fails repo-wide. Passing runs on the same PRs' branch-HEAD builds (pre-claim ledger) confirm the coupling. Not a product regression; the enforcement code is correct.

## Readiness checklist

- **Objective unambiguous:** make S7 independent of live task statuses (synthesize the exemplar it needs inside the temp ledger copy when absent, or restructure); suite must pass with any backlog composition including empty. No enforcement-behavior change.
- **Dependencies:** none. MASKING NOTE: this packet itself re-adds a backlog task, which hides the symptom on future runs — the fix must be verified against a simulated empty-backlog copy, not just the live ledger.
- **File scope exclusive:** `tools/test_project_control.py` (+ docstring-level touch of `tools/project_control.py` only if needed), own producer report. No other task currently owns tools/ (M0-T016 accepted).
- **Acceptance scenarios:** S1 suite passes with the real ledger AS-IS; S2 suite passes with a temp copy whose backlog is emptied (the regression case); S3 no enforcement-behavior change (all 10 groups green); S4 CI control-plane job green on the task PR.
- **Credentials:** none. Gates G0/G2/G3/G4 assigned; reviewer code-reviewer.
- **Execution/disk:** worktree `.claude/worktrees/M0-T017`; pure-stdlib local test runs permitted; KB-scale.
- **Cleanup:** task branch → PR → merge; worktree removed via deletion-approval flow.

Result: PASS — ready to claim and dispatch.
