# Wave 4 (2026-10-07) - concurrency record for two pieces built at the same time

Written by the orchestrator before any builder of the wave is started, as the orchestration policy requires (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** Owner messages 107 and 108 of 2026-10-07 (D-090 source-052, rows R494 to R497): several independent parts at once, about five helpers, never on the same file. Bounds as recorded: at most five helpers at once, at most three building and at most four reviewing; heavy test runs one at a time; merges one at a time, in order; nothing built on unmerged work.

**One branch.** Both tasks ride on one branch, `task/wave4-result-ways-readings-p4` (worktree `/root/project/w-wave4`), from the integration head `65338f6d` (the merge of wave 3). The integration branch's own run on that head was read as complete and successful before the branch was made. The orchestrator alone runs the ledger, git and the registry there. Each builder works in a worktree of its own and makes one commit, which the orchestrator cherry-picks.

**Order.** Merged so far of the work order: steps R0, P1 and P2; the lot-reach measurements; contract 1.3.0. The rest of Part 0 is the engine work, cut by the orchestrator into pieces built one after the other so that each can be reviewed well: (A) decide how each result appears, in new files that nothing calls (this wave: M5-T129); (B1) carry the facts to the engine without changing any output; (B2) emit contract 1.3.0, with the validators' checks of row DB-171, the regenerated saved results and drawings and the review-register entries; then the website's display, built against real documents. This wave also holds the independent reading of the text wave 3 captured (M4-T032).

## The pieces

| | M5-T129 | M4-T032 |
|---|---|---|
| What | Decide how each result appears (settled, conditional, withheld): a pure decision module; computes no zoning number; nothing calls it | The independent reading of the law text captured by M4-T031, written into the R6B reference cases |
| Depends on | M5-T127 and M5-T128: accepted and merged | M4-T030 and M4-T031: accepted and merged |
| Depends on the other piece of this wave | no | no |
| Builder | `scenario-optimization-engineer` | `rules-engineer`, started with two independent readings already in hand (two reader agents of different types, working outside the repository and without the web from a sealed folder made from the merged head) |
| Files it may write | `services/api/app/scenario/three_answers/result_ways.py`, `result_way_inputs.py` (new); `services/api/tests/scenario/three_answers/test_result_ways.py`, `test_result_ways_*.py` (new); its report | `docs/reference-cases/R6B/**`; `services/api/tests/rules/reference_cases/**`; its report |
| Files it only reads | the work order; the contract schema; `services/api/app/spatial/lot_reach.py`; the existing engine modules; the REACH rows of the corner-reach reference case through the loader | the captures; the two readings |
| Forbidden | every existing file under `services/api/app/**`; `packages/**`; `apps/**`; `docs/**`; every other test | `services/api/app/**`; every capture; register; plans; the measurement-basis record |
| Gates | G0, G2, G3, G4 | G0, G2, G3, G4 |
| Reviewers | `data-contract-verifier` (G3) and `qa-engineer` (G4): ADR-006 Tier B, "Scenario calculation: data-contract + QA" | `code-reviewer` (G3 and G4) |
| Rule check | 10 rows | 5 rows |

## Files shared between pieces

- **Written by more than one piece: none.** The two sets of allowed paths do not overlap.
- **Read by one piece while the other writes nearby (the point learned in waves 2 and 3):** M4-T032 writes the reference cases and may mark older rows as superseded; a test that reads a superseded row through the loader fails. M5-T129's tests therefore read ONLY the reach rows of `cases/corner-reach.json` (which M4-T032 is told not to change or supersede) and take every other expected outcome from the sentences of the work order, quoted beside the test. M5-T129's module holds no table of what the overlay reading supports: the caller states it. So neither piece can break the other. **Watch at integration:** after both commits are on the branch the orchestrator runs both pieces' tests and M5-T127's lot-reach test, and confirms that the reach rows are unchanged.
- **Written by the orchestrator only:** `project-control/**` and `docs/DISCOVERY_BACKLOG.md`.
- **Shared test surface:** the full `services/api` suite covers both. It is run once, by the orchestrator alone, on the branch after both commits are integrated. Before any push that touches a contract schema the repository's contract validator is run (not expected in this wave: no schema changes).

## Limits kept

- Helpers at the same time: at most five; at most three building; at most four reviewing. Planned peak: two builders, then three reviewers as the builders finish.
- Producer and reviewer are different agents for every piece; no reader of M4-T032 is its builder or its reviewer.
- Every review names the exact head it reviewed. A commit to a piece's files after its review voids that review. A failed review is recorded as failed, in the task's progress log and in its review record, and the piece goes back to its builder.
- One pull request for the wave, merged by the fail-closed step on a fully green run.

## Stop conditions

- A builder's commit touches a file outside its own allowed paths: that commit is not integrated; the piece goes back to its builder.
- M5-T129 cannot be built without editing an existing file: the builder stops and reports.
- The work order's words and the orchestrator's stated readings do not decide a combination: the module withholds it and the builder lists it; nobody guesses.
- A piece fails its review and cannot be corrected quickly: it is taken off the branch before the wave's freeze so that it does not hold the other.
- The two readings of M4-T032 differ on a point: the row stays "not known" with both readings named; the builder does not decide.
- Any Tier D matter (a secret, a payment, production): stop and tell the owner.

## Merge order

The wave merges as one pull request after both tasks are accepted. If one piece is taken out, the other merges first. The clean-up of the temporary security exception (task M0-T183, not before 2026-10-07 14:09 UTC) is on a branch of its own after this wave is merged, because it runs ledger commands and one ledger-touching branch is open at a time; if this wave is still open at that time the orchestrator decides then, and records the decision.
