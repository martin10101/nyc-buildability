# Wave 14 (2026-10-09; this record written 2026-10-08 23:59 UTC) - concurrency record: one piece (the results screen's layout and announcements), no parallel builder

Written by the orchestrator before the builder of the wave is started, as the orchestration policy requires (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** Backlog row DB-206 points a and b; owner message 124 (D-090 source-063, row R627: continue the results screen). Bounds as recorded (rows R494 to R497).

**One piece.** M5-T142: on the results screen each condition of a figure becomes its own line under a visible word that marks the figure as conditional; a withheld result's reason and its kind of gap are set apart; a new result and each failure are announced to screen-reader users. No server file; no switch; the document's words are not retyped.

**One branch.** `task/wave14-results-layout` (worktree `/root/project/w-wave14`), from the integration head `1cd18f68`. The orchestrator alone runs the ledger, git and the registry there. The builder works in a worktree of its own and makes commits the orchestrator integrates by cherry-pick.

## The piece

- **Builder:** `frontend-engineer`, one, in an isolated worktree.
- **Files it may write:** the 8 literal paths of the packet (seven existing website files and its report).
- **Gates:** G0, G2, G3, G4. **Reviewers:** `code-reviewer` (G3), `qa-engineer` (G4), a walkthrough of the running screen by a `human-journey-reviewer`, then the rule check by a `directive-compliance-verifier` (6 rows).

## How this wave is run (the owner's simplification and the changed coding rules)

- On the build machine: lint, typecheck and the touched tests only. The builder starts no server and runs no browser test (the owner's test preview holds the ports).
- **Every full suite and security check runs in CI on the pushed head, and that run is read on the exact head before any gate, acceptance or merge; a later code change needs it again.**
- Pushed: the head under review and the final head. The contract and claim seams are committed locally and ride with the first of those pushes.
- Evidence is written once: the reviewers' returns, kept unchanged, are the evidence of the reviews; the evidence map points to tests and to the review record's checks.
- Unchanged: producer and reviewer are different agents; the independent reviews, the walkthrough, the rule check, the pre-merge check and the fail-closed merge.

## Stop conditions

- A file outside the allowed paths must change: the builder stops and reports.
- A browser spec's assertion would break: the builder stops and reports.
