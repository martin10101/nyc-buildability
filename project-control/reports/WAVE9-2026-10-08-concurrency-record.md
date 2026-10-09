# Wave 9 (2026-10-08) - concurrency record: one piece, no parallel builder

Written by the orchestrator before the builder of the wave is started, as the orchestration policy requires (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** Owner message 119 of 2026-10-08 (D-090 source-060, rows R582 and R583): after wave 8, the piece that emits the results document, then the results display. Bounds as recorded (rows R494 to R497): at most five helpers at once, at most three building and at most four reviewing; heavy test runs one at a time; merges one at a time; nothing built on unmerged work.

**One piece.** M5-T136: the piece that first emits the results document in its three-way form (contract 1.3.0). It is NOT split and nothing is built beside it: it regenerates the committed journey fixture, which the server tests, the saved drawings and the website tests all read, so any other piece touching the results document or its readers would share files with it. The results display is built only after this piece has merged.

**One branch.** `task/wave9-emit-three-way-document` (worktree `/root/project/w-wave9`), from the integration head `1adaf7f4`. The integration branch's own run on that commit was read as complete and successful before the contract seam. The orchestrator alone runs the ledger, git and the registry there. The builder works in a worktree of its own and makes commits the orchestrator integrates by cherry-pick.

## The piece

- **Builder:** `scenario-optimization-engineer`, one, in an isolated worktree.
- **Files it may write:** the 28 literal paths of the packet (one new module, the adapter, five server test files, the journey fixture and its three saved drawings, the website reader, the answer card and six website tests, the review register's source and its rendered files for three rules, its report).
- **Files it only reads:** the engine (`engine.py`, `dwelling_units.py`, `geometry.py`, `answers.py`, `building_option.py`), the decision modules except the adapter, the results schema, its copies and the generated type, every other fixture and snapshot.
- **Gates:** G0, G2, G3, G4. **Reviewers:** `data-contract-verifier` (G3), `qa-engineer` (G4), then the rule check by a `directive-compliance-verifier` (18 rows).

## Beside it, read-only only

- One read-only helper may prepare the exact fewer-checks proposal the owner asked for (rows R580 and R581): research, no file of the repository written. It shares nothing with the builder.

## Limits kept

- Helpers at the same time: at most five; at most three building; at most four reviewing. Planned: one builder; two reviewers when it has finished; one research helper beside.
- Producer and reviewer are different agents. Every review names the exact head it reviewed; a commit to the piece's files after its review voids that review; a failed review is recorded as failed, in the task's progress log and in its review record, before any rework.
- Heavy test runs one at a time: the full api suite and the website checks are run by the orchestrator at the final candidate, one after the other.
- One pull request for the wave, merged by the fail-closed step on a fully green run. If a dependency check turns red for a reason outside the wave, nothing merges on a run that predates it.

## Stop conditions

- The builder finds that the emitted document cannot be expressed in the 1.3.0 schema as it stands: it stops and reports the exact point; no schema is changed in this wave.
- A snapshot suite changes a saved file that the packet does not name: the builder stops and reports it; the orchestrator adds that one literal path.
- A question of law appears that the reference cases do not answer: it is named, the result stays withheld or conditional, and nobody decides it by preference.
