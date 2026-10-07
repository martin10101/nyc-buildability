# Wave 1 (2026-10-07) - concurrency record for three pieces built at the same time

Written by the orchestrator before any builder of the wave is started, as the orchestration policy requires (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** Owner messages 107 and 108 of 2026-10-07 (D-090 source-052): "run a few difrint parts of the program at once", "obviously not anything that will collide with each other or work on the same file", "Like spine up 5 subagents". Rows R494 to R497. The orchestrator's reading of the bounds, told to the owner: at most five helpers at once, at most three building and at most four reviewing; heavy test runs one at a time; merges one at a time, in order; nothing built on unmerged work.

**One branch.** All three tasks ride on one branch, `task/wave1-measurement-basis-p2-captures-reference-cases` (worktree `/root/project/w-wave1`), from the integration head `a5c6c2f0` (the merge of the law-text captures, task M4-T025). The orchestrator alone runs the ledger, git and the registry there, one command at a time. Each builder works in a worktree of its own and makes one commit, which the orchestrator cherry-picks.

## The pieces

| | M5-T126 | M4-T026 | M4-T027 |
|---|---|---|---|
| What | The measurement basis for the apartment estimate, as a record with worked examples (no estimator) | Law-text captures, step P2: ZR 34-11, 34-111, 34-24, 35-53, 35-63 and every section under it | The R6B reference cases worked from the text captured in step P1 |
| Depends on | M4-T025: accepted and merged | M4-T025: accepted and merged | M4-T024 and M4-T025: both accepted and merged |
| Depends on another piece of this wave | no | no | no |
| Builder | `scenario-optimization-engineer` | `legal-corpus-engineer` | `rules-engineer`, started only after two independent readings are in (reader 1 `official-source-researcher`, reader 2 `geospatial-engineer`; both work outside the repository from a sealed folder) |
| Files it may write | `docs/measurement-basis/**`; `services/api/tests/scenario/measurement_basis/**`; its report | `docs/research/zr-snapshots/v1/**` (new files only); `services/api/app/_zr_snapshots/v1/**`; `services/api/tests/rules/test_zr_snapshot_bundle.py` only if it lists captures; its report | `docs/reference-cases/R6B/**`; `services/api/tests/rules/reference_cases/**`; its report |
| Files it only reads | the captures of M4-T025; the reference cases; `services/api/app/scenario/three_answers/` | the captures of M4-T025; the research lead | the captures; the two readings |
| Forbidden | `services/api/app/**`, every capture, plan, reference case, register | every existing capture, rule file, register, reference case, plan | `services/api/app/**`, every capture, register, plan |
| Gates | G0, G2, G3, G4 | G0, G2, G3, G4 | G0, G2, G3, G4 |
| Reviewer | `code-reviewer` | `data-contract-verifier` (re-reads every official page) | a second `code-reviewer` agent (re-works every numeric row) |
| Rule check | 20 rows | 1 row (R291, its share) | 6 rows |

## Files shared between pieces

- **Written by more than one piece: none.** The three sets of allowed paths do not overlap.
- **Read by one piece while another writes nearby:** M4-T027's tests read existing capture files under `docs/research/zr-snapshots/v1/`; M4-T026 only adds new files there and edits none, and each builder works in its own worktree, so neither sees the other's files before integration.
- **Written by the orchestrator only:** `project-control/**` (ledger, registry, records) and `docs/DISCOVERY_BACKLOG.md`.
- **Shared test surface:** the full `services/api` suite covers all three. It is run once, by the orchestrator alone, on the branch after all three commits are integrated. No two heavy runs overlap on the server.

## Limits kept

- Helpers at the same time: at most five; at most three building; at most four reviewing. Planned peak: two builders and two readers (four), then three builders, then the reviewers as each builder finishes.
- Producer and reviewer are different agents for every piece; no reader of M4-T027 is its builder or its reviewer.
- Every review names the exact head it reviewed. A commit to a piece's files after its review voids that review.
- One pull request for the wave, merged by the fail-closed step on a fully green run. The integration branch's own run on `a5c6c2f0` is read before that merge.

## Stop conditions

- A builder's commit touches a file outside its own allowed paths: that commit is not integrated; the piece goes back to its builder.
- Two pieces turn out to need the same file: the later one is taken out of the wave and sequenced after the merge.
- A piece fails its review and cannot be corrected quickly: it is taken off the branch (its commit reverted before the wave's freeze, its task left in rework) so that it does not hold the other two.
- A page of the official site does not answer for a capture: the capture says so; no text is filled from memory, a lead or another site.
- The two readings of M4-T027 differ on a point: the row stays "not known" with both readings named; the builder does not decide.
- Any Tier D matter (a secret, a payment, production): stop and tell the owner.

## Merge order

The wave merges as one pull request after all three tasks are accepted. If one piece is taken out, the other two merge first and it follows on a branch of its own from the new integration head. After the wave: the clean-up of the temporary security exception (task M0-T183, not before 2026-10-07 14:09 UTC), on a branch of its own.
