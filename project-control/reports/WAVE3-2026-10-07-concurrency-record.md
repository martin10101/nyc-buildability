# Wave 3 (2026-10-07) - concurrency record for three pieces built at the same time

Written by the orchestrator before any builder of the wave is started, as the orchestration policy requires (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** Owner messages 107 and 108 of 2026-10-07 (D-090 source-052, rows R494 to R497): several independent parts at once, about five helpers, never on the same file. Bounds as recorded: at most five helpers at once, at most three building and at most four reviewing; heavy test runs one at a time; merges one at a time, in order; nothing built on unmerged work.

**One branch.** All three tasks ride on one branch, `task/wave3-results-contract-readings-further-captures` (worktree `/root/project/w-wave3`), from the integration head `5743630e` (the merge of wave 2). The integration branch's own run on that head was read before the branch was made. The orchestrator alone runs the ledger, git and the registry there. Each builder works in a worktree of its own and makes one commit, which the orchestrator cherry-picks.

**Order.** The work order's steps R0, P1 and P2 are merged, and so is the first new file of Part 0 (the lot-reach measurements). This wave holds: the first step of the rest of Part 0 (the contract that lets one value be settled, conditional or withheld, merged before any engine or screen uses it, so that the engine and the website can then be built side by side); the independent reading of the text wave 2 captured; and the capture of the text wave 2's readings and captures still name as missing. None is built on unmerged work. The engine and the website are NOT in this wave.

## The pieces

| | M5-T128 | M4-T030 | M4-T031 |
|---|---|---|---|
| What | The results contract can carry a value that is settled, conditional or withheld (version 1.3.0, strictly additive; nothing emits it) | The independent reading of the law text captured by M4-T029, written into the R6B reference cases | Further law-text captures |
| Depends on | nothing unmerged | M4-T028 and M4-T029: accepted and merged | M4-T029: accepted and merged |
| Depends on another piece of this wave | no | no | no |
| Builder | `backend-engineer` | `rules-engineer`, started only after two independent readings are in (two reader agents of different types, both working outside the repository from a sealed folder made from the merged head) | `legal-corpus-engineer` |
| Files it may write | `packages/contracts/schemas/v1/results.schema.json`; its runtime copy `services/api/app/_contract_schemas/v1/results.schema.json`; `packages/contracts/generated/results.ts`; one new test `services/api/tests/contracts/test_results_three_ways_slot.py`; its report | `docs/reference-cases/R6B/**`; `services/api/tests/rules/reference_cases/**`; its report | `docs/research/zr-snapshots/v1/**` (new files only); `services/api/app/_zr_snapshots/v1/**`; `services/api/tests/rules/test_zr_snapshot_bundle.py` only if it lists captures; its report |
| Files it only reads | the fixtures under `packages/contracts/fixtures/`; the earlier contract tests; the engine's validator | the captures; the two readings | the existing captures; the earlier producer reports |
| Forbidden | every fixture; every engine, route, drawing and website file; every other schema | `services/api/app/**`; every capture; register; plans; the measurement-basis record | every existing capture; rule files; register; reference cases; plans |
| Gates | G0, G2, G3, G4 | G0, G2, G3, G4 | G0, G2, G3, G4 |
| Reviewer | `data-contract-verifier` (the contract and its compatibility with every present reader: ADR-006 Tier B, "Contract/schema addition") | `code-reviewer` | a second `data-contract-verifier` agent (re-reads every official page) |
| Rule check | 4 rows | 5 rows | 1 row (R291, its share) |

## Files shared between pieces

- **Written by more than one piece: none.** The three sets of allowed paths do not overlap.
- **Read by one piece while another writes nearby:** M4-T030's tests read existing capture files; M4-T031 only adds new capture files and edits none. The readers of M4-T030 work from a sealed folder made before M4-T031 adds anything, so they do not have M4-T031's texts. **Watch at integration (learned in wave 2):** the reference cases must say "the readers did not have" a text, never that the repository lacks it; M4-T030's instructions say so, and the orchestrator reads that wording again after both commits are on the branch.
- **Read by one piece while another writes nearby:** M5-T128 changes the results schema, which the engine's validator, the drawing and CAD suites and the website's fixtures read. No other piece of this wave touches those readers. **Watch at integration:** the full `services/api` suite (the drawing and CAD snapshot suites are in it) is run after all three commits are on the branch; the website's checks run in CI on the pushed head.
- **Written by the orchestrator only:** `project-control/**` and `docs/DISCOVERY_BACKLOG.md`.
- **Shared test surface:** the full `services/api` suite covers all three. It is run once, by the orchestrator alone, on the branch after all three commits are integrated. No two heavy runs overlap on the server.

## Limits kept

- Helpers at the same time: at most five; at most three building; at most four reviewing. Planned peak: two builders and two readers (four), then three builders, then the reviewers as each builder finishes.
- Producer and reviewer are different agents for every piece; no reader of M4-T030 is its builder or its reviewer; the reviewers of M5-T128 and M4-T031 are different agents.
- Every review names the exact head it reviewed. A commit to a piece's files after its review voids that review. A failed review is recorded as failed, in the task's progress log and in its review record, and the piece goes back to its builder.
- One pull request for the wave, merged by the fail-closed step on a fully green run.

## Stop conditions

- A builder's commit touches a file outside its own allowed paths: that commit is not integrated; the piece goes back to its builder.
- Two pieces turn out to need the same file: the later one is taken out of the wave and sequenced after the merge.
- A piece fails its review and cannot be corrected quickly: it is taken off the branch before the wave's freeze so that it does not hold the other two.
- The contract cannot be made strictly additive (a present valid document would become invalid, or a present reader would have to change): the builder stops and reports; nothing non-additive is merged in this wave.
- A check requires a new valid results fixture for the new version: the builder stops and reports; the orchestrator decides (a new fixture is read by the drawing snapshot suites).
- A page of the official site does not answer for a capture: the capture says so; no text is filled from memory, an earlier report or another site.
- The two readings of M4-T030 differ on a point: the row stays "not known" with both readings named; the builder does not decide.
- Any Tier D matter (a secret, a payment, production): stop and tell the owner.

## Merge order

The wave merges as one pull request after all three tasks are accepted. If one piece is taken out, the other two merge first and it follows on a branch of its own from the new integration head. The clean-up of the temporary security exception (task M0-T183, not before 2026-10-07 14:09 UTC) is on a branch of its own after this wave, because it runs ledger commands and one ledger-touching branch is open at a time. After this wave: the engine (the heavy part of Part 0) and the website's display of the three ways, built side by side against the merged contract.
