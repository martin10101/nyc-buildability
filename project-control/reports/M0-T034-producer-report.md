# M0-T034 — producer report

**Task:** Governance acceptance semantics: lifecycle-aware `accept()` + real guards for
governance-shaped tasks
**Producer:** `backend-engineer` (this report is producer evidence, not a gate verdict)
**Base commit:** `05ee1917291659d18f88718a6b73e51cf619d4ff`
**Directive:** D-004, Message F item 2 (rows `D-004-R627..R633`)

> A worker agent cannot mark its own task complete. Everything below is evidence submitted
> for an independent gate. Where I could not prove something, it says so in plain words.

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

---

## 1. What changed and why

| File | Change |
|---|---|
| `tools/directive_registry.py` | The stated acceptance-ordering classification rule + `acceptance_ordering_deferral()`; `task_verification_result()` returning `(reasons, deferrals)`; `requirement_verification_state()`; **actual `reviewed_sha` comparison** in both the v2 and v1 verification paths; the **control-plane material identity** (`control_plane_entries`, `control_plane_material_dirty`, `_hash_manifest_entries`, `_ls_tree_entries`, `_status_records`); `frozen_git_identity(..., control_plane_prefixes=)`. |
| `tools/project_control.py` | `_task_git_identity` now passes the control-plane prefixes, so submit/gate/accept share one identity; `_directive_accept_reasons` returns `(reasons, deferrals)` and passes the resolved commit for the `reviewed_sha` check; `accept()` records deferrals on the packet under `post_accept_verification`; `checkpoint()` is the **first post-accept opportunity** and refuses while any deferral is unverified; module docstring gained `LIFECYCLE-AWARE ACCEPTANCE` and `CONTROL-PLANE CONTENT IDENTITY` sections. |
| `tools/test_project_control.py` | New group **S11** (5 test functions) proving AS-1..AS-8 and AS-12 end-to-end through the CLI; `make_directive` extended to author rows with explicit `classification` / `lifecycle_events`. |
| `tools/test_directive_compliance.py` | New verification-layer tests: the classifier's five conditions each proven necessary, the source-level generality proofs, the `reviewed_sha` comparison, and the control-plane material identity / dirt guard. |

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
2. **INDEPENDENT ATTESTATION.** That object records a non-empty `classified_by` that is **not**
   the producer of the verification record, plus a non-empty `justification`. Per `D-004-R632`
   the sufficient judgment is the independent verifier's; this module supplies **necessary**
   conditions only and deliberately refuses to supply the sufficient one.
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
5. **NO NEGATIVE FINDING.** The verification row's `state` is neither `FAIL` nor `BLOCKED`. A row
   the verifier actively failed or found blocked keeps gating however it is classified.

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

**Deferral is not waiver.** A deferred row is never deleted, waived, rewritten to `PASS`, or
silently passed. `accept()` records it on the task packet under `post_accept_verification`, and
`checkpoint()` — the first post-accept opportunity the control plane offers — refuses to record
while any registered deferral is still unverified.

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

### Command 1 — full project-control suite

```
$ cd /c/Users/MLFLL/Downloads/nyc-zoning/nyc-development-feasibility-claude-pack/.claude/worktrees/agent-a8497f73f558bac2a
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
| AS-2 | `test_s11_non_lifecycle_rows_still_block_acceptance` — **10 cases**: plain unmet row; mixed lifecycle binding; prohibition; producer self-classification; no justification; act class outside the enumeration; `FAIL`; `BLOCKED`; missing row; **plus a positive control** proving the nine refusals were caused by the broken condition and not by a defect in the fixture. Each asserts the task stays `awaiting_gate` and gains **no** `post_accept_verification` | met |
| AS-3 | `test_s11_no_special_casing_source_proofs` + `test_classifier_is_general_no_allowlist_flag_or_env_override` — AST-parsed function bodies (docstrings stripped, comments dropped) contain no ledger task id, no requirement id, and none of `getenv/environ/force/bypass/override/allowlist`; `project_control.py` never reads the environment; `accept -h` and `checkpoint -h` expose exactly their pre-existing options | met |
| AS-4 | same test as AS-1 — `checkpoint` is refused while either deferral is unverified (refusal names the row), refused again when only one is verified, succeeds when both are, and records `post_accept_verifications_confirmed` on the checkpoint. Also proves justified+approved `NOT_APPLICABLE` discharges a deferral while unjustified `NOT_APPLICABLE` does not | met |
| AS-5 | `test_s11_governance_identity_and_dirt_guards` (f)(g) + `ControlPlaneMaterialIdentityTests` | **met in substance, not in the literal reading** — see §3 |
| AS-6 | `test_s11_governance_identity_and_dirt_guards` (c)(d)(e) — dirty file in scope, material packet edit, and untracked file in scope all fail accept closed; registry-level tests add deleted and unparseable packets | met |
| AS-7 | `test_s11_reviewed_sha_compared_and_no_regression` (a)(b)(c) + `ReviewedShaComparisonTests` — a stale **and** an absent `reviewed_sha` both fail closed; the matching one accepts | met |
| AS-8 | both suites green (20/20 project-control groups with S10's 118 cases unchanged; 83/83 directive-compliance tests, up from the 55-test baseline); ordinary scopes byte-identical; accepted task stays terminal; plain checkpoint unaffected | met |
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
