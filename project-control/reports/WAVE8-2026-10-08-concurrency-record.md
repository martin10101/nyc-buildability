# Wave 8 (2026-10-08) - concurrency record for two pieces built at the same time

Written by the orchestrator before any builder of the wave is started, as the orchestration policy requires (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** Owner messages 107 and 108 of 2026-10-07 (D-090 source-052, rows R494 to R497): several independent parts at once, about five helpers, never on the same file. Bounds as recorded: at most five helpers at once, at most three building and at most four reviewing; heavy test runs one at a time; merges one at a time, in order; nothing built on unmerged work.

**Why these two.** Neither waits on an owner decision, and both follow from wave 7. (1) The two independent readings of step P5 named the law texts they did not have (backlog row DB-188): they are captured as source text, so that a later reading can settle the rows that say "not known" (the commercial floor area ratio; the amount of parking; the waivers; the Use Group categories). (2) The measurement-basis record still lists as "not decided" what the owner decided on 2026-10-07 (D-090 source-057, rows R539 to R545) and still says "not captured yet" for two texts that are now captured and read (backlog row DB-184, second piece). NOT in this wave, because it waits for the owner to settle where five results are carried in the results document (row R555): the piece that first emits contract version 1.3.0, and the website's display after it.

**One branch.** The two tasks ride on one branch, `task/wave8-captures-measurement-basis` (worktree `/root/project/w-wave8`), from the integration head `39e7f2d2`, the merge of wave 7 (pull request 468). The integration branch's own run on that merge commit is read as complete and successful BEFORE any builder's commit is integrated (recorded in the wave's progress entries). The orchestrator alone runs the ledger, git and the registry there. Each builder works in a worktree of its own and makes one commit per round, which the orchestrator integrates.

**How the packets were written.** Each packet was drafted by a read-only helper from the code at the head of pull request 468, then read and adjusted by the orchestrator; the drafts stay in the session folder and each adjustment is stated in the packet's path notes. Every entry of both packets' allowed paths is a literal file or a literal folder; the ledger now refuses anything else.

## The pieces

| | M4-T036 | M5-T135 |
|---|---|---|
| What | Capture, as source text only, the law texts the step-P5 readings name as missing (about 29 pages in six groups); no reading for any lot | The follow-up of the measurement-basis record: the owner's decisions of 2026-10-07 in the owner's words; the mixed-building rule and the energy eligibility stated from the captures; two sentences of one example that are now false; no estimator, no program code |
| Depends on | M4-T034, M4-T035: accepted and merged | M5-T133, M4-T034, M4-T035: accepted and merged |
| Depends on the other piece of this wave | no | no (it may quote only captures that exist at the claim head; what M4-T036 captures is written as an open question of law) |
| Builder | `legal-corpus-engineer` | `scenario-optimization-engineer` |
| Files it may write | new files in the folders `docs/research/zr-snapshots/v1` and `services/api/app/_zr_snapshots/v1` (named literally as folders); its report | `docs/measurement-basis/MEASUREMENT_BASIS.md`, the six example files, the five files under `services/api/tests/scenario/measurement_basis/` (each named literally); its report |
| Files it only reads | the existing captures; the last capture tasks' reports | the captures that exist at the claim head; the reference case of step P5; the owner's recorded decisions |
| Forbidden | every existing capture (it adds files only); reference cases; rules; register; the measurement-basis folder | `services/api/app/**`; the captures; the reference cases; every other document |
| Gates | G0, G2, G3, G4 | G0, G2, G3, G4 |
| Reviewers | `data-contract-verifier` (G3 and G4: it fetches every official page itself) | a second `data-contract-verifier` (G3: every quote against its capture; every decision against the owner's words) and a `qa-engineer` (G4: the tests) |
| Rule check | 3 rows | 11 rows |

## Files shared between pieces

- **Written by both: none.** One writes in the two capture folders; the other in the measurement-basis folder and its tests.
- **Read by one while the other writes nearby:** M5-T135 reads captures under `docs/research/zr-snapshots/v1/` while M4-T036 ADDS files there. M4-T036 edits no existing capture (its scenario S8), and M5-T135 may quote only captures that exist at the claim head, so what it reads cannot change under it. **Watch at integration:** after both commits are on the branch the orchestrator runs `tests/scenario`, `tests/rules`, `tests/contracts` and `tests/journey` together, then the full suite once.
- **Written by the orchestrator only:** `project-control/**` and `docs/DISCOVERY_BACKLOG.md`.

## Limits kept

- Helpers at the same time: at most five; at most three building; at most four reviewing. Planned start: two builders; reviewers as each finishes (three review seats in all).
- Producer and reviewer are different agents for every piece. Every review names the exact head it reviewed; a commit to a piece's files after its review voids that review; a failed review is recorded as failed, in the task's progress log and in its review record, before any rework.
- One pull request for the wave, merged by the fail-closed step on a fully green run. If a dependency check turns red for a reason outside the wave, nothing merges on a run that predates it.

## Stop conditions

- A builder's commit touches a file outside its own allowed paths: that commit is not integrated; the piece goes back to its builder.
- M4-T036: a section named in the packet does not exist on the official site as named, or has moved: the builder reports what the site shows and captures nothing under a guessed number. A page too large for the capture channel: the documented fallback, disclosed in the capture's notes, or the page is reported as not captured.
- M5-T135: a statement needs a text that is not captured at the claim head: it is written as an open question of law; nobody writes law from memory. An owner decision is quoted in the owner's words; nothing the owner called preliminary is written as validated.
- A piece fails its review and cannot be corrected quickly: it is taken off the branch before the wave's freeze so that it does not hold the other.
- Any Tier D matter (a secret, a payment, production): stop and tell the owner.

## Merge order

The wave merges as one pull request after both tasks are accepted. If one piece is taken out, the other merges first.
