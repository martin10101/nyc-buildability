# Wave 17, second piece (2026-10-09; written 06:44 UTC) - concurrency record: M4-T038 (the review register's calculation entries and the six-step comparison), after the first piece's builder has finished

Written by the orchestrator before the builder of this piece is started (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F). It adds to `WAVE17-2026-10-09-concurrency-record.md`.

**Authority.** D-090 rows R685 to R709 (the owner's message of 2026-10-09 05:36 UTC) and R379.

**One more piece on the same branch** `task/wave17-hand-worked-option`: M4-T038. The first piece (M4-T037) is built and integrated; its builder has finished; its independent review reads a detached copy at the pushed head. The two pieces share no file: M4-T037 owns `docs/reference-cases/R6B` and `services/api/tests/rules/reference_cases`; M4-T038 owns the register's files under `services/api/app/rules/review_register`, `docs/zoning-rule-review` and one new test file in `services/api/tests/rules`.

- **Builder:** `rules-engineer`, one, in an isolated worktree reset to this piece's claim head; started only when the review of M4-T037 has returned.
- **Gates:** G0, G2, G3, G4. **Reviewers:** `data-contract-verifier` (G3), `qa-engineer` (G4), then the rule check.
- **Beside it:** no other builder. Reviewers of the first piece may still run; they are read-only.
- **Run as wave 17 is run:** focused checks on the build machine; every full suite and security check in CI on the pushed head, read before any gate, acceptance or merge; evidence written once.

## Stop conditions

- A file outside the allowed paths must change (the existing register test among them): the builder stops and reports.
- An expected answer would have to be taken from a program run, or a human verdict entered: the builder stops and reports.
- A rule, a calculation, a result or a fixture would have to change: the builder stops and reports.
