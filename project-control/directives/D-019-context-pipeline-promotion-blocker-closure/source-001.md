# D-019 — Owner master prompt (verbatim capture, 2026-08-19)

> Captured verbatim per D-001 from the owner's typed session instruction that
> authorized ONE bounded corrective task (D-019 / M0-T076). Preceded by the
> read-only orientation file
> `NYC_BUILDABILITY_D019_NEXT_SESSION_HANDOFF_2026-08-19.md` (external, not in any
> checkout). This capture is the immutable directive source; requirements.json
> decomposes it into binding rows.

Read the attached NYC_BUILDABILITY_D019_NEXT_SESSION_HANDOFF_2026-08-19.md completely before taking any action.

You are authorized to execute ONE bounded corrective task end to end. This is not a rebuild and does not authorize NYC application work, controller changes or pipeline promotion.

SECTION 1 — LIVE RECONCILIATION

Before creating anything:

1. Fetch and reconcile live origin/main.
2. Confirm the handoff checkpoint or report every difference.
3. Confirm the worktree is clean.
4. Confirm M0-T076 and D-019 remain unused; if either is occupied, choose the next valid identity and report it.
5. Confirm no overlapping branch or PR.
6. Run the directive validator.
7. Capture a clean, reproducible pre-change failure record for every blocker listed below.

Do not rely on the historical PASS reports as proof. Treat them as claims to verify.

SECTION 2 — CONTROL-PLANE IDENTITY

Capture the complete owner instruction as one new directive, proposed:

D-019 — context-pipeline-promotion-blocker-closure

Create one task, proposed:

M0-T076 — Context pipeline promotion-blocker closure and adversarial completion protocol

Use one branch and one PR. Producer, adversarial reviewer and directive verifier must be independent.

Do not reopen or rewrite M0-T075. Preserve its records historically and add an honest correction/reconciliation report.

SECTION 3 — REQUIRED CORRECTIONS

A. MEMORY LOCK

Repair SingleWriterLock so:

- Ownership metadata is complete before the public lock becomes visible.
- Every owner has an unguessable ownership token.
- Stale takeover uses an atomic move/quarantine operation.
- Missing or partial metadata cannot cause immediate reclamation of a potentially live lock.
- Release removes the lock only when the token still matches.
- Load, conflict/idempotency check, mutation, validation, promotion and retention remain inside one valid ownership span.

Add the exact deterministic regression where writer A pauses during lock publication and writer B attempts entry. The forbidden outcome—both reporting promoted while one node disappears—must be impossible.

B. CONTAINMENT AND PRIVACY

Inventory every context-related read.

Apply the shared canonical and real-path containment rule to all repository evidence reads, including:

- task, state and directive requirements;
- routing table;
- checkpoint, blocker and handoff records;
- --include and --ci-summary;
- source/test/contract excerpts;
- graph/view seeds;
- ontology inputs;
- deep views;
- memory evidence paths.

Absolute paths, drive paths, traversal, dot segments, doubled separators, backslashes and escaping links must never be read.

Errors and packets must not repeat a supplied private absolute path.

A refused explicitly requested --include or --ci-summary must make the result nonzero/insufficient. Its marker content must be absent from context.md, metadata, evidence files, stdout and stderr.

C. CORRECT DIFF IDENTITY

The canonical orchestrator must not silently use HEAD for active worker or reviewer tasks.

Resolve and validate the task's frozen G0 reviewed SHA as the default diff base, or require an explicit trusted --diff-base when no frozen base is available.

Record:

- chosen base SHA;
- how it was resolved;
- current head SHA;
- dirty/clean state;
- exact diff command.

Add committed-work tests. After a task change is committed, the worker and reviewer packets must still contain the applicable committed hunks.

D. TRUE UNIT E INTEGRATION AND SEED QUALITY

Consume actual accepted Unit E repository-view functions, or extract a genuine shared primitive used by both Unit E and the compiler. Do not describe duplicated logic as "Unit E-class."

Deterministic seed order:

1. Actual changed implementation paths.
2. Canonical allowed implementation paths.
3. Relevant graph-derived test/dependent paths.
4. Strictly extracted prose candidates.
5. Documentation/control-plane candidates only when relevant.

Record all selected, unresolved and skipped-over-cap candidates.

A clean M0-T066 proof must query its subsystem implementation files before documentation and reports consume the five-seed cap.

Avoid duplicate source/test excerpts.

E. HONEST ROUTING

Every model_routing.Signals field must be:

- derived from authoritative structured compiled evidence; or
- identified as undetermined.

An undetermined risk-bearing signal must raise ambiguity_or_missing_evidence. Never silently use false for unknown concurrency, security, schema, destructive-operation, external-side-effect or protected-configuration impact.

Prove that a concurrency-focused task cannot emerge as concurrency_or_performance=false with no ambiguity.

Do not modify protected model configuration.

F. USEFUL BOUNDED MEMORY

Keep memory explicitly ADVISORY.

For relevant task digests include bounded useful fields:

- digest ID;
- outcome and agent;
- bounded note;
- requirement IDs;
- relevant file paths;
- evidence references;
- unresolved/quarantined state;
- source/repository identity.

All memory content remains under the existing single global packet budget and never substitutes for reopened authoritative source.

G. REPRODUCIBLE PROMOTION BENCHMARK

Replace the dirty-working-tree comparison with a genuinely frozen, apples-to-apples comparison.

Baseline and post-change runs must use equivalent:

- task packet;
- diff base;
- role;
- provider/model;
- reasoning setting;
- source snapshot;
- clean/dirty state.

The exact documented e2e command must exit 0 twice from independent clean checkouts.

"No worse than baseline" must test meaningful required evidence and relevance, not only source-ID counts.

Keep provider token savings UNMEASURED unless real provider usage exists.

Add the complete clean-checkout e2e benchmark to permanent CI. Do not rely only on the single-shape unit test.

SECTION 4 — MANDATORY ADVERSARIAL COMPLETION PROTOCOL

Before submission, the producer must create a requirement-to-counterexample matrix.

For every requirement containing "every," "never," "atomic," "same," "complete," "exact," "cannot" or equivalent absolute language:

- state the most likely counterexample;
- execute it;
- record command, input, exit, output digest and result.

The independent reviewer must:

1. Begin from the directive and actual code, not the producer's conclusions.
2. Use a fresh clean worktree pinned to the submitted SHA.
3. Create new adversarial probes not copied from producer tests.
4. Trace actual imports and calls for every claimed integration.
5. Execute all documented commands exactly.
6. Test clean, dirty, committed, uncommitted, missing, malformed and hostile input states where applicable.
7. Attempt to exploit every observation, including defects labeled pre-existing or low probability.
8. Reject proxy proof such as field presence, source counts or test counts when semantic correctness is required.
9. Mark FAIL if any literal directive guarantee is contradicted, regardless of how many other tests pass.

A review observation affecting a required guarantee is blocking. It cannot be downgraded merely because the underlying code predates this task.

SECTION 5 — REQUIRED PROOFS

At minimum independently reproduce:

1. The former two-promoted/one-lost schedule no longer loses either node.
2. Absolute --ci-summary and --include markers are never read or disclosed and cause nonzero.
3. Static and raced escaping-link probes refuse.
4. Committed task changes appear using the recorded frozen base.
5. M0-T066 graph evidence starts from its implementation.
6. Actual Unit E provenance and call identity appear.
7. A concurrency task routes high/ambiguous rather than silently false.
8. A real advisory digest contributes useful bounded context.
9. Status projection still catches uncommitted changes.
10. Exact clean-checkout e2e command exits 0 twice.
11. Expanded index parity remains byte-identical.
12. All pre-existing context/index/graph/memory/view/benchmark/projection and routing suites remain green.

SECTION 6 — HARD SCOPE LIMITS

Do not modify or operate:

- tools/agent_supervisor/**;
- protected config.toml;
- model_selection.toml;
- controller manifests or live controller;
- apps/**;
- services/**;
- packages/**;
- supabase/**;
- NYC zoning, legal or numeric application logic;
- branch protection or security policy;
- limited-auto;
- history rewriting.

Do not approve or activate D-013-R060.

Do not run the controller-update bundle or any live probe.

Do not modify code-graph generators, fingerprint or baseline engines unless a new independently reproduced blocker proves it unavoidable. Stop and report before expanding into such a surface.

Do not remove, skip, weaken or replace any existing test.

SECTION 7 — ACCEPTANCE AND RETURN

Use the complete normal lifecycle:

G0 → implementation → producer counterexample matrix → frozen submit SHA → fresh adversarial review → correction/retest if necessary → independent DCV at the exact reviewed identity → G3/G4/G5 → accept → merge only when every required check is green.

Before merge, verify from a fresh clean worktree:

- exact head-SHA identity;
- full clean e2e benchmark twice;
- exact lock exploit;
- full containment probes;
- all documented commands;
- all existing and new suites;
- modularity;
- directive validation;
- forbidden-path diff empty.

The final return must include:

- directive/task/PR/merge identities;
- exact reviewed SHA and manifest;
- exact commands and test counts;
- adversarial probes and results;
- clean-checkout benchmark results;
- before/after evidence;
- protected-path diff confirmation;
- what remains owner-gated;
- an evidence-based R060 recommendation.

Leave R060 pending for the owner.
