# M0-T034 — producer report

**Task:** Governance acceptance semantics: lifecycle-aware `accept()` + real guards for
governance-shaped tasks
**Producer:** `backend-engineer` (this report is producer evidence, not a gate verdict)
**Base commit:** round 1 `05ee1917291659d18f88718a6b73e51cf619d4ff`; **round 2 (rework)**
`1298f4b85edcc81409afbde23d570a22bbc389ff`
**Directive:** D-004, Message F item 2 (rows `D-004-R627..R633`)
**Rounds:** §§0–8 are the round-1 record submitted to G3/G5, which both returned **FAIL**.
**§§9–10 are the rework**, and where they contradict §§0–8 the rework governs.

> A worker agent cannot mark its own task complete. Everything below is evidence submitted
> for an independent gate. Where I could not prove something, it says so in plain words.
> A FAIL-then-fix does not inherit a pass: this asks for fresh G3 and G5 verdicts at the new
> frozen SHA, not a re-reading of the round-1 verdicts.

---

## 0. Environment note the reviewer needs first

The task branch `task/M0-T034-governance-acceptance-semantics` is checked out in the **shared
checkout**, but this agent is worktree-isolated: any `git` command targeting the shared checkout
is refused by the isolation guard with

```
This agent is isolated in the worktree C:\...\.claude\worktrees\agent-a8497f73f558bac2a,
but this command changes directory to the shared checkout ... Refusing to run it
```

I therefore fast-forwarded **my own** worktree branch to the exact task base and did all work
there:

```
$ git merge --ff-only 05ee1917291659d18f88718a6b73e51cf619d4ff
Updating dc842e8..05ee191
Fast-forward
 project-control/state.json         |   3 +-
 project-control/tasks/M0-T034.json | 104 +++++++++++++++++++++++++++++++++++++
 2 files changed, 106 insertions(+), 1 deletion(-)
$ git rev-parse HEAD
05ee1917291659d18f88718a6b73e51cf619d4ff
```

**All changed files live in the worktree `.claude/worktrees/agent-a8497f73f558bac2a` on branch
`worktree-agent-a8497f73f558bac2a`, uncommitted, at base `05ee1917`.** The orchestrator must
integrate from there, not from the shared checkout (which shows no diff).

**Round 2 (rework after two FAIL gates) ran in a DIFFERENT worktree.** The same isolation applies:
the rework was produced in `.claude/worktrees/agent-aa6a2a030ff145fe0` on branch
`worktree-agent-aa6a2a030ff145fe0`, which I fast-forwarded to the round-1 task tip:

```
$ git reset --hard 1298f4b85edcc81409afbde23d570a22bbc389ff
HEAD is now at 1298f4b M0-T034: producer self-check recorded (in_progress -> self_check)
$ git rev-parse HEAD
1298f4b85edcc81409afbde23d570a22bbc389ff
```

One consequence a reviewer should know: that worktree's copy of
`project-control/tasks/M0-T034.json` is the committed one at `1298f4b`, which does **not** yet
contain owner ruling C2 or the G3/G5 rework entry — those exist only in the shared checkout's
working tree. I read the packet from the shared checkout **read-only** to get the current text,
and did not write to it (it is an orchestrator lifecycle path).

---

## 1. What changed and why

| File | Change |
|---|---|
| `tools/directive_registry.py` | The stated acceptance-ordering classification rule + `acceptance_ordering_deferral()`; `task_verification_result()` returning `(reasons, deferrals)`; `requirement_verification_state()`; **actual `reviewed_sha` comparison** in both the v2 and v1 verification paths; the **control-plane material identity** (`control_plane_entries`, `control_plane_material_dirty`, `_hash_manifest_entries`, `_ls_tree_entries`, `_status_records`); `frozen_git_identity(..., control_plane_prefixes=)`. |
| `tools/project_control.py` | `_task_git_identity` now passes the control-plane prefixes, so submit/gate/accept share one identity; `_directive_accept_reasons` returns `(reasons, deferrals)` and passes the resolved commit for the `reviewed_sha` check; `accept()` records deferrals on the packet under `post_accept_verification`; `checkpoint()` is the **first post-accept opportunity** and refuses while any deferral is unverified; module docstring gained `LIFECYCLE-AWARE ACCEPTANCE` and `CONTROL-PLANE CONTENT IDENTITY` sections. |
| `tools/test_project_control.py` | New group **S11** (5 test functions) proving AS-1..AS-8 and AS-12 end-to-end through the CLI; `make_directive` extended to author rows with explicit `classification` / `lifecycle_events`. |
| `tools/test_directive_compliance.py` | New verification-layer tests: the classifier's five conditions each proven necessary, the source-level generality proofs, the `reviewed_sha` comparison, and the control-plane material identity / dirt guard. |

**Round 2 adds to the same four files** (full detail in §9):

| File | Round-2 change |
|---|---|
| `tools/directive_registry.py` | condition (5) inverted from the denylist `NEGATIVE_VERIFICATION_STATES` to the allowlist `DEFERRABLE_VERIFICATION_STATES` with an `isinstance` guard, and the stated rule rewritten to match; condition (2) now requires a **known producer**, a **dated** `classified_at` (`_is_dated_attestation`), and case/whitespace-insensitive identity comparison (`_identity_key`, `_text`); a missing producer is an explicit fail-closed reason in **both** `_v2_task_unresolved` and `_v1_task_unresolved`; new `_task_verification_container`, `_row_is_satisfied`, **`deferred_requirement_discharge`** (the same-standard discharge) and **`outstanding_lifecycle_claims`** (registry re-derivation). |
| `tools/project_control.py` | `_post_accept_verification_blockers()` rewritten: discharges via `deferred_requirement_discharge` bound to `deferred_at_identity`/`deferred_at_sha`, and unions the packet-recorded deferrals with a **re-derivation from the registry** over every accepted in-regime task; module docstring gains the `DEFERRAL IS NOT WAIVER` paragraph. |
| `tools/test_project_control.py` | AS-2 grows **10 → 35 cases**, probing outside the old denylist; two new S11 groups (`..._deferral_is_not_waiver_...`, `..._missing_producer_identity_fails_closed`), so the suite runs **22** groups. |
| `tools/test_directive_compliance.py` | **83 → 98 tests**: condition-(5) allowlist test replacing the denylist-iterating one, a never-raises test over unhashable states, producer-identity and dated-attestation tests, and the 12-test `DeferredDischargeStandardTests`. |

`tools/validate_directive_compliance.py` was **not** touched (forbidden on purpose: it stays an
independent check on the code I changed). No file under `project-control/directives/**` was
touched. No requirement row's `applicability` was edited in place (`D-004-R627`).

---

## 2. The stated classifier rule (AS-12)

The rule is written in the code, in `tools/directive_registry.py`, as a block comment headed
`ACCEPTANCE-ORDERING LIFECYCLE CLASSIFICATION`, immediately above the constants and the
function that implement it. It quotes `D-004-R629` verbatim and then states:

> A requirement row may be treated as an acceptance-ordering lifecycle act — recorded
> EVALUATED-AND-DEFERRED instead of gating `accept()` — **if and only if ALL FIVE conditions
> below hold TOGETHER.**

1. **ACT CLASS.** The verification row carries a `lifecycle_classification` object whose
   `act_class` is in `ACCEPTANCE_ORDERING_ACT_CLASSES` — the owner's **closed** four-item
   enumeration transcribed from R629: `accept`, `post_accept_cleanup`, `checkpoint`,
   `stop_after`. The code never extends the enumeration.
2. **INDEPENDENT, DATED ATTESTATION** *(amended in round 2 — F3, F5, F6)*. That object records a
   non-empty `classified_by` that is **not** the producer of the verification record, a non-empty
   `justification`, and a well-formed **dated** `classified_at`. Identities are compared
   **case- and whitespace-insensitively**, and a **missing or empty producer REFUSES** rather
   than silently disabling the independence test. Per `D-004-R632` the sufficient judgment is the
   independent verifier's; this module supplies **necessary** conditions only and deliberately
   refuses to supply the sufficient one.
3. **LIFECYCLE BINDING (row semantics).** The requirement row's own
   `applicability.lifecycle_events` is non-empty and a **subset** of
   `ACCEPTANCE_ORDERING_LIFECYCLE_EVENTS = {"accept"}`. This is the mechanical reading of
   R629's word **"SOLE"**: a row that also binds an obligation at `claim`/`progress`/`submit`/
   `gate` had a duty that *was* satisfiable before acceptance, so it keeps gating.
4. **ELIGIBLE CLASSIFICATION (row semantics).** The row's own `classification` is in
   `LIFECYCLE_ELIGIBLE_CLASSIFICATIONS = {"obligation", "sequencing"}` — an **allowlist**. An
   acceptance-ordering *act* is something the executor does (`obligation`) or an ordering
   constraint on when it may stop (`sequencing`). Every other classification the schema permits
   — `prohibition`, `hold`, `decision`, `authorization`, `dependency`, `harness`, `evidence`,
   `external_fact`, `return` — is a **bar** on acceptance or an evidentiary/return duty, not an
   act performed at acceptance. Deferring a `prohibition`/`hold`/`authorization` bound to
   acceptance would waive the very bar that says "do not accept yet"; those are excluded
   structurally so that **no attestation, however well-formed, can reach them.**
5. **EXPLICITLY PENDING VERIFICATION STATE** *(rewritten in round 2 — defect D1)*. The row's
   `state` is a **string** drawn from `DEFERRABLE_VERIFICATION_STATES = {"pending"}`. Round 1 had
   this condition backwards: it was the **denylist** `NEGATIVE_VERIFICATION_STATES = {FAIL,
   BLOCKED}`, the only denylist in an otherwise all-allowlist rule, so every value its author had
   not enumerated was *released* — including **`UNVERIFIABLE`**, the independent verifier stating
   it **could not verify** the obligation, which is schema-valid, validator-valid and reachable
   through a clean registry with green CI. Absent, `null`, unknown, lowercase and whitespace-
   padded states leaked the same way, and `state: []` raised an uncaught `TypeError`, falsifying
   the classifier's own docstring. It is now an allowlist with an `isinstance(state, str)` guard
   evaluated **first**, so a malformed state refuses and never raises.

**Why (3) admits only `"accept"`.** I measured the registry's actual `lifecycle_events`
vocabulary across all D-004 rows: it is exactly `{claim, progress, submit, gate, accept}`.
Verified by exhaustive grep — a search for `checkpoint|post_accept|stop_after|merge|commit|
cleanup|close|blocker|review|report|dispatch|plan|verify` as a `lifecycle_events` element
returned **`No matches found`**. `accept` is the only token denoting an act at or after
acceptance. I deliberately did **not** add tokens that do not exist in the vocabulary: defining
semantics for an unused token would widen the rule on speculation, and rider 1 says a rule one
notch too permissive is the worst outcome.

**Known limit, stated in the code on purpose.** Conditions (3) and (4) cannot separate an
ordering constraint that is an *act* ("stop AFTER acceptance") from one that is a *bar* ("stop
BEFORE acceptance") — both are `sequencing` rows bound to `accept`. That discrimination is
exactly the semantic judgment `D-004-R632` assigns to the independent verifier, which is why
(1)+(2) are mandatory rather than advisory. I would rather a reviewer reject this design than
have it silently swallow a "stop before accept" row.

**Deferral is not waiver** *(made true in code in round 2 — defect F2)*. A deferred row is never
deleted, waived, rewritten to `PASS`, or silently passed. `accept()` records it on the task packet
under `post_accept_verification`, and `checkpoint()` — the first post-accept opportunity the
control plane offers — refuses to record while any registered deferral is still **discharged to
the same standard as the gate that deferred it**: an independent verifier (present, and not the
producer), the content identity **and** reviewed commit the deferral was granted at, and a `PASS`
(or a justified, independently approved `NOT_APPLICABLE`). In round 1 this paragraph was true only
as prose: the discharge accepted a **bare** `state: "PASS"` written at any time, at any identity,
by anyone including the producer, which held the deferred obligation to a *lower* bar than an
ordinary requirement and inverted the design's own premise.

---

## 3. The staleness-vs-lifecycle resolution (the design tension)

**The tension.** AS-5 asks that a change to a file inside `allowed_paths` move the recorded
identity, and names the concrete case: `project-control/tasks/M0-T027.json` changed between
`f08769e1` and `16ae4589` while the identity did not. I re-derived that delta myself:

```
$ git diff --name-only f08769e1 16ae4589 -- project-control/reports/AGENT-TEAMS-PILOT-1.md \
    project-control/reports/AGENT-TEAMS-PILOT-2-PROBE.md \
    project-control/reports/AGENT-TEAMS-PILOT-3.md \
    project-control/reports/M0-T027-producer-report.md \
    project-control/tasks/M0-T027.json
project-control/tasks/M0-T027.json

$ git diff f08769e1 16ae4589 -- project-control/tasks/M0-T027.json
-  "status": "in_progress",
-  "progress_percent": 90,
+  "status": "awaiting_gate",
+  "progress_percent": 85,
-  "updated_at": "2026-07-30T20:24:27.966508+00:00",
+  "updated_at": "2026-07-31T04:40:02.965885+00:00",
```

Exactly three keys differ — `status`, `progress_percent`, `updated_at` — every one of them
outside `MATERIAL_FIELDS`. That specific delta is **pure lifecycle bookkeeping**.

**Why the literal reading is impossible, not merely inconvenient.** The control plane rewrites
its own records *between* the moment an identity is stamped and the moment it is checked:
`submit()` stamps the identity and then writes `status`/`progress` to the packet; `gate()` writes
`progress_percent` after stamping its own record; `accept()` then recomputes and compares. A raw
blob-id identity over the task's own packet is therefore **stale the instant it is recorded**,
and no task could ever be accepted. I did not assert this — I proved it executably:
`ControlPlaneMaterialIdentityTests.test_raw_blob_control_plane_identity_would_be_unusable`
shows the raw-blob manifest moving on a lifecycle-only transition while the material identity
holds, and `S11 (d)` shows the CLI accepting only because a lifecycle-only packet delta is not
treated as dirt.

**My resolution.** Keep the exclusion for the *raw-blob* component, and measure the excluded
tree by a **material identity** instead:

* a task packet (`project-control/tasks/*.json`) contributes `material_digest(packet)` — the
  owner's **own** material/lifecycle boundary from D-001 amendment 3 §1, which already excludes
  status, progress, timestamps, reports, gate records, roster, worktree and `progress_log`;
* **every other** control-plane file contributes its canonical git blob id, exactly like ordinary
  work product: reports, directive sources, requirements, verification records, config.

The same boundary is applied to the dirt guard: a control-plane file in scope is dirty unless it
is a tracked, modified task packet whose working-tree material digest still equals its HEAD
material digest. Untracked, deleted, renamed/copied, unparseable and materially-changed files are
always dirt.

**What this buys and what it costs — stated plainly.**

* The guard is no longer vacuous. For a governance-shaped scope the identity is a real manifest
  (5 entries for M0-T027's `allowed_paths`), not the empty-set hash `e3b0c442…`.
* A committed change to any non-packet file in scope moves the identity. A **material** packet
  amendment moves it. A dirty or untracked file in scope now fails closed.
* **A lifecycle-only packet change still does not move the identity — by design.** So the
  literal AS-5 regression case (`f08769e1` → `16ae4589`, status/progress/updated_at only) still
  produces an unchanged identity. I judge AS-5 satisfied in substance (the guard is real and
  moves on real changes) and **not** satisfied in its most literal reading (that specific delta
  moving). I am flagging this rather than papering over it; the gate should decide whether my
  reading is the right one. If a reviewer insists on the literal reading, the honest answer is
  that it cannot be implemented without making every acceptance impossible, and the executable
  proof of that is in the suite.

**Uniform, not shape-conditional.** I did *not* branch on "is this task governance-shaped".
The control-plane material component is computed for every task; when no path in scope falls
inside the control-plane tree the entry list is empty and the identity is **byte-identical** to
the previous value (asserted in `S11 (d)` of `test_s11_reviewed_sha_compared_and_no_regression`
and in `test_ordinary_scopes_are_byte_identical_to_before`). A uniform rule is better for AS-3
than a shape test.

---

## 4. Per-scenario evidence

> **Round-1 transcripts, preserved.** The suite outputs in this section are the round-1 runs at
> base `05ee1917`. They are kept as the record of what was submitted to the two gates that
> returned FAIL. The **authoritative** post-rework runs are in **§9.10**, at the round-2 base
> `1298f4b`: 22 project-control groups (was 20) and 98 compliance tests (was 83), both exit 0.

### Command 1 — full project-control suite

```
$ cd <REPO>/.claude/worktrees/agent-a8497f73f558bac2a
$ python tools/test_project_control.py
OK: original 15-check workflow preserved
OK: S1 transition enum (legal chain passes; every prohibited jump rejected)
OK: S2 accept preconditions (status, gates, dependencies, blockers)
OK: S3 gate classes (independent/self_check/administrative; no bypass)
OK: S4 containment (task ids, report paths, gate ids, checkpoint ids)
OK: S5 atomic writes (concurrent invocations, interrupted write, serialization failure)
OK: S6 spoofing attempts all rejected
OK: S7 backward compatibility (364 real ledger files parse; legacy records accepted; validation is write-time only; zero-backlog composition survived via synthesized exemplar)
OK: S8 hardening follow-up (orchestrator roster prohibition, --gates enum, blocked-task roster precondition)
OK: S10 governance-orchestrator unblock semantics (4 conjunctive conditions, preserved defaults, fail-closed malformed data, gate() unchanged, source-level generality proofs)
    S10 [D-004-R413/R414]: 10/10 blocks executed, 118 assertion cases
    S10 per-block case counts: 1-non-governance-orchestrator-refused=32, 2-governance-orchestrator-unblocks=9, 3-governance-orchestrator-no-reviewers-refused=2, 4-orchestrator-only-roster-refused=3, 5-governance-no-independent-gate-refused=6, 6-malformed-fails-closed=31, 7-normal-producer-unchanged=12, 8-cancel-and-message-only-ungated=12, 9-gate-unchanged=8, 10-source-level-generality-proofs=3
OK: docs honesty (--agent disclaimed in --help and module docstring)
OK: S9 directive claim enforcement (refs required, selective citation refused, governance-path guard)
OK: S9 submit git-canonical identity (clean-required, dirty fails closed, stale on edit)
OK: S9 accept requires independent per-task verification at the git identity
OK: S9 regime-bypass closed + migration table (9 adversarial proofs)
OK: S11 lifecycle-aware acceptance + first-post-accept verification (AS-1, AS-4)
OK: S11 unmet NON-lifecycle rows still block acceptance (AS-2, 10 cases incl. positive control)
OK: S11 governance-shaped staleness identity + dirt guard (AS-5, AS-6)
OK: S11 reviewed_sha comparison + no-regression (AS-7, AS-8)
OK: S11 no special-casing; classification rule stated in code (AS-3, AS-12)
OK: all 20 project-control test groups passed
```

**Exit code 0.** (S10's 118 assertion cases and its exact per-block expectations are unchanged,
which is itself part of the no-regression evidence.)

### Command 2 — an earlier run that FAILED, and the real defect it caught

I am recording this because it is the most useful thing in the report for a reviewer. The first
run of the suite against my implementation failed:

```
$ python tools/test_project_control.py
... (S1..S10, docs honesty all OK) ...
AssertionError: claim with full refs must succeed: Cannot claim from status 'backlog':
  claim requires ['ready', 'rework'] (G0 readiness moves backlog to ready).
Exit code 1
```

Root cause: `git status --porcelain -- ` **with an empty pathspec list reports the whole
repository**. A task with empty `allowed_paths` was therefore being judged dirty against
control-plane records it does not own, and its `G0` gate silently failed. Fixed by making an
empty path list mean an empty scope in `control_plane_material_dirty` (documented in the
function's docstring). Reviewers should confirm this fix does not re-open the vacuity it was
meant to close — it does not, because a task with *no declared paths* has no scope to guard,
while the pre-existing whole-repo behavior of `relevant_working_tree_dirty` is untouched.

### Command 3 — full directive-compliance suite

```
$ python tools/test_directive_compliance.py
test_as12_rule_is_documented_in_the_code (AcceptanceOrderingClassifierTests) ... ok
test_classifier_is_general_no_allowlist_flag_or_env_override (AcceptanceOrderingClassifierTests) ... ok
test_condition2_attestation_must_be_independent_and_reasoned (AcceptanceOrderingClassifierTests) ... ok
test_condition3_row_binding_outside_acceptance_ordering_keeps_gating (AcceptanceOrderingClassifierTests) ... ok
test_condition4_only_obligation_and_sequencing_are_eligible (AcceptanceOrderingClassifierTests) ... ok
test_condition5_negative_verifier_finding_never_deferred (AcceptanceOrderingClassifierTests) ... ok
test_every_owner_enumerated_act_class_is_accepted_and_no_other (AcceptanceOrderingClassifierTests) ... ok
test_missing_requirement_row_fails_closed (AcceptanceOrderingClassifierTests) ... ok
test_no_claim_means_ordinary_gating_with_no_noise (AcceptanceOrderingClassifierTests) ... ok
test_well_formed_attestation_on_eligible_row_defers (AcceptanceOrderingClassifierTests) ... ok
test_deleted_packet_is_dirty (ControlPlaneMaterialIdentityTests) ... ok
test_dirty_control_plane_file_is_detected (ControlPlaneMaterialIdentityTests) ... ok
test_lifecycle_only_packet_change_does_not_move_the_identity (ControlPlaneMaterialIdentityTests) ... ok
test_lifecycle_only_uncommitted_packet_edit_is_not_dirty (ControlPlaneMaterialIdentityTests) ... ok
test_material_packet_amendment_moves_the_identity (ControlPlaneMaterialIdentityTests) ... ok
test_material_uncommitted_packet_edit_is_dirty (ControlPlaneMaterialIdentityTests) ... ok
test_new_identity_is_not_the_empty_set_hash (ControlPlaneMaterialIdentityTests) ... ok
test_non_packet_change_moves_the_identity (ControlPlaneMaterialIdentityTests) ... ok
test_old_guard_was_provably_vacuous (ControlPlaneMaterialIdentityTests) ... ok
test_ordinary_scopes_are_byte_identical_to_before (ControlPlaneMaterialIdentityTests) ... ok
test_raw_blob_control_plane_identity_would_be_unusable (ControlPlaneMaterialIdentityTests) ... ok
test_unparseable_packet_at_commit_fails_the_identity_closed (ControlPlaneMaterialIdentityTests) ... ok
test_unparseable_packet_is_dirty (ControlPlaneMaterialIdentityTests) ... ok
test_untracked_control_plane_file_is_detected (ControlPlaneMaterialIdentityTests) ... ok
test_backward_compatible_when_no_sha_supplied (ReviewedShaComparisonTests) ... ok
test_matching_reviewed_sha_passes (ReviewedShaComparisonTests) ... ok
test_missing_reviewed_sha_fails_closed (ReviewedShaComparisonTests) ... ok
test_stale_reviewed_sha_fails_closed (ReviewedShaComparisonTests) ... ok
  [... all 55 pre-existing tests also ran and passed: PositiveTests, ResolverTests,
   NegativeValidatorTests c1..c15, ContentManifestTests, GitContentIdentityTests
   R145..R153, MultiTaskVerificationTests R137..R142, MultipleDirectivesTest,
   RequirementsBodyDigestTest, ClaudeMdSectionTests, StdlibOnlyTests ...]

----------------------------------------------------------------------
Ran 83 tests in 147.766s

OK
```

**Exit code 0.** Baseline at `05ee1917` was 55 tests; this run is 83 (28 new), with every
pre-existing test still passing — including `test_real_registry_valid`,
`test_directive_registry_stdlib_only`, and the whole `GitContentIdentityTests` /
`MultiTaskVerificationTests` sets that guard the identity and verification semantics I changed.

### Scenario map

| AS | Where proven | Verdict I claim |
|---|---|---|
| AS-1 | `test_s11_lifecycle_aware_acceptance_and_post_accept_verification` — accept succeeds; `post_accept_verification.deferred_requirements` records both rows with `act_class`, `classified_by`, `justification`, `deferred_at_identity`, `deferred_at_sha`; the registry rows are asserted still `pending`, i.e. **not** rewritten to PASS | met |
| AS-2 | `test_s11_non_lifecycle_rows_still_block_acceptance` — **35 cases (round 2; was 10)**: plain unmet row; mixed lifecycle binding; prohibition; producer self-classification; no justification; act class outside the enumeration; **20 non-pending states probed OUTSIDE the old denylist** (`UNVERIFIABLE`, `fail`, `blocked`, `FAIL `, `Pending`, `pending `, `PASSED`, `""`, `wat`, `null`, `0`, `1`, `false`, `true`, `[]`, `["pending"]`, `{}`, `{...}`) plus an absent `state` key; 5 undated/invalid `classified_at` shapes; a re-spelled producer self-classification; missing row; **plus a positive control** proving the refusals were caused by the broken condition and not by a defect in the fixture. Each asserts the task stays `awaiting_gate`, gains **no** `post_accept_verification`, and that no case produced a traceback | met |
| AS-3 | `test_s11_no_special_casing_source_proofs` + `test_classifier_is_general_no_allowlist_flag_or_env_override` — AST-parsed function bodies (docstrings stripped, comments dropped) contain no ledger task id, no requirement id, and none of `getenv/environ/force/bypass/override/allowlist`; `project_control.py` never reads the environment; `accept -h` and `checkpoint -h` expose exactly their pre-existing options | met |
| AS-4 | same test as AS-1 — `checkpoint` is refused while either deferral is unverified (refusal names the row), refused again when only one is verified, succeeds when both are, and records `post_accept_verifications_confirmed` on the checkpoint. Also proves justified+approved `NOT_APPLICABLE` discharges a deferral while unjustified `NOT_APPLICABLE` does not. **Round 2 adds `test_s11_deferral_is_not_waiver_at_the_first_post_accept_opportunity` (9 CLI cases) + `DeferredDischargeStandardTests` (12 registry cases)**: the discharge is held to the SAME standard as the gate it deferred, and the obligation is re-derived from the registry so deleting the packet record does not erase it | met |
| AS-5 | `test_s11_governance_identity_and_dirt_guards` (f)(g) + `ControlPlaneMaterialIdentityTests` | **owner ruling C2 (binding)**: the literal clause is recorded NOT MET and PROVEN UNMEETABLE; the substituted material/lifecycle mechanism is ACCEPTED in substance. The 43-field exclusion list is explicitly **not** endorsed and is tightened under the C1 follow-up task, not here — see §3 and §9 |
| AS-6 | `test_s11_governance_identity_and_dirt_guards` (c)(d)(e) — dirty file in scope, material packet edit, and untracked file in scope all fail accept closed; registry-level tests add deleted and unparseable packets | met |
| AS-7 | `test_s11_reviewed_sha_compared_and_no_regression` (a)(b)(c) + `ReviewedShaComparisonTests` — a stale **and** an absent `reviewed_sha` both fail closed; the matching one accepts | met |
| AS-8 | **round 2:** both suites green — **22/22** project-control groups with S10's 118 assertion cases and per-block counts unchanged, **98/98** directive-compliance tests (round 1: 20/20 and 83/83; original baseline 55). Ordinary scopes byte-identical; accepted task stays terminal; plain checkpoint unaffected; lint findings unchanged from HEAD; the new registry re-derivation adds 0 blockers to the live ledger (§9.10 Commands D, E, F) | met |
| AS-9 | `git status --porcelain` (below) | met |
| AS-10 | **not mine.** Both modules are asserted to name none of the eight rows | deliberately not answered |
| AS-11 | §5 below | answered |
| AS-12 | rule stated in `directive_registry.py`; asserted present by test | met |
| AS-13 | orchestrator's to write from the verifier's return | not mine |
| AS-14 | §6 below | disclosed |

### AS-9 containment

```
$ git status --porcelain
 M tools/directive_registry.py
 M tools/project_control.py
 M tools/test_directive_compliance.py
 M tools/test_project_control.py

$ git diff --stat
 tools/directive_registry.py        | 604 +++++++++++++++++++++++++++++++++----
 tools/project_control.py           | 205 +++++++++++--
 tools/test_directive_compliance.py | 440 +++++++++++++++++++++++++++
 tools/test_project_control.py      | 576 ++++++++++++++++++++++++++++++++++-
 4 files changed, 1741 insertions(+), 84 deletions(-)
```

Four files, all in `allowed_paths`. `project-control/directives/**` unmodified. No `applicability`
edited. `tools/validate_directive_compliance.py` untouched.

---

## 5. AS-11 — would option (iii) alone have reached acceptance?

**Answer: NO.**

Derivation, from `project-control/directives/D-004-agent-teams-runtime-adoption/requirements.json`:

| Row | `applicability.task_ids` | Scoped solely to M0-T027? |
|---|---|---|
| `D-004-R388` | `["M0-T027"]` | yes |
| `D-004-R486` | `["M0-T027"]` | yes |
| `D-004-R487` | `["M0-T027"]` | yes |
| `D-004-R488` | `["M0-T027"]` | yes |
| `D-004-R501` | `["M0-T027"]` | yes |
| `D-004-R322` | `["M0-T027", "D-004-STEP4CLOSE"]` | **no** |
| `D-004-R323` | `["M0-T027", "D-004-STEP4CLOSE"]` | **no** |
| `D-004-R389` | `["M0-T033", "M0-T027"]` | **no** |

Option (iii) — re-scoping only the five rows scoped solely to `M0-T027` to the
`D-004-OPTIONB` sentinel — would leave `R322`, `R323` and `R389` still applicable to `M0-T027`
and still unmet. Removing `M0-T027` from those three would be an **in-place applicability edit**,
which `D-004-R627` prohibits ("Do NOT edit any requirement row's applicability in place — the
append-only invariant is not to be holed, for five rows or eight"). They therefore remain
applicable and unmet, and `accept()` still refuses on them. The owner's expectation ("I expect
not, given R322/R323/R389 remain") is confirmed.

I am recording the `task_ids` values as **data read from the registry**. I am not classifying any
of these rows as an acceptance-ordering lifecycle act or not — that is AS-10, the independent
verifier's call.

---

## 6. AS-14 — disclosed findings, NOT fixed, NOT worked around

These are surfaced, left exactly as they are, and handed to the gate.

**F1 — M0-T027's verification is 136 rows short of its applicable set.** Its
`task_verification` block holds **97** rows while **233** requirements are applicable, and its
declared `applicable_requirement_ids` (97) does not equal the derived set (233). `_v2_task_unresolved`
returns **99** reasons for M0-T027 before any identity or `reviewed_sha` check is reached. This
was established read-only before my work and I changed nothing about it. My changes cannot cure
it and do not try to.

**F2 — the tightened identity invalidates M0-T027's already-stamped evidence.** M0-T027's submit
record carries `content_manifest_sha256 = e3b0c442…` (the empty-set hash). Under the corrected
identity its `allowed_paths` produce a real 5-entry manifest, so the stamped value no longer
matches and `accept()` will report *"frozen-evidence identity mismatch … re-submit and re-verify
at the new content identity before acceptance."* **This is correct behavior** — the old value was
the artifact of the vacuous guard — but it means **M0-T027 must be re-submitted and re-verified
at the new identity before it can be accepted.** I have not touched M0-T027's packet, report
record, or verification. The orchestrator should plan for the re-submission; I am not authorized
to perform it and did not.

**F3 — the reviewed_sha comparison binds acceptance to the reviewed HEAD.** `accept()` now
compares the verification's `reviewed_sha` against the resolved commit (HEAD). Any commit landing
between verification and acceptance fails closed. This is exactly what Message F item 3 asks for
("the verifier must ALSO manually perform the guards accept() currently skips — reviewed_sha vs
head"), but it is a real operational tightening: the verification record must be refreshed at the
final head before the accept call.

**F4 — evidence must be committed before submit.** With the dirt guard now live over the
control-plane tree, an uncommitted or untracked file inside `allowed_paths` fails submit/gate/
accept closed. This applies to **this very task**: `project-control/reports/M0-T034-producer-report.md`
is in M0-T034's `allowed_paths`, so it must be committed before M0-T034 is submitted.

**F5 — identity values change for any task with control-plane paths in scope.** Tasks whose
`allowed_paths` mix code and control-plane files now get a different (larger) manifest. Tasks with
no control-plane paths are byte-identical to before (asserted). No accepted task is re-evaluated,
so no stored history is retro-rejected.

---

## 7. What I could NOT prove

**Sandbox interruption, disclosed for the record (now resolved).** For most of this session
`python tools/test_directive_compliance.py` was refused by the sandbox with:

```
claude-sonnet-5[1m] is temporarily unavailable, so auto mode cannot determine the safety of
Bash right now. Wait briefly and then try this action again.
```

Cause: `.claude/settings.local.json` allowlists `Bash(python tools/test_project_control.py*)` but
**not** `test_directive_compliance.py`, so that command required the command-safety classifier,
which was unavailable. I deliberately did **not** route around it — I did not rename the file,
did not invoke it through the allowlisted `test_project_control.py` entry point, and did not
otherwise exploit the trailing wildcard in the allowlist. The classifier recovered late in the
session and the suite ran green (Command 3 above), so **this is no longer an evidence gap**. It
is recorded because a reviewer re-running this work may hit the same allowlist gap, and because
the correct response to it is to wait or ask the orchestrator to capture the output — never to
work around the control.

**Honest limits that remain:**

* AS-5 is met in substance and not in its most literal reading (§3). I have stated my reasoning
  and the executable proof that the literal reading is unimplementable; I have not tried to make
  the wording fit.
* I have no way to prove the classifier is correct for row shapes that do not yet exist in the
  registry. Condition (3) is deliberately anchored to the *measured* vocabulary
  `{claim, progress, submit, gate, accept}`; if a future capture introduces a new
  lifecycle-event token, the classifier will refuse to defer rows carrying it until someone
  extends the constant through a reviewed change. That is intended, but it is a maintenance
  obligation a reviewer should be aware of.
* The `checkpoint()` guard makes `checkpoint` fail closed on an unreadable task packet. No
  current test exercises a corrupt packet followed by a checkpoint; I judged fail-closed correct
  but a reviewer may reasonably want that case covered.
* I did not run `tools/validate_directive_compliance.py` — it is a forbidden path for me and is
  meant to be an independent check on this change. (The compliance suite does exercise it
  indirectly via `PositiveTests.test_real_registry_valid` and the `NegativeValidatorTests`, all
  of which passed, but a standalone validator run against the real registry at the merged head is
  the reviewer's to perform.)
* I could not run the new code against the **real** M0-T027 scope to print its post-fix identity
  value, because computing it requires executing the resolver against the live repository and the
  only allowlisted `project_control.py` entry points are lifecycle subcommands the orchestrator
  owns. The claim in finding F2 (that M0-T027's stamped `e3b0c442…` will no longer match) follows
  from the same code path the tests prove, but its concrete value at the merged head is
  **unverified by me** and should be captured by the orchestrator before M0-T027 is re-submitted.

---

## 8. What I want reviewers to bear down on

*(Round-1 list, kept verbatim. Round 2 adds §10.)*

1. **Condition (4)'s allowlist.** Is `{obligation, sequencing}` right, or is `sequencing` already
   one notch too permissive because "stop BEFORE accept" and "stop AFTER accept" are structurally
   identical? I chose to include it and lean on the verifier's attestation; a reviewer may
   reasonably say the classifier should refuse `sequencing` entirely. Rider 1 says rejecting my
   design is the cheaper failure.
2. **Condition (3)'s `{"accept"}`.** Confirm the vocabulary measurement independently rather than
   trusting my grep.
3. **The staleness resolution in §3.** This is the judgment call the packet asked me to make and
   justify. Attack the impossibility proof if you think a literal AS-5 is implementable.
4. **The empty-pathspec fix.** `control_plane_material_dirty` returning `[], None` for an empty
   path list — is that a hole?
5. **AS-2's ten cases.** Try to construct a shape that reaches deferral without satisfying all
   five conditions.

---

## 9. ROUND 2 — rework after two independent FAIL gates

Both gates (G3 and G5) returned **FAIL** on the same axis. Nothing below argues with either
verdict; both were right, and the D1 finding in particular is the one I should have caught myself,
because I wrote four allowlist conditions and then made the fifth a denylist.

Owner ruling **C2** is treated as binding and is not re-litigated: the literal clause of AS-5 is
recorded NOT MET and PROVEN UNMEETABLE, the substituted material/lifecycle mechanism is accepted
in substance, and the 43-field exclusion list is explicitly **not** endorsed. Owner decision
**C1** (invert the boundary so unlisted fields default INTO the identity) is a **follow-up
controlled task queued after M0-T027 acceptance** — I did **not** implement it here, and §9.4
records the executable reason why doing so inside this task would have been actively harmful.

### 9.1 D1 (blocking) — condition (5) inverted from denylist to allowlist

| | Round 1 | Round 2 |
|---|---|---|
| Constant | `NEGATIVE_VERIFICATION_STATES = {"FAIL","BLOCKED"}` | `DEFERRABLE_VERIFICATION_STATES = {"pending"}` |
| Test | `if state in NEGATIVE_...:` refuse | `if not isinstance(state, str) or state not in DEFERRABLE_...:` refuse |
| Default | **release** (anything unlisted defers) | **refuse** (anything unlisted gates) |

`NEGATIVE_VERIFICATION_STATES` is **deleted**, not merely unused, and a test now asserts the
identifier appears nowhere in `tools/directive_registry.py` so the denylist cannot be
reintroduced. The stated rule at the top of the module was rewritten to match (AS-12: the
documented rule and the code must agree), naming `UNVERIFIABLE` explicitly as the value a denylist
released and stating that the `isinstance` guard is load-bearing rather than decorative.

Measured behaviour of the shipped classifier (positive control first):

```
'pending'                    -> deferred
'UNVERIFIABLE'               -> REFUSED  ... is not an explicitly pending row
'FAIL' / 'BLOCKED'           -> REFUSED
'fail' / 'blocked' / 'FAIL ' -> REFUSED
'Pending' / 'pending '       -> REFUSED
None / 0 / 1 / False / True  -> REFUSED
[] / ['pending'] / {} / ()   -> REFUSED   (no exception raised)
absent `state` key           -> REFUSED
```

`state: []` previously raised `TypeError: unhashable type: 'list'`. Two tests now pin this:
`test_classifier_never_raises_on_any_malformed_state` (registry level, 7 unhashable/mistyped
shapes) and the CLI-level probe in AS-2, which asserts `"Traceback" not in stderr` for every case.

**The suite no longer certifies the hole.** `test_s11_non_lifecycle_rows_still_block_acceptance`
went from **10 cases to 35**, and its condition-(5) block now probes **outside** the old denylist
by construction: `UNVERIFIABLE`, absent, `null`, `[]`, `{}`, case variants, whitespace-padded
variants, numeric and boolean states. `test_condition5_only_an_explicitly_pending_state_is_
deferrable` replaces the round-1 test that iterated the denylist itself — a test which, as G3 put
it, could only ever confirm the values its subject already knew about.

### 9.2 F2 (blocking) — "deferral is not waiver" is now true in code

The discharge path no longer trusts a bare state. `DirectiveRegistry.deferred_requirement_
discharge()` applies the **same** standards as the gate that deferred the row:

* **independence** — a non-empty producer **and** a non-empty verifier that is not the producer
  (case/whitespace-insensitive), the identical test `_v2_task_unresolved` applies at acceptance;
* **content identity** — the record's `reviewed_manifest_sha256` must equal the identity the
  deferral was granted at (`deferred_at_identity`, stamped by `accept()`);
* **reviewed commit** — the record's `reviewed_sha` must equal `deferred_at_sha`;
* **row state** — `PASS`, or `NOT_APPLICABLE` with justification **and** independent approver.

A deferral record lacking `deferred_at_identity`/`deferred_at_sha` fails closed rather than
discharging unbound. `requirement_verification_state()` is retained as a plain accessor, but its
docstring now says in terms that it is **not** sufficient for discharge, and a test asserts the
exact row that reads `PASS` through it does **not** discharge.

Nine CLI-level cases prove it end to end
(`test_s11_deferral_is_not_waiver_at_the_first_post_accept_opportunity`): bare PASS with no
verifier; producer self-discharge spelled `" ORCHESTRATOR "`; wrong content identity; wrong
reviewed commit; deleted row; **proper discharge (positive control)**; packet-record deletion;
re-derived-then-satisfied; and an `UNVERIFIABLE` post-accept verdict. Twelve more at the registry
level in `DeferredDischargeStandardTests`.

**Limit I am not hiding:** an actor who can write `verification.json` can also copy the expected
identity and sha into it, since both are public values on the task packet. That is equally true of
the acceptance gate itself — the protection is verifier-independence plus the fact that the
identity is a git-derived constant, not a secret. F2 asked that the discharge be held to the *same*
standard as the gate; it now is. It is not held to a *higher* one.

### 9.3 F3 (blocking) — an empty producer no longer makes independence inert

`elif producer and by == producer:` silently disabled itself whenever `producer` resolved empty
through the `tv.producer → v.producer → requirements.producer` chain — and the same emptiness
already disabled the **pre-existing** verifier-independence checks in `_v2_task_unresolved` and
`_v1_task_unresolved`. A missing/empty producer is now an **explicit fail-closed reason** in both
functions and in the classifier's condition (2), on the principle that independence which cannot
be **evaluated** has not been **established**. `test_s11_missing_producer_identity_fails_closed`
blanks the producer in all three places it can be read and proves accept refuses, with a positive
control restoring it. All producer/verifier comparisons are now case- and whitespace-insensitive
(**F6**, done rather than deferred: two lines, and it removes an entire class of trivially
re-spelled self-review).

### 9.4 F4 — re-derivation done; the `MATERIAL_FIELDS` half deliberately NOT done

**Done.** The outstanding set is now read from **two** independent places and unioned:
`_post_accept_verification_blockers()` reads the packet's deferral records **and** re-derives
outstanding obligations from the registry (`outstanding_lifecycle_claims()`), for every
**accepted, in-regime** task. Deleting `post_accept_verification` from a packet now removes the
record, not the obligation — proven in case (g) of the new CLI test, which deletes the key
outright and still gets a refusal naming the row and the phrase *"re-derived from the registry"*.

**Not done, with an executable reason.** F4 also observes the key is not in `MATERIAL_FIELDS`.
Adding it there would break stored history:

```
$ python - <<'PY'   # measured against the live ledger
current  MATERIAL_FIELDS digest (M0-T023): a0adb736ebee1299
widened  MATERIAL_FIELDS digest (M0-T023): 203cbcfcd296e114
grandfathered tasks whose digest WOULD change if the key were added: 57 / 57
post_accept_verification present on any task today: False
PY
```

`material_digest()` builds `{k: task.get(k) for k in MATERIAL_FIELDS}`, so **adding any field adds
a `"…":null` entry to every task's canonical JSON**, changing the material digest of all **57**
tasks in the frozen migration manifest and invalidating grandfathering for every legacy task. That
is a retro-rejection of stored history, which AS-8 forbids. `MATERIAL_FIELDS` also drives D-001
grandfathering, which is precisely why owner decision **C1 split that work into a follow-up task**.
I judged re-derivation the substantive fix for the harm F4 names ("deleting it erases the
obligation silently") and left the digest question to C1's follow-up. **I did not mirror the key
in `sync_state()` either** — a mirror is a third copy of the same mutable assertion, whereas the
registry re-derivation is an independent source of truth. If the gate disagrees, the mirror is
cheap to add.

**New coupling this introduces, disclosed:** `checkpoint` now loads the directive registry whenever
any accepted in-regime task exists, and fails closed if it cannot. Measured against the live
ledger: registry loads in **47 ms** with **0** errors, there are **11** accepted in-regime tasks
spanning 12 (task, directive) pairs, and every pair re-derives to `[]` — so this change adds
**zero** blockers today. The residual risk is that a future registry integrity error would block
checkpoints; I chose fail-closed consistently with the rest of the module (and the validator runs
in CI, so such an error surfaces there first), but this is a real availability trade and a
reviewer may legitimately want it downgraded.

### 9.5 F5 — attestation validation done; identity-binding done indirectly

`classified_at` was copied unvalidated. It is now required to be an ISO-8601 **date-and-time**
that is both well-shaped and **calendar-valid** (`2026-13-99T99:99:99+00:00` and `2026-02-30T…`
both refuse; a bare date refuses; `"t"` refuses). The attestation is bound to an identity
**indirectly but checkably**: `accept()` stamps `deferred_at_identity`/`deferred_at_sha` on the
deferral, and §9.2's discharge re-checks the record against both. What I did **not** do is add a
`classified_at_sha`-style field to the attestation itself — that would invent registry schema I am
forbidden to define (see §9.7), so an attestation is still transportable between records of the
same task at the same identity. Stated rather than papered over.

### 9.6 F6 — done (see §9.3)

### 9.7 F8 — NOT done, out of allowed_paths, justified

F8 asks that `lifecycle_classification` be defined in the v1 verification schema and that
conditions (1)/(2)/(4)/(5) be mirrored in the validator. Both targets are **forbidden paths** for
this task:

* the schema lives at `project-control/directives/schema/v1/directive_verification.schema.json`,
  inside `project-control/directives/**` — forbidden, and the packet reserves registry writes to
  the orchestrator's D-001 capture authority;
* `tools/validate_directive_compliance.py` is forbidden **by design**, so the validator stays an
  independent check on the code being changed.

I therefore cannot address F8 without breaching containment, and I did not. What I can say about
the risk: the key is admitted today only by `additionalProperties: true`, so CI does not validate
its shape — but the **classifier** validates every field of it and fails closed on each malformed
shape, so an invalid attestation cannot produce a deferral; it can only produce a refusal. The
schema/validator work is a genuine second line of defence and should be its own task, most
naturally folded into the C1 follow-up which already touches this area.

### 9.8 The two static-analysis items

Not touched, per the gate's instruction: `directive_registry.py:683` (analyzer matched the
pre-change 5-arg signature) and the `project_control.py:258-264` Optional cluster (untouched
M0-T014 code) were both ruled FALSE POSITIVES by G3. I re-confirmed the first by inspection —
`_v1_task_unresolved` is defined with `(self, d, v, directive_id, applicable,
reviewed_manifest_sha256, reviewed_sha=None)` and called with exactly that shape — and changed
neither.

### 9.9 D2 — the absolute path in a public repo

`project-control/reports/M0-T034-producer-report.md` line 198 carried a `cd` transcript with the
OS username and full home-directory layout, while line 21 of the same file was already correctly
elided. I amended line 198 myself (producer evidence stays producer-amended) to:

```
$ cd <REPO>/.claude/worktrees/agent-a8497f73f558bac2a
```

and re-swept the whole file and `tools/` for `MLFLL`, `/c/Users`, `C:\Users` and
`Downloads/nyc-zoning` — **no matches remain**. The round-2 transcripts in this section are
`<REPO>`-relative by construction.

### 9.10 Round-2 command evidence (authoritative; base `1298f4b`)

**Command A — full project-control suite.** Exit code **0**, 22 groups (was 20).

*Evidence-integrity note, disclosed rather than quietly dropped:* an earlier pass of this suite
overlapped a one-line edit I made to `tools/project_control.py`, so that pass exercised a mixture
of two file states and is **not** cited here. The transcript below is a clean re-run with no
concurrent edits, and the four files were SHA-256'd immediately before and after it to prove the
bytes did not move:

```
$ python -c "<sha256 of the four changed tools files>"     # before AND after, identical
9bd9fd018e1aa978 tools/directive_registry.py
3a3bd8358e93df56 tools/project_control.py
d0ca7740ec4f334f tools/test_project_control.py
224d9867b76053ca tools/test_directive_compliance.py
```

```
$ cd <REPO>/.claude/worktrees/agent-aa6a2a030ff145fe0
$ python tools/test_project_control.py
OK: original 15-check workflow preserved
OK: S1 transition enum (legal chain passes; every prohibited jump rejected)
OK: S2 accept preconditions (status, gates, dependencies, blockers)
OK: S3 gate classes (independent/self_check/administrative; no bypass)
OK: S4 containment (task ids, report paths, gate ids, checkpoint ids)
OK: S5 atomic writes (concurrent invocations, interrupted write, serialization failure)
OK: S6 spoofing attempts all rejected
OK: S7 backward compatibility (364 real ledger files parse; legacy records accepted; validation is write-time only; zero-backlog composition survived via synthesized exemplar)
OK: S8 hardening follow-up (orchestrator roster prohibition, --gates enum, blocked-task roster precondition)
OK: S10 governance-orchestrator unblock semantics (4 conjunctive conditions, preserved defaults, fail-closed malformed data, gate() unchanged, source-level generality proofs)
    S10 [D-004-R413/R414]: 10/10 blocks executed, 118 assertion cases
    S10 per-block case counts: 1-non-governance-orchestrator-refused=32, 2-governance-orchestrator-unblocks=9, 3-governance-orchestrator-no-reviewers-refused=2, 4-orchestrator-only-roster-refused=3, 5-governance-no-independent-gate-refused=6, 6-malformed-fails-closed=31, 7-normal-producer-unchanged=12, 8-cancel-and-message-only-ungated=12, 9-gate-unchanged=8, 10-source-level-generality-proofs=3
OK: docs honesty (--agent disclaimed in --help and module docstring)
OK: S9 directive claim enforcement (refs required, selective citation refused, governance-path guard)
OK: S9 submit git-canonical identity (clean-required, dirty fails closed, stale on edit)
OK: S9 accept requires independent per-task verification at the git identity
OK: S9 regime-bypass closed + migration table (9 adversarial proofs)
OK: S11 lifecycle-aware acceptance + first-post-accept verification (AS-1, AS-4)
OK: S11 unmet NON-lifecycle rows still block acceptance (AS-2, 35 cases incl. positive control)
OK: S11 governance-shaped staleness identity + dirt guard (AS-5, AS-6)
OK: S11 reviewed_sha comparison + no-regression (AS-7, AS-8)
OK: S11 deferral is not waiver -- post-accept discharge held to the gate's own standard (9 cases incl. positive control)
OK: S11 an unknown producer identity fails closed (independence is never inert)
OK: S11 no special-casing; classification rule stated in code (AS-3, AS-12)
OK: all 22 project-control test groups passed
PC_CLEAN_EXIT=0
```

S10's 118 assertion cases and its exact per-block counts are **unchanged**, which is part of the
no-regression evidence: nothing in this rework moved the M0-T033 unblock semantics.

**Command B — full directive-compliance suite.** Exit code **0**, 98 tests (was 83).

```
$ python tools/test_directive_compliance.py
[... 98 tests, all "... ok" ...]
----------------------------------------------------------------------
Ran 98 tests in 127.272s

OK
DC_FINAL_EXIT=0
```

The +15 delta is measured, not asserted:

```
$ python -c "<AST count of test_* methods per class, HEAD vs working tree>"
HEAD total 83 | WORKING total 98 | delta 15
   AcceptanceOrderingClassifierTests 10 -> 13
   DeferredDischargeStandardTests 0 -> 12
```

**Command C — AS-9 containment, re-proven for round 2.**

```
$ git status --porcelain
 M project-control/reports/M0-T034-producer-report.md
 M tools/directive_registry.py
 M tools/project_control.py
 M tools/test_directive_compliance.py
 M tools/test_project_control.py

$ git diff --stat
 project-control/reports/M0-T034-producer-report.md | 261 +++++++++++++++++-
 tools/directive_registry.py                        | 296 +++++++++++++++++----
 tools/project_control.py                           |  92 +++++--
 tools/test_directive_compliance.py                 | 243 ++++++++++++++++-
 tools/test_project_control.py                      | 245 ++++++++++++++++-
 5 files changed, 1044 insertions(+), 93 deletions(-)

$ git diff --name-only -- project-control/directives/ | wc -l
0
```

Five files, every one inside `allowed_paths`. `project-control/directives/**` unmodified (0 files).
No requirement row's `applicability` edited. `tools/validate_directive_compliance.py` untouched.
`project-control/tasks/M0-T034.json` untouched by me (orchestrator lifecycle path).

**Command D — live-ledger probe for the new registry coupling (§9.4).**

```
$ python -c "<load registry; list accepted in-regime tasks; re-derive claims>"
load_registry ms=47.4
registry errors: []
  D-001 active errors=[] nreq=136      D-002 active errors=[] nreq=69
  D-003 active errors=[] nreq=28       D-004 active errors=[] nreq=649
  D-005 active errors=[] nreq=110
accepted in-regime tasks: 11
M0-T023 D-001 -> []      M0-T024 D-002 -> []      M0-T028 D-004 -> []
M0-T030 D-005 -> []      M0-T031 D-005 -> []      M0-T033 D-001 -> []
M0-T033 D-004 -> []      M2-T017 D-002 -> []      M2-T018 D-004 -> []
M3-T001 D-002 -> []      M4-T007 D-002 -> []      M4-T008 D-004 -> []
```

Twelve (task, directive) pairs, all re-deriving to `[]`: the new re-derivation adds **zero**
blockers to the live ledger today.

**Command E — the new guard, run read-only against the live ledger.** This calls the guard
function itself rather than the CLI (`checkpoint` is an orchestrator-only write path I must not
invoke), so it is the closest first-hand proof I am permitted to produce that the coupling in
§9.4 does not block the real control plane:

```
$ python -c "import project_control as pc; print(pc._post_accept_verification_blockers())"
read-only call against the LIVE ledger: 97 ms
blockers: 0
```

**Command F — lint parity.** My changes add **zero** new findings to the four files:

```
$ python -m ruff check --statistics <the four files, HEAD>     $ ... <the four files, working>
11 E702   3 F841   2 E741   1 E401   1 E402                    11 E702   3 F841   2 E741   1 E401   1 E402
```

---

## 10. Round 2 — what I could NOT prove, and where to bear down

**Could not prove:**

1. **F8 is unaddressed and I cannot address it.** The schema and the validator are both forbidden
   paths (§9.7). A reviewer must decide whether M0-T034 can merge with `lifecycle_classification`
   still admitted only by `additionalProperties: true`. My position: the classifier validates every
   field and fails closed on each, so an invalid attestation yields a refusal and never a deferral
   — but that is one layer, not two, and CI does not check the shape.
2. **F5 is only partly closed.** `classified_at` is now validated and calendar-checked, and the
   deferral is bound to an identity and commit that the discharge re-verifies — but the
   attestation object itself still carries no identity of its own, so it remains transportable
   between records of the same task at the same identity. Closing that needs a schema field I am
   forbidden to define.
3. **The F2 discharge is held to the same standard as the gate, not a higher one.** Anyone who can
   write `verification.json` can copy the expected identity and sha from the packet. That is the
   gate's own threat model; I did not invent a stronger one inside this task.
4. **I still have not run `tools/validate_directive_compliance.py`** (forbidden path, and it is
   meant to be an independent check on this code). `PositiveTests.test_real_registry_valid` and
   the `NegativeValidatorTests` exercise it indirectly and pass, but a standalone run at the merged
   head is the reviewer's.
5. **I did not re-measure M0-T027's post-fix identity value** against the live repository — the
   round-1 limitation is unchanged. Finding F2 in §6 (that its stamped `e3b0c442…` will no longer
   match) still follows from the proven code path but its concrete value is unverified by me.
6. **No test covers a corrupt task packet followed by a checkpoint.** Round 1 flagged this; it is
   still true, and the new re-derivation makes `checkpoint` read more state than before, so the
   gap is slightly wider than it was.

**Where a fresh G3/G5 should bear down hardest:**

1. **Condition (5)'s allowlist — is `{"pending"}` too narrow?** I chose strict equality: no
   `strip()`, no `casefold()`, so `"pending "` and `"Pending"` refuse. That is fail-closed, but it
   means a verifier who writes a whitespace-padded state gets a confusing refusal rather than a
   deferral. I judged a confusing refusal strictly better than a permissive parse; disagree if you
   think it will be mistaken for a bug in the field.
2. **The new `checkpoint` → registry coupling (§9.4).** This is the round-2 change most likely to
   have an unintended consequence: a command that previously needed no registry now fails closed
   without one. I proved it adds zero blockers today, not that it will never block.
3. **Whether re-derivation is the right substitute for `MATERIAL_FIELDS`.** I produced executable
   evidence that the digest change would retro-reject 57 grandfathered tasks, but a reviewer may
   still want the key mirrored somewhere, or want F4 held open until the C1 follow-up lands.
4. **Condition (4) still admits `sequencing`** — round 1's self-flagged weakest choice, unchanged
   and unresolved by this rework. Both gates passed rider 1 from code, but the "stop BEFORE
   accept" / "stop AFTER accept" ambiguity is still discriminated only by the verifier's
   attestation.
5. **The 43-field exclusion list is still in place.** Owner ruling C2 explicitly does **not**
   endorse it; C1 orders it tightened under a separate follow-up. Nothing in this rework touched
   it, by design. Confirm that is the intended sequencing rather than an omission.
6. **Try to construct a shape that reaches deferral without satisfying all five conditions.** AS-2
   now runs 35 cases; the interesting attack surface is the interaction between conditions, not
   any single one.
