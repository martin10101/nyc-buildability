<!--
CAPTURE METADATA (not part of the owner's words; the verbatim directive follows the marker below)
  directive_id:      D-001
  source_file:       source-001.md
  kind:              original
  captured_at:       2026-07-23
  captured_by:       orchestrator (lead session)
  channel:           owner_message
  frozen_baseline:   1acb9b510541cfa87afff6b2dc197880e01a389b (origin/main at capture)
  integrity:         SHA-256 of this file is recorded in manifest.json -> sources[].content_digest_sha256
  append_only:       This file is IMMUTABLE once D-001 is active. Corrections are new
                     numbered amendment files (source-002-amendment.md, ...), never edits here.
-->

# D-001 — Verbatim owner directive (original)

<!-- BEGIN VERBATIM OWNER TEXT -->
STANDING DIRECTIVE-COMPLIANCE PROTOCOL

Apply this protocol to every future owner directive. It supplements the existing task, gate and PR controls. Do not weaken any existing independent-review requirement.

The objective is to prevent a producer or orchestrator from declaring a directive complete based on memory, intention or a general summary.

1. REQUIREMENT EXTRACTION BEFORE EDITING

Before changing any file:

* freeze and report the exact base SHA;
* copy the owner directive verbatim into a durable compliance matrix;
* assign every independently testable requirement a stable ID such as R-001, R-002, etc.;
* do not combine unrelated requirements into one broad row;
* do not omit qualifications, negative requirements, stop conditions or “nothing was authorized” boundaries.

Every row must contain:

* requirement ID;
* verbatim or faithful atomic requirement;
* affected PR/task;
* expected file or artifact;
* implementation owner;
* exact acceptance evidence;
* negative/adversarial check;
* status: pending, implemented, PASS, FAIL, BLOCKED or UNVERIFIABLE;
* evidence location.

Before implementation, return the requirement-to-file/test map. If any requirement is ambiguous, contradictory or lacks a provable acceptance method, stop and identify it. Do not silently interpret it.

2. ONE PR AT A TIME

Do not implement corrections across several PRs simultaneously unless the owner explicitly requires atomic cross-PR work.

For multiple PRs:

* reconcile each branch independently;
* state each branch’s actual ledger;
* separately state any hypothetical combined-after-merge ledger;
* never describe proposed or unmerged changes as current-main state;
* complete and verify one PR before beginning the next whenever possible.

3. ONE CURRENT SOURCE OF TRUTH

Do not leave superseded operational instructions active in the same document.

* Move historical structures to a clearly marked archive or amendment log.
* Keep one concise authoritative current section.
* Search the entire changed tree for old task counts, old IDs, old ownership, old branch names, old worktrees, old dates and superseded instructions.
* Git history is the preferred history; active documents should not require a future agent to decide which contradictory paragraph controls.

4. IMPLEMENTATION EVIDENCE

An item may be marked implemented only when the actual diff contains the change.

An item may be marked PASS only when its defined evidence has been executed or inspected.

For every claim containing “all,” “every,” “none,” “exactly,” “complete,” “swept,” “enforced” or “unchanged,” provide the command, query, test or exhaustive file list proving it.

Do not use a free-form return report as the evidence source. Generate the return from the completed compliance matrix.

5. SEMANTIC AND STALE-REFERENCE SWEEP

After implementation and before independent review:

* inspect the complete final diff;
* search for every superseded literal, identifier, count, date, branch, worktree and ownership assignment;
* recalculate ledger totals from actual files;
* verify task dependencies against actual task IDs;
* verify blocker claims against the control code that enforces them;
* distinguish machine enforcement, structural prevention, manual procedure and proposal-only language;
* verify that every claimed automatic behavior actually has executable code.

Passing JSON validation or CI does not prove semantic consistency.

6. EXTERNAL AND TIME-SENSITIVE FACTS

For dependency versions, publication ages, prices, official endpoints and effective dates:

* query the primary official source at execution time;
* use exact timestamps when a policy is measured in seconds or complete days;
* do not substitute a blog/article date for a package-registry publication timestamp;
* record the source URL, retrieval time and exact value;
* if official sources disagree, stop with data_conflict;
* never use an estimate where an exact acceptance threshold is required.

7. CLEAN-CONTEXT INDEPENDENT VERIFICATION

After the producer finishes, assign a separate verifier that did not produce the changes.

The verifier must receive:

* the original owner directive;
* the complete requirement matrix;
* the frozen base SHA;
* the final head SHA;
* the actual complete diff;
* relevant repository files and test results.

Do not give the verifier the producer’s conclusion as its source of truth.

The verifier must independently mark every requirement:

* PASS — directly proven;
* FAIL — absent, incorrect or contradictory;
* BLOCKED — legitimate external blocker;
* UNVERIFIABLE — evidence insufficient.

Any FAIL or UNVERIFIABLE result prevents the directive from being called complete. Return it to the producer, correct it and rerun the clean-context verification.

8. MACHINE CHECKS

Where a requirement can be mechanically enforced, add a regression rather than relying on prose. Prioritize checks for:

* actual task and ledger counts;
* milestone summaries matching task files;
* task IDs and dependency direction;
* blocker records referencing the intended task IDs;
* prohibited old identifiers or branch/worktree references;
* contract closure and unexpected fields;
* fixture-only work not satisfying production acceptance;
* cross-PR current-versus-proposed state;
* no missing requirement-matrix rows.

Semantic requirements that cannot be fully automated still require independent verification.

9. RETURN STANDARD

The final return must include:

* frozen base and final head;
* exact changed files;
* complete requirement matrix;
* PASS/FAIL/BLOCKED/UNVERIFIABLE count;
* proof for every exhaustive claim;
* stale-reference sweep results;
* local and remote checks separately;
* independent verifier identity and results;
* unresolved items;
* confirmation of every prohibited action that was not taken.

Do not say “all requirements addressed,” “complete,” “fully corrected,” or equivalent unless:

* every matrix row is PASS or an explicitly owner-accepted BLOCKED item;
* zero rows are FAIL or UNVERIFIABLE;
* the independent clean-context verifier agrees;
* the final diff and branch state were reconciled after the last change.

10. OWNER BOUNDARY

Passing this protocol never authorizes merging, task movement, claiming, dispatch, implementation outside the approved scope, acceptance, deployment, purchasing, dependency installation or PR closure. Those actions still require their existing approvals.

First propose how to integrate this protocol into the existing control plane without duplicating the current task/gate system. Do not implement or merge the protocol until owner approval.


Owner directive — implement a durable Owner Directive Compliance System.

Purpose: eliminate reliance on chat memory. Every substantive owner instruction, correction, restriction, authorization, replan, or PR amendment must become durable, atomic, traceable, independently verified repository state before implementation can be declared complete.

This directive authorizes creating, moving to ready, claiming, and implementing exactly one dedicated governance/control task if the reconciled ledger and concurrency rules permit it. Use lead-only implementation on a dedicated branch and open one PR for owner review. This does not authorize accepting or merging that task, modifying or closing PRs #91, #93, #94, #95, or #64, dispatching product work, changing product code, deploying, purchasing, installing dependencies, or weakening any existing blocker, hold, gate, or owner-approval requirement.

First reconcile `origin/main`, the ledger, current claimed/blocked tasks, worktrees, and open PRs. Freeze and report the exact base SHA. Create a new task ID only after reconciliation; do not reuse or alter an accepted task.

Implement the following architecture:

1. Root `CLAUDE.md`

Add a concise section of no more than 12 lines titled “Owner-directive compliance.” Do not place the full workflow there and do not create a competing `.claude/CLAUDE.md`.

The section must say that a substantive owner directive includes any request that changes, corrects, restricts, authorizes, replans, implements, dispatches, claims, accepts, merges, or amends repository work. Pure explanations and read-only status questions do not create directives unless they introduce a new requirement.

Before planning, writing, claiming, dispatching, submitting, accepting, merging, or declaring completion for an applicable directive, Claude must:

* invoke `/directive-compliance`;
* capture the directive and amendments under `project-control/directives/`;
* bind the affected task/PR to exact atomic requirement IDs;
* preserve prohibitions, holds, sequencing, dependencies, harnesses, evidence requirements, owner decisions, and required return items;
* require independent completeness and final verification;
* refuse to use narrative assertions such as “all addressed” as evidence.

Keep the existing automatic-context budget green.

2. Reusable project skill

Create:

`.claude/skills/directive-compliance/SKILL.md`

Its description must cause Claude to invoke it for owner directives, corrections, PR amendments, replans, “fix everything,” “address all items,” implementation authorizations, and claims that work is complete. It must remain manually invocable as `/directive-compliance`.

The workflow must:

* classify whether the prompt is a substantive directive;
* capture the exact text verbatim before acting;
* hash the captured source;
* create append-only amendment files instead of silently rewriting history;
* decompose every instruction into atomic requirements;
* separately capture positive deliverables, prohibitions, holds, sequencing, dependencies, decisions, unresolved questions, acceptance harnesses, evidence requirements, external-current-fact checks, and required return-report items;
* run a forward trace from every source paragraph/item to requirement IDs;
* run a reverse trace from every requirement and changed file back to its source;
* stop for genuine ambiguity instead of choosing silently;
* bind the applicable IDs to task packets and review packets;
* invalidate earlier verification when the reviewed head SHA or directive source changes;
* prohibit producer self-verification;
* require every item to end as PASS, FAIL, BLOCKED, UNVERIFIABLE, or independently justified NOT_APPLICABLE;
* prohibit “complete,” “all addressed,” or equivalent claims while any item is pending, failed, blocked, unverifiable, stale, or missing evidence.

3. Durable directive registry

Create a versioned structure under:

`project-control/directives/`

Include:

* a registry/index supporting multiple concurrent active directives;
* versioned schema files;
* one directory per directive;
* verbatim `source-001.md`;
* append-only `source-002-amendment.md`, etc.;
* `manifest.json`;
* `requirements.json`;
* `verification.json`.

Do not use one global “current directive” pointer that loses parallel work. The registry must map directives to exact tasks, branches, PRs, scopes, and statuses.

Each manifest must include at least:

* directive ID and version;
* capture timestamp;
* source-file hashes;
* frozen baseline SHA;
* affected tasks/PRs;
* scope and applicability;
* amendments and supersession relationships;
* owner-approval state;
* lifecycle state;
* final reviewed SHA when applicable.

Each atomic requirement must include at least:

* stable requirement ID;
* exact source anchor;
* plain-language obligation;
* classification;
* affected scope and paths;
* dependencies and sequencing;
* required harness/test;
* required evidence;
* producer;
* independent verifier;
* status and reason;
* evidence paths;
* reviewed SHA;
* supersession or NOT_APPLICABLE justification where relevant.

Capture this setup directive itself as the first live directive and use it to prove the system against its own implementation.

4. Project-control integration

Do not create a competing lifecycle authority. Extend `tools/project_control.py` and its existing atomic-write and orchestrator-authority model.

Prospectively enforce that:

* a new or materially amended task cannot be claimed without applicable directive references;
* submission cannot proceed without implementation evidence for every applicable requirement;
* acceptance cannot proceed without independent final verification of every applicable requirement at the same frozen SHA;
* a source amendment or head-SHA change invalidates stale verification;
* producer and verifier identities must differ;
* NOT_APPLICABLE requires explicit reasoning and independent approval;
* BLOCKED, FAIL, UNVERIFIABLE, pending, stale, or missing evidence prevents acceptance.

Do not retroactively rewrite or reject accepted historical tasks. Define an effective version/date and a safe migration rule for existing nonaccepted work: apply the protocol when that task is next amended, replanned, reclaimed, or continued. Prove that this does not deadlock currently claimed or awaiting-gate work.

5. Existing workflow integration

Amend these skills without duplicating the full protocol:

* `/start-controlled-task`: require exact directive requirement references.
* `/replan-project`: capture new owner information or corrections as a directive/amendment before changing the plan.
* `/submit-checkpoint`: require requirement-to-evidence mapping.
* `/run-quality-gate`: require directive verification at the frozen SHA and forbid relying on the producer’s summary.

Update `.claude/rules/project-control.md` with concise path-scoped rules for the new directive records.

6. Independent verifier

Create:

`.claude/agents/directive-compliance-verifier.md`

It must be a custom, read-only agent governed by the existing reviewer restrictions. It must not treat the producer report or producer-created matrix as proof of completeness.

At intake it must compare the verbatim directive and every amendment against the atomic matrix and return PASS/FAIL/BLOCKED with missing, weakened, combined, or invented requirements.

At final review it must inspect:

* the original directive and amendments;
* atomic requirements;
* frozen baseline and head SHAs;
* actual diff and files;
* tests/harness outputs;
* task and PR state;
* prohibited-action evidence;
* required return items.

It must report every requirement ID individually. “Spot checked,” “appears complete,” and summary-only verification are prohibited.

7. Deterministic validator and CI

Create a stdlib-only read-only validator such as:

`tools/validate_directive_compliance.py`

Add comprehensive tests and wire them into the existing control-plane CI rather than creating an unconnected green check.

Validate at least:

* schemas and unique IDs;
* source hashes;
* append-only amendment history;
* source-anchor coverage;
* valid task/PR references;
* applicable task requirement references;
* producer/verifier separation;
* evidence-path existence;
* baseline/head SHA presence;
* stale verification after source or head changes;
* no unsupported NOT_APPLICABLE;
* no acceptance with unresolved items;
* no narrative “complete” state replacing atomic statuses;
* no silent disappearance of requirements through supersession;
* no retroactive mutation of accepted packets;
* safe handling of multiple simultaneous directives.

No new package may be installed. If any dependency is proposed, stop and apply `/dependency-security` first.

8. Context and enforcement hooks

Create a small hook that reads only the active directive registry and injects a compact reminder and active directive paths:

* at session startup/resume;
* after compaction;
* on `UserPromptSubmit`, using a short conditional reminder rather than the entire protocol.

The per-prompt injected text must remain small and say, in substance: “If this prompt changes repository work, invoke `/directive-compliance` and capture/bind it before acting.”

Add narrowly scoped deterministic action enforcement only after adversarial tests pass. It must not block normal read-only inspection or test execution. It should block applicable producer dispatch or controlled lifecycle transitions when the task lacks valid directive references or the validator fails. Any merge guard must preserve explicit owner-approval requirements.

Do not replace or weaken `agent_dispatch_guard.py`, `readonly_agent_guard.py`, their tests, ADR-005, or existing authority rules.

9. Required adversarial harnesses

Include positive and negative tests proving at least:

* one numbered directive item omitted;
* a prohibition omitted;
* two materially different requirements incorrectly combined;
* an invented requirement;
* an amendment captured but not added to the matrix;
* source text changed without hash/version change;
* implementation verified at SHA A and then changed at SHA B;
* producer attempts self-verification;
* pending/FAIL/BLOCKED/UNVERIFIABLE item with a “complete” claim;
* unsupported NOT_APPLICABLE;
* evidence path missing;
* task references the wrong directive;
* two concurrent directives with different scopes;
* accepted historical task remains immutable;
* existing claimed task is not accidentally deadlocked;
* context compaction restores the short active pointer;
* hooks do not inject the full protocol on every prompt;
* normal status, test, and read-only commands remain usable;
* governance files cannot be modified by ordinary product tasks without an applicable governance directive.

10. Bootstrap review and return

Use this directive’s own matrix during implementation. After freezing the PR head, use the new read-only directive-compliance verifier plus the existing required control/security reviewers. Re-run all existing control-plane, hook, context-budget, and repository CI checks.

Return:

* branch, PR, base SHA, and final head SHA;
* exact changed files;
* before/after eager-context totals;
* every requirement ID with PASS/FAIL/BLOCKED/UNVERIFIABLE status and evidence;
* hook behavior and adversarial-test results;
* project-control transition enforcement;
* migration behavior for accepted and currently active work;
* local and GitHub CI results stated separately;
* unresolved limitations and owner decisions;
* explicit confirmation of everything not merged, accepted, dispatched, deployed, installed, purchased, modified, or closed.

Do not claim this makes an AI infallible or guarantees semantic completeness. State precisely what is mechanically enforced, what is independently reviewed, and what still requires owner or qualified-human judgment. Stop after opening the PR and returning the evidence. Do not merge it.
<!-- END VERBATIM OWNER TEXT -->
