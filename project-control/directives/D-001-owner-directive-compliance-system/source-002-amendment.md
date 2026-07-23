<!--
CAPTURE METADATA (not part of the owner's words; the verbatim amendment follows the marker below)
  directive_id:      D-001
  source_file:       source-002-amendment.md
  kind:              amendment
  amends:            source-001.md
  sequence:          2
  captured_at:       2026-07-23
  captured_by:       orchestrator (lead session)
  channel:           owner_message (answer to the lead's R-000 sequencing question)
  integrity:         SHA-256 of this file is recorded in manifest.json -> sources[].content_digest_sha256
  effect:            Approves Option 1 (build full M0-T023 PR, stop before merge) AND adds 8 mandatory
                     design corrections (see requirements D-001-R101..R-118). Append-only: never edit
                     source-001.md; this file records the correction. Does NOT authorize merge/accept.
-->

# D-001 — Amendment 002 (owner approval + 8 mandatory corrections)

<!-- BEGIN VERBATIM OWNER TEXT -->
Approve Option 1: Build the full M0-T023 PR and stop before merge.

This authorizes implementation of exactly one dedicated governance/control task, M0-T023, from frozen base `1acb9b5`, with D-001 as its governing owner directive. It authorizes creating the task/branch, implementing the complete closed loop, running its harnesses and independent G0–G5 reviews, and opening one PR.

It does not authorize merging, accepting M0-T023, creating a checkpoint, deploying, purchasing, installing dependencies, closing/superseding any existing PR, modifying PRs #64/#91/#93/#94/#95, releasing holds, or beginning product work. Stop with the PR open for owner review.

Before implementation, incorporate these mandatory corrections into the packet and design:

1. Preserve one acceptance authority, but do not make enforcement blind to the registry. `project_control.py` remains the only task/gate/acceptance authority. However, its claim/submit/accept checks must use a shared stdlib-only, read-only directive resolver to verify that every cited directive/requirement exists, is active, has valid hashes, and applies to the task. A syntactically valid but nonexistent, withdrawn, superseded, malformed or hash-invalid reference must fail closed. The standalone validator and CLI must share the same resolver rather than implementing different interpretations.

2. Prevent selective citation. Define deterministic applicability metadata for each directive requirement—such as task IDs/types, milestones, relevant paths, lifecycle event and effective date. The system must derive the applicable active requirements and compare them against the task’s `directive_refs`. A task cannot satisfy compliance by citing only the easiest applicable requirements. Unknown applicability, conflicting active requirements or unresolved scope must block controlled work and require an existing blocker/owner decision—not silently choose.

3. Protect owner authority and history. Define explicit directive states such as proposed, active, superseded and withdrawn. AI may draft a directive but may not self-activate, amend, supersede or withdraw an owner directive. Original verbatim source files, hashes and requirement IDs become append-only after activation. Corrections must use numbered amendments with supersession links. Add CI tests that reject silent deletion, renumbering or rewriting of active source/requirements.

4. Replace “materially amended” with machine-enforceable migration rules. Accepted/canceled historical tasks remain untouched. Define exact transitions that cause a legacy nonterminal task to enter regime 1.0—for example replan, rework/reclaim, or specified packet-field changes. Do not rely only on the task’s original `created_at`, because that would let an old packet remain grandfathered forever after substantial rework. Test every relevant current task state and prove no existing task is deadlocked.

5. Define frozen-evidence identity correctly. A raw SHA comparison alone can break after merge, rebase or squash even when reviewed file contents are identical. Specify whether final verification binds to an exact commit, tree hash, or path-scoped content manifest, while preserving the reviewed SHA as provenance. Any relevant product/control-file change after review must invalidate the affected PASS evidence. Add adversarial tests for post-review edits, identical-tree merges, merge commits, rebases and squash merges. Acceptance must never consume evidence for different relevant contents.

6. Keep reminder hooks bounded and advisory. Do not inject raw directive source text into prompts. Inject only validated applicable requirement IDs, short imperative summaries and file pointers. Put a strict size limit on reminder output and avoid repeating the same full reminder on every prompt or compaction, because that would recreate the context-bloat problem this project already corrected. An invalid/corrupt registry must produce a visible fail-closed warning; it must never silently emit nothing and continue. Treat registry text as data so it cannot become a prompt-injection or command-execution surface.

7. Document the bootstrap sequence. Explain exactly how M0-T023 can be created, cite D-001 and prove the new regime on itself without circularly depending on enforcement code that does not exist yet. The final evidence must distinguish bootstrap actions performed under the old CLI from validations replayed under the completed new CLI.

8. The adversarial harness must include at minimum: missing/fake/withdrawn references; omitted applicable requirements; multiple simultaneous directives; amendments and supersession; conflicts; corrupted manifests/hashes; legacy terminal immutability; every grandfathered nonterminal transition; stale post-review evidence; merge/rebase/squash behavior; reminder size/deduplication; hook failure; and proof that the directive-compliance verifier is operationally read-only.

Keep the two-lane principle: the registry records authoritative owner instructions, while all work-blocking decisions continue through the existing CLI, blockers, holds and gates. Shared read-only reference resolution is not a second gate or competing authority.

Return with:

* PR number and URL, branch and frozen base;
* final head SHA and exact changed-file list;
* M0-T023 packet, dependency and ownership boundaries;
* D-001 requirement-to-code/test evidence map;
* migration table for every existing task status;
* all local and remote CI results stated separately;
* independent verifier, control/code and security reports bound to the final reviewed evidence identity;
* unresolved limitations or owner decisions;
* explicit confirmation that nothing was merged, accepted, deployed, purchased, installed, closed or released.

Stop after opening the green reviewed PR.
<!-- END VERBATIM OWNER TEXT -->
