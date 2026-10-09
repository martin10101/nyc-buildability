# Wave 13 (2026-10-08) - concurrency record: one piece (the website results panel), no parallel builder

Written by the orchestrator before the builder of the wave is started, as the orchestration policy requires (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** Owner rows D-090-R292 (step 4: connect one option to the screen) and D-090-R582 (the results display is connected after the piece that emits the results document). Bounds as recorded (rows R494 to R497): at most five helpers at once, at most three building and at most four reviewing; heavy test runs one at a time; merges one at a time; nothing built on unmerged work.

**One piece.** M5-T140: the results panel on the website, behind its own switch that is off by default. It asks the server route for one lot's results when the user presses a button and shows each result as settled, conditional or withheld. It stands on four merged server pieces (M5-T136, M5-T137, M5-T138, M5-T139). It changes no server file and turns no production switch on.

**One branch.** `task/wave13-results-panel` (worktree `/root/project/w-wave13`), from the integration head `6d024fc8` (the merge of wave 12). The orchestrator alone runs the ledger, git and the registry there. The builder works in a worktree of its own and makes commits the orchestrator integrates by cherry-pick.

## The piece

- **Builder:** `frontend-engineer`, one, in an isolated worktree.
- **Files it may write:** the 26 literal paths of the packet (13 new files, 12 existing ones, its report), all under `apps/web` except the report.
- **Files it only reads:** everything under `services/api` and `packages`; the cards' status strip and scope summary; the other pages of the website.
- **Gates:** G0, G2, G3, G4. **Reviewers:** `data-contract-verifier` (G3), `qa-engineer` (G4), a walkthrough of the running screen by a `human-journey-reviewer`, then the rule check by a `directive-compliance-verifier` (17 rows).

## Beside it

- Nothing is built beside it. No other branch touches the ledger.

## Limits kept

- Helpers at the same time: at most five; at most three building; at most four reviewing. Planned: one builder; three reviewers when it has finished (two reviews and the walkthrough), each in a review copy of its own.
- Producer and reviewer are different agents. Every review names the exact head it reviewed; a commit to the piece's files after its review voids that review unless the same reviewer confirms the change.
- Heavy test runs one at a time, by the orchestrator at the final candidate: the website's lint, typecheck, unit tests, build and browser tests, then the full api suite (the browser harness file is imported by api tests).
- One pull request for the wave, merged by the fail-closed step on a fully green run.

## Stop conditions

- A file outside the allowed paths must change (a consumer of the dashboard's tool set, of the reader or of the cards): the builder stops and reports.
- A server file, a schema, a fixture under `packages`, a dependency file or a production setting seems needed: the builder stops and reports.
- A ruling of the packet cannot be built as written: the builder stops and reports; it does not choose differently.
