# D-018 source-001 — owner directive (verbatim), 2026-08-18

Channel: owner-typed instruction in the orchestrator session (continuation of the
D-017 session, after the D-017 close-out report). Captured verbatim below;
nothing added, removed, or paraphrased. Frozen base at capture:
origin/main c123b5e723c4a61f891ab215d194255e2f280d4e.

---

You are authorized to perform exactly ONE bounded corrective vertical-integration task for the context-intelligence system. This is one task, one implementation branch, and one PR—not a restart of D-013 and not a multi-unit program.

First reconcile everything against the live repository. The dated checkpoint is origin/main c123b5e, 97 accepted tasks, M0-T063–M0-T069 accepted, and M0-T075 currently the next unused M0 ID, but verify every fact live before acting. Read the applicable AGENTS.md, CLAUDE.md, control-plane rules, D-013, D-017, the accepted task packets, and the actual source. If the worktree is dirty, the next ID is no longer free, an overlapping PR exists, or control-plane state is inconsistent, stop without edits and return the reconciliation evidence.

If the checkpoint still permits it, create exactly one task using the next valid ledger ID, presently expected to be M0-T075, titled substantially "Context pipeline end-to-end integration, concurrency hardening, and promotion-proof repair." Use one branch and one PR. Do not reopen M0-T069, rewrite its historical review records, or pretend its 42-case result was false. Preserve it honestly as an index-parity benchmark and add a new follow-up correction/evidence record explaining its actual scope.

The required outcome is one genuinely operating context compiler—not parallel tools that merely could be consumed later. Preserve the existing context_pack.py public interface where practical. The canonical compiler must consume, under one shared budget:

- The authoritative task packet.
- The exact applicable requirement IDs AND exact requirement text, resolving directive_refs including "ALL" deterministically.
- Changed files and canonical implementation paths from task scope. Seed the graph from real changed/allowed paths, never from an entire prose output description. Prose fields may be parsed only through a strict deterministic path extractor. Every unresolved seed must be recorded, and a task requiring code evidence must not be declared sufficient when no relevant graph/source evidence resolved.
- Bounded Unit E repository views and Unit C subsystem/ontology results.
- Bounded relevant Unit D memory digests as explicitly advisory evidence, with absence or quarantine stated honestly.
- Exact authoritative source excerpts and relevant tests/contracts selected deterministically from task scope, changes, and graph evidence. Detailed code claims must bind to reopened sources.
- Exact inclusion, omission, truncation, query, digest, and coverage provenance.

Role sufficiency must become enforceable. If required task, requirement, diff, source, or review evidence is missing, ambiguous, stale, unsafe, or unavailable, emit a bounded machine-readable result and exit nonzero. Preserve the existing split proposal for over-budget material. Do not silently treat a recorded omission as success.

Create one canonical orchestrator-facing entry point outside tools/agent_supervisor/** that future Claude operation can actually invoke. It must use the integrated compiler rather than building a second packet. Where model routing is requested, derive model_routing.Signals from the compiled task/diff/graph/ontology evidence; missing signals must set ambiguity/missing-evidence and must never silently default a complex task to LOW. Produce a bounded routing/dispatch manifest and record the decision through the accepted external runtime convention. If true automatic controller consumption cannot be implemented without changing protected supervisor files, state that boundary honestly and wire the canonical non-protected command into the operating instructions/runbook; do not claim automatic supervisor integration.

Fix the memory-graph transaction. The single-writer protection must cover load-current → idempotency/conflict check → mutation → validation → generation promotion. Two different concurrent valid digests must either both survive, or one must explicitly receive concurrent_writer and succeed on retry. It is forbidden for both calls to report promoted while one node disappears. Add the exact two-writer stale-read/lost-update regression test.

Apply one shared canonical repository-path and real-path-containment rule to every context-related file read. Reject absolute paths, drive paths, "."/"..", doubled separators, backslash ambiguity, traversal, and repository symlinks/junctions whose resolved target leaves the checkout. Cover at least context --include, deep source views, graph/view seeds, ontology resolution inputs, memory evidence paths, and task-derived paths. Never disclose a private absolute path in an error or packet.

Make retention real rather than documentary: invoke bounded generation retention safely for index and memory stores while preserving rollback generations, and apply bounded/rotated retention to external telemetry and routing JSONL records. Keep all runtime state outside Git and preserve redaction.

Extend—not replace—the Unit F benchmark. Before changing behavior, capture a G0 baseline from current accepted main. Retain the existing 42/42 index cases. Add an end-to-end frozen corpus for the five required task shapes that invokes the actual compiler with the same task packet, diff base, role, provider/model, reasoning setting, and source snapshot. Prove cold/warm determinism, global-budget compliance or nonzero split refusal, required-evidence completeness, exact provenance, resolved graph/source evidence, advisory-memory handling, and representative-task correctness no worse than the captured baseline. Add a distinct parser-version case. Fold actual lock refusal and orphan quarantine into the pass predicates. Correct the p95 calculation while touching this benchmark. Provider token savings must remain UNMEASURED unless provider-reported usage genuinely exists. Do not approve or activate D-013-R060 promotion; return the evidence and recommendation for the owner.

Repair the status projection so its check validates every material input that can change its output—not HEAD alone. Cover task packet/status, verification registry, gates, submissions/review decisions, task/directive indexes, and Git identity with a deterministic input-manifest digest. Map the actual project_control.py statuses, including self_check and canceled, to the directive's compact meanings. Clearly distinguish a committed historical snapshot from a freshly generated current projection.

Correct and smoke-test every command in docs/CONTEXT_PIPELINE_RUNBOOK.md, especially the required --max-bytes context-pack argument. Make the runbook describe the one canonical compiler and state honestly whether controller/supervisor consumption remains owner-gated.

Add one permanent additive CI job running all context-pipeline suites from Units B–F plus the new integration and adversarial tests. Do not remove, weaken, skip, or replace existing CI, security, modularity, branch-protection, or supervisor tests.

The fresh independent reviewer must inspect actual code and independently reproduce at least these proofs:

1. On a clean accepted task, real allowed/changed implementation paths resolve; exact requirements and at least one authoritative source excerpt are present; prose output descriptions are not used as literal graph paths.
2. A materially insufficient role packet exits nonzero.
3. Two synchronized memory writers cannot lose a node.
4. Absolute, traversal, and out-of-repository symlink reads are refused without leaking private paths.
5. An uncommitted task-status/control-plane change makes a projection stale.
6. The complete compiler/memory/views/benchmark/projection suites run in permanent CI.
7. The canonical orchestrator-facing entry point actually calls the integrated compiler and grounded router; documentation alone or unused modules are not acceptance evidence.
8. Existing 42/42 index parity remains green.

Protected boundaries are absolute: do not modify tools/agent_supervisor/**, the live controller config, config.toml, model_selection.toml, protected hashes, limited-auto state, supervisor safety behavior, branch protection, security policy, or history. Do not run the controller update bundle, do not perform a live supervisor probe, do not make the D-013-R060 promotion decision, and do not touch NYC application logic except hermetic test fixtures genuinely required for the five benchmark shapes. Claude is the sole writer; producer and fresh reviewer/verifier identities remain separate.

Run all focused and regression suites, modularity, directive validation, and required CI. Submit, independently review, rework genuine findings, verify at the frozen reviewed SHA, accept, and merge only on green under the existing control plane. Then stop and return: task/PR/merge identities, exact tests and CI evidence, before/after end-to-end benchmark results, whether automatic controller consumption is still owner-gated, the unchanged protected hashes, and one consolidated owner-action bundle. Do not execute that bundle.
