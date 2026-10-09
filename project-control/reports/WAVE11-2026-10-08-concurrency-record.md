# Wave 11 (2026-10-08) - concurrency record: one piece, no parallel builder

Written by the orchestrator before the builder of the wave is started, as the orchestration policy requires (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** Owner message 119 of 2026-10-08 (D-090 source-060, row R582): after the piece that emits the results document, the results display is connected; the work order's Part A (the server route) is its first half. Bounds as recorded (rows R494 to R497): at most five helpers at once, at most three building and at most four reviewing; heavy test runs one at a time; merges one at a time; nothing built on unmerged work.

**One piece.** M5-T138: one internal route, `POST /api/v1/properties/{bbl}/results`, behind a NEW switch that is off by default, that returns the emitted results document for one lot. It builds on tasks M5-T136 and M5-T137, both merged. The website (Part B) is NOT in this piece and starts only after it has merged.

**One branch.** `task/wave11-results-route` (worktree `/root/project/w-wave11`), from the integration head `08b17a74` (the merge of wave 10). The orchestrator alone runs the ledger, git and the registry there. The builder works in a worktree of its own and makes commits the orchestrator integrates by cherry-pick.

## The piece

- **Builder:** `backend-engineer`, one, in an isolated worktree.
- **Files it may write:** the 16 literal paths of the packet (three new route modules, the switch, the mount and the reported list, five test files, three documents with stale lines, its report).
- **Files it only reads:** the engine, the decision modules, the adapter and the derivation of M5-T137, the transform, every schema and fixture, the study-inputs provider and the live geometry module, the whole website.
- **Gates:** G0, G2, G3, G4, G5. **Reviewers:** `data-contract-verifier` (G3), `qa-engineer` (G4), `security-reviewer` (G5), then the rule check by a `directive-compliance-verifier` (18 rows).

## Limits kept

- Helpers at the same time: at most five; at most three building; at most four reviewing. Planned: one builder; three reviewers when it has finished.
- Producer and reviewer are different agents. Every review names the exact head it reviewed; a commit to the piece's files after its review voids that review; a failed review is recorded as failed before any rework.
- Heavy test runs one at a time, by the orchestrator at the final candidate.
- One pull request for the wave, merged by the fail-closed step on a fully green run. Nothing merges on a run that predates a security advisory.
- **No production switch is turned on.** The new switch defaults to off and `render.yaml` is not touched. Turning it on anywhere is the owner's decision and is not asked here.

## Stop conditions

- The route would have to supply a condition of the lot itself, or call the older entry with typed values: the builder stops and reports.
- The option document cannot be built from the body without a value that is a fact about the lot: it stops and reports.
- A file outside the allowed paths must change (a schema, a fixture, the provider, the entry): it stops and reports.
