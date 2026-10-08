# Wave 7 (2026-10-08) - concurrency record for three pieces built at the same time

Written by the orchestrator before any builder of the wave is started, as the orchestration policy requires (`.claude/ORCHESTRATION_POLICY.md`, sections B, C and F).

**Authority.** Owner messages 107 and 108 of 2026-10-07 (D-090 source-052, rows R494 to R497): several independent parts at once, about five helpers, never on the same file. Bounds as recorded: at most five helpers at once, at most three building and at most four reviewing; heavy test runs one at a time; merges one at a time, in order; nothing built on unmerged work.

**Why these three.** They are the next pieces in the recorded order (the handoff of 2026-10-07, "Waiting work" item 3) and none waits on an owner decision: the piece that wires the decision module into the real path (row R531: the integration work continues), the independent reading of the law texts that waves 5 and 6 captured and nobody has read (backlog row DB-184; with it the reading that says which of two existing answers on the benchmark lot's rear yard is right, backlog row DB-185 point b), and the repair of the ledger's seal that the owner asked to keep tracked until it is done (row R557; backlog row DB-181). NOT in this wave, because it waits for the owner to settle where five results are carried in the results document (row R555): the piece that first emits contract version 1.3.0, and the website's display after it.

**One branch.** The three tasks ride on one branch, `task/wave7-wiring-reading-seal` (worktree `/root/project/w-wave7`), from the integration head `85500b94`, the merge of wave 6 and the security upgrade (pull request 466). The integration branch's own run on that merge commit is read as complete and successful BEFORE any builder's commit is integrated (recorded in the wave's progress entries). The orchestrator alone runs the ledger, git and the registry there. Each builder works in a worktree of its own and makes one commit per round, which the orchestrator integrates.

**How the packets were written.** Each packet was drafted by a read-only helper from the code at the head of pull request 466 (a scoping study for the wiring piece; a draft for each of the other two), then read and adjusted by the orchestrator; the drafts stay in the session folder and each adjustment is stated in the packet's path notes.

## The pieces

| | M5-T134 | M4-T035 | M0-T188 |
|---|---|---|---|
| What | Wire the carriers: the property profile, the site geometry and the prepared outline are surfaced on the real path and handed to the decision module through one new thin adapter that returns the ways beside the engine's result; nothing is emitted | The independent reading of the newly captured law texts into the R6B reference cases (a new step-P5 case); one mixed building worked by hand; what each option's parking, loading and bicycle line may say; the benchmark lot's rear yard read from the text | Repair the ledger's seal: a pattern entry in a packet's allowed paths is refused at contract time, at claim and at submit; a look-back report; no old record is rewritten |
| Depends on | M5-T129, M5-T130, M5-T131, M5-T132: accepted and merged | M4-T032, M4-T033, M4-T034: accepted and merged | nothing |
| Depends on another piece of this wave | no | no | no (its commits are integrated LAST, see below) |
| Builder | `scenario-optimization-engineer` | `rules-engineer`, started only when the orchestrator holds two independent readings, each made by a different helper working alone from a sealed folder | `backend-engineer` |
| Files it may write | four named files under `services/api/app/` (`api/v1/study_inputs.py`, `api/v1/study_live_geometry.py`, `scenario/three_answers/inputs.py`, `contracts/evaluator_inputs.py`), one new module `scenario/three_answers/result_way_engine_bridge.py`, six named test files, its report | the folders `docs/reference-cases/R6B` and `services/api/tests/rules/reference_cases` (named literally as folders), its report | `tools/directive_registry.py`, `tools/project_control.py`, `tools/validate_directive_compliance.py`, `tools/test_project_control.py`, one new test file, its two reports |
| Files it only reads | the decision modules and their tests; the work order; backlog rows DB-171, DB-172, DB-175 | the captures; the two benchmark test files; the two readings | every task packet, gate record and directive record (for the look-back) |
| Forbidden | the decision module's files and texts; `engine.py`; the contract schema, fixtures and snapshots; `apps/**`; every switch | `services/api/app/**`; the captures; the review register; the measurement-basis folder; plans | every task, gate and directive record; every workflow; `.claude/**`; `services/**` |
| Gates | G0, G2, G3, G4 | G0, G2, G3, G4 | G0, G2, G3, G4, G5 |
| Reviewers | `data-contract-verifier` (G3) and `qa-engineer` (G4): ADR-006 Tier B, "Scenario calculation" | a second `data-contract-verifier` (G3 and G4: it fetches the official pages itself and compares every quote) | `code-reviewer` (G3 and G4) and `security-reviewer` (G5): ledger tooling |
| Rule check | 7 rows | 5 rows | 1 row |

## Files shared between pieces

- **Written by more than one piece: none.** The three write in three different families: server modules and their tests; reference-case documents and their test support; the ledger's tools.
- **Read by one piece while another writes nearby:** none. M4-T035 reads the two benchmark test files under `services/api/tests/scenario/three_answers/`; M5-T134 adds and changes other test files in that folder and does not change those two.
- **The ledger's tools change inside the wave (M0-T188).** The orchestrator uses those tools for all three tasks. Therefore M0-T188's commits are integrated onto the branch LAST, after M5-T134 and M4-T035 have been submitted and gated with the unchanged tools. Its builder works from the claim head in its own worktree, so nothing it does reaches the branch before then.
- **Written by the orchestrator only:** `project-control/**` and `docs/DISCOVERY_BACKLOG.md`.
- **Shared test surface:** the full `services/api` suite covers M5-T134 and M4-T035. It is run once, by the orchestrator alone, on the branch after their commits are integrated. M0-T188's tests are the focused ledger tests and the registry validator; the long directive-compliance suite is CI's.

## Limits kept

- Helpers at the same time: at most five; at most three building; at most four reviewing. Planned start: two builders (M5-T134, M0-T188) and the two readers of M4-T035 (four helpers, two building); the builder of M4-T035 starts when both readings are in. Reviewers start as builders finish; never more than four reviewing at once.
- Producer and reviewer are different agents for every piece. The two readers of M4-T035 are two different helpers; neither is its builder or its reviewer; neither may open the repository or the web.
- Every review names the exact head it reviewed. A commit to a piece's files after its review voids that review. A failed review is recorded as failed, in the task's progress log and in its review record, before any rework.
- One pull request for the wave, merged by the fail-closed step on a fully green run. If a dependency check turns red for a reason outside the wave, nothing merges on a run that predates it (as with blockers B-030 and B-031).

## Stop conditions

- A builder's commit touches a file outside its own allowed paths: that commit is not integrated; the piece goes back to its builder.
- M5-T134 cannot keep the emitted results document byte-identical: the builder stops and reports; nothing is emitted in this task.
- M4-T035: the two readings disagree on a point: the reference row says "not sure" with both readings named; nobody writes law from memory. A reading that would change what the program outputs is recorded in the reference case and in the backlog; no engine file changes in this task.
- M0-T188: any accepted task would stop validating after the change: the builder stops and reports; no old record is rewritten to make it pass.
- A piece fails its review and cannot be corrected quickly: it is taken off the branch before the wave's freeze so that it does not hold the others.
- Any Tier D matter (a secret, a payment, production): stop and tell the owner.

## Merge order

The wave merges as one pull request after the tasks on it are accepted. If one piece is taken out, the others merge first.
