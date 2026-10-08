# Wave 10 (2026-10-08) - concurrency record: one piece, no parallel builder

Written by the orchestrator before the builder of the wave is started, as the orchestration policy requires (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** Owner message 119 of 2026-10-08 (D-090 source-060, row R582): after the piece that emits the results document, the results display is connected. Bounds as recorded (rows R494 to R497): at most five helpers at once, at most three building and at most four reviewing; heavy test runs one at a time; merges one at a time; nothing built on unmerged work.

**Why this piece comes before the route.** The server route of the work order's Part A must give the older engine five facts of the lot. Today only tests supply them, typed in. A route may not type them in and may not take them from the user as facts. M5-T137 makes them come from the evidence the decision step already gathers. The route is contracted after this piece has merged.

**One piece.** M5-T137. Nothing is built beside it: it regenerates the committed journey result, which the server tests, the saved drawings and the website tests all read.

**One branch.** `task/wave10-conditions-from-evidence` (worktree `/root/project/w-wave10`), from the integration head `42d85651` (the merge of wave 9). The integration branch's own run on that commit was read as complete and successful before the contract seam. The orchestrator alone runs the ledger, git and the registry there. The builder works in a worktree of its own and makes commits the orchestrator integrates by cherry-pick.

## The piece

- **Builder:** `scenario-optimization-engineer`, one, in an isolated worktree.
- **Files it may write:** the 19 literal paths of the packet (one new module, the adapter, the transform, five server test files, the journey fixture and two saved drawings, three website test files, the review register's source and three rendered files, its report).
- **Files it only reads:** the engine, the decision modules except the adapter, the disclosure builder, the results schema and its copies, every rule file, every other fixture and saved drawing, the website's source.
- **Gates:** G0, G2, G3, G4. **Reviewers:** `data-contract-verifier` (G3), `qa-engineer` (G4), then the rule check by a `directive-compliance-verifier` (10 rows).

## Limits kept

- Helpers at the same time: at most five; at most three building; at most four reviewing. Planned: one builder; two reviewers when it has finished.
- Producer and reviewer are different agents. Every review names the exact head it reviewed; a commit to the piece's files after its review voids that review; a failed review is recorded as failed, in the task's progress log and in its review record, before any rework.
- Heavy test runs one at a time: the full api suite and the website checks are run by the orchestrator at the final candidate, one after the other.
- One pull request for the wave, merged by the fail-closed step on a fully green run. If a dependency check turns red for a reason outside the wave, nothing merges on a run that predates it.

## Stop conditions

- The builder finds a state in which the decision step shows a result while a condition that result reads is not known: it stops and reports the state; nothing is papered over.
- A stand-in cannot be proved to withhold from the rule file: it stops and reports.
- A website file other than the three named tests fails, or a saved file other than the three named changes: it stops and reports; the orchestrator adds a literal path or splits the work.
