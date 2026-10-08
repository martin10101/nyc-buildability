# Wave 13, repair task (2026-10-08) - concurrency record: one small piece, no parallel builder

Written by the orchestrator before the builder of the repair is started, as the orchestration policy requires (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Why there is a second task in this wave.** Task M5-T140 (the results panel) is accepted on this branch, and its pull request (476) cannot merge: the browser-test job fails in CI, because the browser-test harness that M5-T140 changed imports two helpers from the server's test tree, which CI does not have on its Python path. The orchestrator had not read the red CI runs on the reviewed heads before it recorded the gates and the acceptance. Nothing was merged. An accepted task is not changed afterwards; the repair is M5-T141.

**One piece.** M5-T141: the harness builds the same recorded inputs from the recorded files by path, with no import from the server's test tree; a guard test and an equality test in the server suite.

**One branch.** `task/wave13-results-panel` (worktree `/root/project/w-wave13`), on top of `02600b8f`. The orchestrator alone runs the ledger, git and the registry there. The builder works in a worktree of its own and makes commits the orchestrator integrates by cherry-pick.

## The piece

- **Builder:** `backend-engineer`, one, in an isolated worktree.
- **Files it may write:** the 3 literal paths of the packet (the harness file, one new server test file, its report).
- **Files it only reads:** everything else, the website's sources and browser specs included.
- **Gates:** G0, G2, G3, G4. **Reviewers:** `data-contract-verifier` (G3), `qa-engineer` (G4), then the rule check by a `directive-compliance-verifier` (2 rows).

## Beside it

- Nothing is built beside it. No other branch touches the ledger.

## Limits kept

- Helpers at the same time: at most five; at most three building; at most four reviewing. Planned: one builder; two reviewers when it has finished.
- Producer and reviewer are different agents. Every review names the exact head it reviewed.
- Heavy test runs one at a time, by the orchestrator at the frozen head: the whole browser suite started the way CI starts it (only the server's `app` package on the Python path), then the full api suite.
- **The orchestrator reads the CI runs on the pushed frozen head before it records any gate.**
- One pull request for the wave (476), merged by the fail-closed step on a fully green run.

## Stop conditions

- The repair needs a second harness module, a browser spec, a website source file or a server application file: the builder stops and reports.
- A recorded value would have to be retyped: the builder stops and reports.
