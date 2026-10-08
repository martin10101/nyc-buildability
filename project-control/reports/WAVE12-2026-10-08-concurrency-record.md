# Wave 12 (2026-10-08) - concurrency record: one small piece, no parallel builder

Written by the orchestrator before the builder of the wave is started, as the orchestration policy requires (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** Owner message 119 of 2026-10-08 (D-090 source-060, row R582): the results display is connected after the piece that emits the results document. Bounds as recorded (rows R494 to R497): at most five helpers at once, at most three building and at most four reviewing; heavy test runs one at a time; merges one at a time; nothing built on unmerged work.

**One piece.** M5-T139: in the results document the route returns, the two lines for the housing program and the floor-to-floor height say that the user chose them when the user did. It is the small server piece before the website panel: found by an independent review of the route (backlog row DB-204 a). The website panel is contracted after its draft has been read against the code; if it is contracted while this piece is still open it rides on a branch of its own after this one has merged, because both touch the ledger.

**One branch.** `task/wave12-user-choices-said-truly` (worktree `/root/project/w-wave12`), from the integration head `10607b0e` (the merge of wave 11). The orchestrator alone runs the ledger, git and the registry there. The builder works in a worktree of its own and makes commits the orchestrator integrates by cherry-pick.

## The piece

- **Builder:** `backend-engineer`, one, in an isolated worktree.
- **Files it may write:** the 7 literal paths of the packet (the entry, the transform, the route file, three test files, its report).
- **Files it only reads:** the engine and its disclosure builder, the decision modules, the body reader of the route, every schema, fixture and saved drawing, the whole website.
- **Gates:** G0, G2, G3, G4. **Reviewers:** `data-contract-verifier` (G3), `qa-engineer` (G4), then the rule check by a `directive-compliance-verifier` (4 rows).

## Beside it, read-only only

- One read-only helper is drafting the website panel's packet (it writes one file outside the repository). It shares nothing with the builder.

## Limits kept

- Helpers at the same time: at most five; at most three building; at most four reviewing. Planned: one builder; two reviewers when it has finished; one drafting helper beside.
- Producer and reviewer are different agents. Every review names the exact head it reviewed; a commit to the piece's files after its review voids that review unless the same reviewer confirms the change.
- Heavy test runs one at a time, by the orchestrator at the final candidate.
- One pull request for the wave, merged by the fail-closed step on a fully green run.

## Stop conditions

- A saved file (the journey result, a drawing) changes: the builder stops and reports.
- The transform's file would pass the size threshold: it stops and reports.
