# Wave 15 (2026-10-09; this record written 01:25 UTC) - concurrency record: one piece (the split of the emitter file and three test gaps), no parallel builder

Written by the orchestrator before the builder of the wave is started, as the orchestration policy requires (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** Backlog rows DB-205 point a and DB-199 points a to c; owner message 124 (D-090 source-063, row R627: continue the results screen). Bounds as recorded (rows R494 to R497).

**One piece.** M5-T143: the scope-line code of `services/api/app/scenario/three_answers/three_way_document.py` (599 lines) moves, character for character, to a new module behind the old import path; three tests the emitter lacked are added. No emitted or shown text changes; no fixture, schema, snapshot or website file; no switch.

**One branch.** `task/wave15-emitter-split` (worktree `/root/project/w-wave15`), from the integration head `702a294a`. The orchestrator alone runs the ledger, git and the registry there. The builder works in a worktree of its own and makes commits the orchestrator integrates by cherry-pick.

## The piece

- **Builder:** `backend-engineer`, one, in an isolated worktree.
- **Files it may write:** the 4 literal paths of the packet.
- **Gates:** G0, G2, G3, G4. **Reviewers:** `code-reviewer` (G3), `qa-engineer` (G4), then the rule check by a `directive-compliance-verifier` (2 rows).
- **Beside it:** no other builder. Nothing else of this session writes a server file.

## How this wave is run (the owner's simplification and the changed coding rules)

- On the build machine: ruff, the touched test folders and the size check. No server is started.
- **Every full suite and security check runs in CI on the pushed head, and that run is read on the exact head before any gate, acceptance or merge; a later code change needs it again.**
- Pushed: the head under review and the final head. The contract and claim seams are committed locally and ride with the first of those pushes.
- Evidence is written once: the reviewers' returns, kept unchanged, are the evidence of the reviews; the evidence map points to tests and to the review record's checks.
- Unchanged: producer and reviewer are different agents; the independent reviews, the rule check, the pre-merge check and the fail-closed merge.

## Stop conditions

- A file outside the allowed paths must change: the builder stops and reports.
- The emitted document differs for any input: the builder stops and reports.
