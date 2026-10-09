# Wave 19 (2026-10-09; written 10:47 UTC) - concurrency record: M5-T146 (the document) and M5-T147 (the screen), the wiring of the first building option

Written by the orchestrator before any builder of these tasks is started (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** D-090 row R773 (long tasks are cut into parts built side by side) and the owner's recorded limits (at most three builders and four reviewers at once; never the same file; heavy runs and merges one at a time).

**Two tasks, one branch, one reviewed head, one pull request.** The regenerated results document changes what the website's tests read, so a head with only one of the two tasks would be red in CI.

**Order and who builds what (each builder in its own worktree, each from the integrated head named in its brief, each making ONE commit):**

1. ALONE: part A of M5-T146, the results contract (a rules-engineer agent): `packages/contracts/schemas/v1/results.schema.json`, `packages/contracts/generated/results.ts`, new fixtures under `packages/contracts/fixtures/valid/results` and `fixtures/invalid/results`.
2. SIDE BY SIDE, three builders, after part A is integrated: part B of M5-T146, the server (a rules-engineer agent): the engine files under `services/api/app/scenario/three_answers/` and its tests under `services/api/tests/scenario/three_answers`; part D1 of M5-T146, the register checker's split and the two guards (a rules-engineer agent): `services/api/app/rules/review_register/` code and `services/api/tests/rules/test_zoning_rule_review_register_calculations.py`; part C of M5-T147, the website (a frontend-engineer agent): files under `apps/web/` only. No path is shared.
3. ALONE, after part B: part D2 of M5-T146 (the register's source data and rendered pages) and part E of M5-T146 (the committed results document, its snapshots, the journey test and the read-route test, regenerated once) by ONE builder, one after the other.
4. ALONE, last: the website's content tests of M5-T147 against the regenerated document (the same frontend builder, resumed).

**One at a time, by the orchestrator:** every cherry-pick, the focused checks on each integrated head, the one push of the head under review, any merge. No full suite runs on the build machine: that is CI's. The website's checks run on this Linux build machine, never on the owner's computer.

**Recorded afterwards** in the review records: each builder's run time and whether a part had to wait.
