# Wave 17 (2026-10-09; this record written 05:41 UTC) - concurrency record: one piece (step P6, the independent hand-worked example of a first building option), no parallel builder

Written by the orchestrator before the builder of the wave is started, as the orchestration policy requires (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** D-090 rows R663 and R664 (the first building shape, the floor schedule and the apartment estimate, by the smallest remaining work), R651 (which readings are necessary, before they are commissioned), R645 and R680 (completed research is reused), R679 (the handoff's remaining-work order). Bounds as recorded (rows R494 to R497).

**One piece.** M4-T037: two independent readings (made by two read-only helpers from a sealed folder) are written into the R6B reference cases as a new step-P6 case. Reference rows, pages and test support only.

**One branch.** `task/wave17-hand-worked-option` (worktree `/root/project/w-wave17`), from the integration head `65c60679`. The orchestrator alone runs the ledger, git and the registry there. The builder works in a worktree of its own and makes commits the orchestrator integrates by cherry-pick.

## The piece

- **Readers (not builders):** two, read-only, each alone, from a sealed folder outside the repository; started at 05:16 UTC on 2026-10-09 (the two dispatches, by the session transcript), while task M5-T144 was at its rule check, as preparation of the next piece that wave 16's record allowed. They write no repository file. Each reader's tool log is audited before its reading is used.
- **Builder:** `rules-engineer`, one, in an isolated worktree, started only when both readings are in hand (they are: received 05:29 and 05:30 UTC, saved unchanged, each tool log audited).
- **Files it may write:** the two folders and the report named in the packet.
- **Gates:** G0, G2, G3, G4. **Reviewers:** one fresh `data-contract-verifier` (G3 and G4; neither reader), then the rule check by a `directive-compliance-verifier` (13 rows).
- **Beside it:** no other builder. Read-only helpers may prepare the next piece (the register's pages for the calculations behind the first building option, with the comparison the owner asked for; then lot coverage by portion); they write no repository file.

## How this wave is run (the owner's simplification and the changed coding rules)

- On the build machine: ruff, the reference-case tests with the two tests of other tasks that read reference rows, the renderer's check, the size check and the path-coverage check.
- **Every full suite and security check runs in CI on the pushed head, and that run is read on the exact head before any gate, acceptance or merge; a later code change needs it again.**
- Pushed: each head under review and the final head. The contract and claim seams are committed locally and ride with the first of those pushes.
- Evidence is written once: the reviewers' returns, kept unchanged, are the evidence of the reviews; the evidence map points to tests and to the review record's checks.
- Unchanged: producer and reviewer are different agents; the independent review, the rule check, the pre-merge check and the fail-closed merge.

## Stop conditions

- A file outside the allowed paths must change: the builder stops and reports.
- A value would be recorded that only one reading gives, or a reading would be added by the builder: the builder stops and reports.
- A reader's tool log shows a path under the repository, a web page or the other reader's folder: that reading is not used and a fresh reader is started.
