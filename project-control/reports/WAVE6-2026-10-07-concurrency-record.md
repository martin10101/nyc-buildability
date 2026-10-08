# Wave 6 (2026-10-07) - concurrency record for three pieces built at the same time

Written by the orchestrator before any builder of the wave is started, as the orchestration policy requires (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** Owner messages 107 and 108 of 2026-10-07 (D-090 source-052, rows R494 to R497): several independent parts at once, about five helpers, never on the same file. Bounds as recorded: at most five helpers at once, at most three building and at most four reviewing; heavy test runs one at a time; merges one at a time, in order; nothing built on unmerged work.

**Why these three.** Owner message 111 of 2026-10-07 (D-090 source-055) carries a check by the owner's reviewer. It asks for three repairs before the apartment estimator is approved and before the decision module's results are shown to a user (row R531): the two wrong explanations, the worked example that does not fit, and the rule on shared floor area. The corrections come first; the piece that wires the decision module into the real path and the reading of the newer captures follow in the next wave.

**One branch.** The three tasks ride on one branch, `task/wave6-corrections-after-reviewer-check` (worktree `/root/project/w-wave6`), from the integration head `f111b927`, the merge of wave 5 (pull request 464). The integration branch's own run on that merge commit is read as complete and successful BEFORE any builder's commit is integrated (recorded in the wave's progress entries). The orchestrator alone runs the ledger, git and the registry there. Each builder works in a worktree of its own and makes one commit per round, which the orchestrator cherry-picks.

## The pieces

| | M5-T132 | M5-T133 | M4-T034 |
|---|---|---|---|
| What | The decision module's explanations: a table of every input state, one repair, one test per state; texts only | The measurement-basis record and its three worked examples corrected; a test of the fit | Law-text captures behind the reviewer's check (source text only) |
| Depends on | M5-T129, M5-T130: accepted and merged | M5-T126, M4-T033: accepted and merged | M4-T033: accepted and merged |
| Depends on another piece of this wave | no | no (it reads only captures that exist at the claim head; what M4-T034 captures is written as "not captured yet") | no |
| Builder | `scenario-optimization-engineer` | a second `scenario-optimization-engineer` agent | `legal-corpus-engineer` |
| Files it may write | `services/api/app/scenario/three_answers/result_ways.py`, `result_way_*.py`; `services/api/tests/scenario/three_answers/test_result_ways.py`, `test_result_ways_*.py`, `test_result_way_*.py`; its report | `docs/measurement-basis/**`; `services/api/tests/scenario/measurement_basis/**`; its report | new files under `docs/research/zr-snapshots/v1/` and `services/api/app/_zr_snapshots/v1/`; `services/api/tests/rules/test_zr_snapshot_bundle.py` only if it lists ids; its report |
| Files it only reads | the work order; the reports of M5-T129 and M5-T130 | the existing captures; the report and review record of M5-T126 | the existing captures; the report of M4-T033 |
| Forbidden | every other app file; every other test; `packages/**`; `apps/**`; `docs/**` | `services/api/app/**`; the captures; the reference cases; every other docs file | every existing capture; reference cases; rules; register; the measurement-basis folder |
| Gates | G0, G2, G3, G4 | G0, G2, G3, G4 | G0, G2, G3, G4 |
| Reviewers | `data-contract-verifier` (G3) and `qa-engineer` (G4): ADR-006 Tier B, "Scenario calculation" | a second `data-contract-verifier` (G3: every quote against its capture; floors by hand) and a second `qa-engineer` (G4: the fit check) | a third `data-contract-verifier` (G3 and G4) |
| Rule check | 6 rows | 13 rows | 5 rows |

## Files shared between pieces

- **Written by more than one piece: none.** The three write in three different folder families: the decision modules and their tests; the measurement-basis documents and their tests; the capture folders.
- **Both under `services/api/tests/scenario/`:** M5-T132 writes only in `three_answers/`, M5-T133 only in `measurement_basis/`. Neither folder's tests import the other's.
- **Read by one piece while another writes nearby:** M5-T133 reads captures under `docs/research/zr-snapshots/v1/` while M4-T034 ADDS files there. M4-T034 edits no existing capture (its scenario S4), and M5-T133 may quote only captures that exist at the claim head (its scenario S8), so what it reads cannot change under it. **Watch at integration:** after all commits are on the branch the orchestrator runs `tests/scenario`, `tests/rules`, `tests/contracts` and `tests/journey` together.
- **Written by the orchestrator only:** `project-control/**` and `docs/DISCOVERY_BACKLOG.md`.
- **Shared test surface:** the full `services/api` suite covers all three. It is run once, by the orchestrator alone, on the branch after all commits are integrated.

## Limits kept

- Helpers at the same time: at most five; at most three building; at most four reviewing. Planned peak: three builders, then reviewers as the builders finish. The wave has five review seats (two, two and one); never more than four reviewers run at once: the fifth starts when one returns.
- Producer and reviewer are different agents for every piece. The two `scenario-optimization-engineer` builders are two separate agents with separate worktrees and no shared file.
- Every review names the exact head it reviewed. A commit to a piece's files after its review voids that review. A failed review is recorded as failed, in the task's progress log and in its review record, and the piece goes back to a builder.
- One pull request for the wave, merged by the fail-closed step on a fully green run.

## Stop conditions

- A builder's commit touches a file outside its own allowed paths: that commit is not integrated; the piece goes back to its builder.
- M5-T132 cannot correct a text without changing the way a result appears: the builder stops and reports; the way is not changed.
- M5-T133 needs a statement of law whose text is not captured: it writes "not captured yet"; nobody writes law from memory or from the reviewer's message.
- M4-T034 finds that the official site does not bear out a section number the reviewer names: it reports what the site shows; the orchestrator tells the owner before any record changes because of it (row R517).
- A piece fails its review and cannot be corrected quickly: it is taken off the branch before the wave's freeze so that it does not hold the others.
- Any Tier D matter (a secret, a payment, production): stop and tell the owner.

## Merge order

The wave merges as one pull request after all three tasks are accepted. If one piece is taken out, the others merge first.
