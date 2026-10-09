# Wave 2 (2026-10-07) - concurrency record for three pieces built at the same time

Written by the orchestrator before any builder of the wave is started, as the orchestration policy requires (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** Owner messages 107 and 108 of 2026-10-07 (D-090 source-052, rows R494 to R497): several independent parts at once, about five helpers, never on the same file. Bounds as recorded: at most five helpers at once, at most three building and at most four reviewing; heavy test runs one at a time; merges one at a time, in order; nothing built on unmerged work.

**One branch.** All three tasks ride on one branch, `task/wave2-lot-reach-overlay-reading-further-captures` (worktree `/root/project/w-wave2`), from the integration head `4fc0d85c` (the merge of wave 1). The orchestrator alone runs the ledger, git and the registry there. Each builder works in a worktree of its own and makes one commit, which the orchestrator cherry-picks.

**Order.** These are the next steps of the R6B work order after the steps merged so far (reference cases, step-P1 captures, step-P2 captures, the reference cases from the step-P1 text): the independent reading of the step-P2 text; the first new file of Part 0; and the capture of text the merged readings named as missing. None is built on unmerged work.

## The pieces

| | M5-T127 | M4-T028 | M4-T029 |
|---|---|---|---|
| What | The lot-reach measurements (from each street line and from the corner point), measurements only | The independent reading of the commercial-overlay text, written into the R6B reference cases | Law-text captures the readings named as missing |
| Depends on | M4-T027: accepted and merged | M4-T026 and M4-T027: accepted and merged | M4-T026: accepted and merged |
| Depends on another piece of this wave | no | no | no |
| Builder | `geospatial-engineer` | `rules-engineer`, started only after two independent readings are in (two reader agents of different types, both working outside the repository from a sealed folder) | `legal-corpus-engineer` |
| Files it may write | `services/api/app/spatial/lot_reach.py`; `services/api/tests/spatial/test_lot_reach.py`; its report | `docs/reference-cases/R6B/**`; `services/api/tests/rules/reference_cases/**`; its report | `docs/research/zr-snapshots/v1/**` (new files only); `services/api/app/_zr_snapshots/v1/**`; `services/api/tests/rules/test_zr_snapshot_bundle.py` only if it lists captures; its report |
| Files it only reads | `services/api/app/spatial/site_geometry/**`; the corner-reach reference case and its loader | the captures; the two readings | the existing captures; the earlier producer reports |
| Forbidden | every existing file under `services/api/app/**`; every document; every other test | `services/api/app/**`; every capture; register; plans | every existing capture; rule files; register; reference cases; plans |
| Gates | G0, G2, G3, G4 | G0, G2, G3, G4 | G0, G2, G3, G4 |
| Reviewer | `code-reviewer` | a second `code-reviewer` agent | `data-contract-verifier` (re-reads every official page) |
| Rule check | 3 rows | 5 rows | 1 row (R291, its share) |

## Files shared between pieces

- **Written by more than one piece: none.** The three sets of allowed paths do not overlap.
- **Read by one piece while another writes nearby:** M5-T127's test reads `docs/reference-cases/R6B/cases/corner-reach.json` through the loader in `services/api/tests/rules/reference_cases/`; M4-T028 may extend that loader and adds rows to other case files. Each builder works in its own worktree from the claim head, so neither sees the other's changes before integration. **Watch at integration:** after both commits are on the branch, the orchestrator runs M5-T127's test again against M4-T028's version of the loader and of the corner-reach case; M4-T028's packet forbids changing an existing expected value without both readings, and the four reach rows are not in its scope. If the reach rows or the loader's interface change, M5-T127's test is re-checked by its builder before review.
- **Read by one piece while another adds files nearby:** M4-T028's tests read existing capture files; M4-T029 only adds new capture files and edits none.
- **Written by the orchestrator only:** `project-control/**` and `docs/DISCOVERY_BACKLOG.md`.
- **Shared test surface:** the full `services/api` suite covers all three. It is run once, by the orchestrator alone, on the branch after all three commits are integrated. No two heavy runs overlap on the server.

## Limits kept

- Helpers at the same time: at most five; at most three building; at most four reviewing. Planned peak: two builders and two readers (four), then three builders, then the reviewers as each builder finishes.
- Producer and reviewer are different agents for every piece; no reader of M4-T028 is its builder or its reviewer; the two reviewers of M5-T127 and M4-T028 are different agents.
- Every review names the exact head it reviewed. A commit to a piece's files after its review voids that review.
- One pull request for the wave, merged by the fail-closed step on a fully green run. The integration branch's own run on `4fc0d85c` is read before that merge.

## Stop conditions

- A builder's commit touches a file outside its own allowed paths: that commit is not integrated; the piece goes back to its builder.
- Two pieces turn out to need the same file: the later one is taken out of the wave and sequenced after the merge.
- A piece fails its review and cannot be corrected quickly: it is taken off the branch before the wave's freeze so that it does not hold the other two.
- M5-T127's measurement and a reference value differ by more than the stated tolerance: the builder stops and reports both; neither is adjusted.
- A page of the official site does not answer for a capture: the capture says so; no text is filled from memory, an earlier report or another site.
- The two readings of M4-T028 differ on a point: the row stays "not known" with both readings named; the builder does not decide.
- Any Tier D matter (a secret, a payment, production): stop and tell the owner.

## Merge order

The wave merges as one pull request after all three tasks are accepted. If one piece is taken out, the other two merge first and it follows on a branch of its own from the new integration head. The clean-up of the temporary security exception (task M0-T183, not before 2026-10-07 14:09 UTC) is on a branch of its own after this wave, because it runs ledger commands and one ledger-touching branch is open at a time.
