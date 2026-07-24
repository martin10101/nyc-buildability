<!--
CAPTURE METADATA (not part of the owner's words; the verbatim amendment follows the marker below)
  directive_id:      D-001
  source_file:       source-003-amendment.md
  kind:              amendment
  amends:            source-001.md
  sequence:          3
  captured_at:       2026-07-23
  captured_by:       orchestrator (lead session)
  channel:           owner_message (PR #97 review — final bounded hardening)
  integrity:         SHA-256 of this file is recorded in manifest.json -> sources[].content_digest_sha256
  effect:            Corrects the implementation of D-001/M0-T023 in PR #97 in place. Adds new atomic
                     requirements D-001-R119.. for: (1) closing the directive-regime bypass with an
                     immutable migration manifest + fail-closed regime entry + material-digest
                     grandfather invalidation; (2) a versioned multi-task verification schema
                     (directive_verification/v2); (3) a cross-platform, Git-canonical content-manifest
                     identity; (4) reconciled reviewed identity + PR metadata. Append-only: source-001.md
                     and source-002-amendment.md are NOT edited, and no existing requirement is renumbered.
                     Does NOT authorize merge/accept/deploy/purchase/product work/PR closure/hold release.
-->

# D-001 — Amendment 003 (final bounded hardening of PR #97)

<!-- BEGIN VERBATIM OWNER TEXT -->
OWNER DIRECTIVE — FINAL BOUNDED HARDENING OF PR #97

Amend PR #97 in place. Do not create another PR. Do not merge or accept M0-T023. Do not begin product implementation yet.

First invoke `/directive-compliance`. Because this corrects the implementation of D-001/M0-T023, append this message verbatim as the next D-001 amendment source. Do not rewrite any prior source file or renumber any existing requirement. Add new atomic requirement IDs for every item below.

At the start, independently reconcile and report:

* current `origin/main`
* current PR #97 head
* reviewed-content SHA and manifest identity
* commits and files added after the reviewed-content SHA
* current remote CI state

Do not trust the existing PR description as current state. GitHub currently reports head `33fbb44`, while the PR description says final head `6e41fd8`; reconcile that discrepancy.

1. Close the directive-regime bypass

The current code permits a new task without `--directive-refs` to be treated as pre-regime/grandfathered. That defeats the purpose of the system.

Implement these rules mechanically:

* Create an immutable migration manifest bound to baseline `1acb9b5`, containing the exact pre-regime task IDs and a digest of each packet’s material fields.
* The legacy list must not silently grow. Adding an ID requires an owner-issued directive amendment.
* When the directive regime is enabled, every newly created task must carry valid active `directive_refs`. `new-task` without them must fail closed.
* A task ID not present in the frozen migration manifest must never become grandfathered merely because its packet omitted the regime stamp.
* A previously unstarted legacy task must enter the regime when it is claimed or reclaimed.
* An already active legacy task (`claimed`, `in_progress`, `self_check`, or `awaiting_gate`) may finish its existing lifecycle without deadlock.
* Accepted/canceled tasks remain immutable.
* A material amendment or replan of a legacy task invalidates grandfathering. Compare a deterministic digest of material packet fields such as objective, inputs, outputs, dependencies, paths, scenarios, gates, risks, and blockers. Exclude ordinary lifecycle bookkeeping such as status, progress, timestamps, reports, and gate records.
* A blocked/rework/backlog/ready legacy task must provide valid directive references at its next claim.
* Do not use `created_at` alone to decide migration status.
* If the registry is missing, corrupt, inactive, or unresolved, new-task and required regime entry must fail closed.
* Do not add a general bypass, suppression flag, or agent-selected exemption.

Add adversarial tests proving:

* a new product task without directive references is rejected
* omitting the regime stamp cannot manufacture grandfathered status
* a new task with valid references succeeds
* already-active legacy tasks can finish
* a legacy task’s material amendment requires regime entry
* lifecycle-only changes do not falsely count as material amendments
* a backlog/blocked/rework task must enter the regime when claimed again
* accepted tasks remain immutable
* malformed or unavailable registry state fails closed

The reminder hook remains advisory and exit-0. Describe it accurately as “fail-visible,” not “fail-closed.” Mechanical fail-closed enforcement belongs to the CLI, validator, blockers, and gates.

2. Support one directive governing multiple tasks

Replace the single-directive/single-content-identity assumption.

Implement a versioned verification schema that supports task-specific verification records. A suitable shape is `directive_verification/v2` with `task_verifications[]`, where every entry contains at least:

* directive ID
* task ID
* exact applicable requirement IDs for that task
* reviewed SHA
* task-specific content-manifest identity
* producer
* independent verifier
* per-requirement states and evidence
* verification timestamp/schema version

Required behavior:

* Acceptance must call verification with `directive_id`, `task_id`, the task’s derived applicable requirement IDs, and its current content identity.
* Only requirements applicable to that task are evaluated for that task’s acceptance.
* `ALL` means all requirements applicable to the current task—not every requirement belonging to the directive.
* Two tasks governed by the same directive may have different allowed paths, content identities, evidence, and reviewers.
* Stale verification for task A must block task A without incorrectly invalidating task B.
* A shared requirement applicable to both tasks must be independently represented for both task verifications.
* Producer/verifier separation must be checked per task.
* Missing, duplicate, extra, stale, or cross-task verification rows must fail closed.
* Migrate D-001’s existing single-task verification into the new representation without losing its evidence history.

Add positive and adversarial fixtures with at least two tasks, different allowed paths, different applicable requirement sets, and different content identities.

3. Make content identities cross-platform and Git-canonical

Do not hash raw working-tree bytes as the authoritative reviewed identity.

Derive the manifest from canonical tracked Git content at the frozen/reviewed commit:

* sorted repository-relative path
* Git blob/object identity
* file mode, including executable/symlink/submodule distinctions where applicable
* deterministic directory expansion

Required behavior:

* LF versus CRLF checkout differences cannot change the identity when canonical Git content is identical.
* Binary content remains byte-exact.
* Relevant untracked or dirty files fail closed rather than being silently omitted.
* Identical relevant blobs remain stable across merge, rebase, and squash.
* A relevant content or file-mode change invalidates verification.
* Submission, independent gates, and acceptance must use the same shared implementation.
* Require and validate the reviewed commit SHA where needed.

Add tests for LF/CRLF equivalence, binary changes, mode changes, dirty/untracked relevant files, unrelated-file changes, merge/rebase-equivalent blobs, and an actual relevant-content mutation.

4. Reconcile the reviewed identity and PR metadata

After implementing the above:

* Freeze a new review identity.
* Rerun independent G3, directive-compliance G4, control-plane G4, and G5.
* Regenerate the complete per-requirement matrix.
* Run the full local and remote CI suite, including web-e2e, API, contracts, locks, control-plane, context-budget, and secret-scan.
* Update the PR description to distinguish clearly among frozen base, reviewed code SHA, reviewed content-manifest identity, evidence-only commits, and current PR head.
* Do not call an older commit the “final head.”
* Any later change to code, schemas, tests, requirements, or content-manifest paths invalidates the review and requires re-review.
* Evidence-only/ledger-only commits must be explicitly enumerated and independently checked as such.

Keep this amendment tightly bounded to these defects. Do not conduct another whole-system replan, change product code, select dependencies, deploy, purchase anything, close another PR, lift a hold, merge, or accept M0-T023.

Return:

1. old and new heads
2. exact changed files
3. D-001 amendment and new requirement IDs
4. regime-entry behavior table for every lifecycle state
5. multi-task verification schema and two-task test evidence
6. cross-platform manifest algorithm and adversarial results
7. local versus remote checks
8. independent review results and identity
9. corrected PR-description identity fields
10. unresolved limitations
11. explicit confirmation that nothing was merged, accepted, deployed, purchased, product-dispatched, or closed

Stop at the updated PR for owner review.
<!-- END VERBATIM OWNER TEXT -->
