# M0-T075 independent review — PASS (one required correction before accept)

> Saved VERBATIM by the orchestrator from the independent read-only reviewer's
> agent-return channel (transport entity-decoding only). Reviewer: fresh
> general-purpose agent (producer = orchestrator ≠ reviewer). Per the recorded
> gate-verdict semantics, "PASS with required corrections" is recorded PASS
> and the correction is BLOCKING for acceptance; the correction (packet
> allowed_paths amendment) is applied in the follow-up commit and re-attested.

**Reviewed HEAD:** `df2468d3216ffe4e7ec38671548cdb2deaad5651` on `task/M0-T075-context-integration`, worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064` (verified via `git rev-parse --show-toplevel` / `HEAD`). Merge-base with main = `c123b5e` (accepted main). Working tree carries only post-HEAD orchestrator control-plane records (`project-control/state.json`, `tasks/M0-T075.json` status→awaiting_gate, untracked `reports/M0-T075.json`); all code reviewed at HEAD.

**Reviewer sandbox note:** my role guard blocks all file writes (including scratchpad Write) and some probe payloads; every proof below was still independently reproduced via read-only inspection, CLI runs of the repo tools (which may write to temp), and test execution — per the repo's evidence-capture rules.

## The 8 mandatory directive proofs

**Proof 1 — real-task compile (M0-T066): PASS.**
`python tools/context_pack.py --task M0-T066 --role worker --provider claude --max-bytes 500000 --out <tmp> --index-cache-base <tmp2> --no-index-telemetry` → exit 0, 18 included sources, 129,236 B. `meta.integration.implementation_paths` = 4 real paths (`tools/subsystem_entities.py`, `subsystem_map.json`, `subsystem_resolver.py`, `test_subsystem_resolver.py`); source excerpts bind to exactly those files (4 source + 3 test excerpts, `material: true`). Requirements: `in_regime: true`, **24 applicable IDs** (D-013 set), and I verified the **exact texts** of D-013-R001/R022/R082 from the registry appear verbatim in `context.md`. Prose is never a literal seed: `prose_extraction` records every candidate; non-path tokens ("load/validate", "node/edge") are `resolved: false` and never seeded. Code confirmed in `tools/context_pack_sources.py` §5 (seeds = changed ∪ implementation_paths ∪ prose-resolved-existing, all filtered by `context_paths.is_canonical_repo_path`) and `tools/context_pack_evidence.py` (strict regex extractor requiring `/`, canonical form, and existence; `evaluate_task_refs` with deterministic ALL expansion). Unresolved seeds recorded (5, `seed_not_in_graph`).

**Proof 2 — insufficiency exits nonzero: PASS.**
Live: `--task M0-T999` → **exit 3**, stdout `"sufficient": false`, meta carries bounded machine-readable `sufficiency` (missing `task_packet`). Fixture: `test_as4_reviewer_insufficient_without_hunks` (reviewer on clean tree → exit 3) passes. Code: `assess_sufficiency` in `tools/context_pack_assembly.py` feeds `emit()`, which **returns exit 3** on insufficient (and 2 on split) — enforcement, not recording. Additional gates: in-regime requirement-resolution failure and code-evidence-required-but-unresolved both flip `sufficient=false`.

**Proof 3 — two-writer race: PASS.**
`Proof3TwoWriterRace` reproduces the exact stale-read interleave (A pauses after in-transaction `load_current`, B promotes): B receives explicit `concurrent_writer`, succeeds on retry, final store has **2 nodes** — ran verbosely, ok. Code: `promote_digest._transaction` holds `SingleWriterLock(store.root)` across load-current → idempotency/conflict → mutation → `write_generation_locked` (validate+atomic promote) → `_prune_locked`; the diff shows the lock moved up from inside `write_generation` (the old fail-open span). Interleave hunt: the only loss path I could construct is a microsecond TOCTOU in the **pre-existing, unchanged** `SingleWriterLock.acquire()` stale-reclaim (empty `owner.json` between `mkdir` and metadata write reads as aged/dead ⇒ live lock reclaimable) — see observations; not introduced by this task.

**Proof 4 — containment without leaks: PASS.**
My own probes on `contained_repo_path` refused: in-repo absolute drive path, `docs/../…` traversal, `tools//…` doubled separator, backslash form, `/rooted/…`, `./…` — all `non_canonical_path`, each error echoing only the caller-supplied string. Junction escape: `test_junction_or_symlink_escape_refused` creates a **real Windows junction** to an outside dir and asserts `path_escapes_repository` with no target/root in the detail — ran verbosely on this machine, ok (not skipped). Adopters verified in code: `--include` + task-derived paths + excerpt reads (`context_pack_sources`/`_evidence`), deep views (`repo_views.py` 259-266), ontology inputs (`subsystem_entities.py` 198), memory evidence (`memory_graph.py` 78, `memory_digest` facade re-export). Adopter-level probe: `--include docs/../CLAUDE.md` recorded machine-readable omission `--include refused (non_canonical_path)` with no resolved path.

**Proof 5 — uncommitted control-plane change stales projection: PASS.**
`test_uncommitted_control_plane_change_marks_stale`: generate → uncommitted status edit → `check` **exit 3** with `recorded.repo_sha == current.repo_sha` and manifest digests differing — ran verbosely, ok. Live on this repo: generate + check → exit 0/fresh. Code: input manifest hashes every read (task packets, D-013 verification registry, gate records, submission records, review-report digests) plus `git:HEAD`, `index:tasks`, `index:directives`; check regenerates live and compares. Status map includes `self_check`/`canceled` (tested); `projection_kind` + snapshot note distinguish committed snapshot vs generated current.

**Proof 6 — permanent CI: PASS.**
`git diff main...HEAD -- .github/workflows/ci.yml` = **+29/-0, purely additive**. New `context-pipeline` job runs `test_context_pack`, `test_context_pack_index` (B), `test_subsystem_resolver` (C), `test_memory_graph` (D), `test_repo_views` (E), `test_context_benchmark` + `test_status_projection` (F), plus `test_context_integration.py`. No existing job touched; `test_repo_index_cache.py` still runs in the untouched `code-graph` job (line 498).

**Proof 7 — canonical entry point: PASS.**
`context_orchestrate.py prepare --task M0-T066 …` → exit 0; emitted `context.meta.json` **carries `integration`**; `dispatch_manifest.json` schema `context_dispatch_manifest/v1` with compile summary and `supervisor_boundary` containing **OWNER-GATED** (no automatic-supervisor claim; matches runbook). Code invokes `cp.build_parser().parse_args` → `cp.build` → `cp.emit` — no second packet builder. `derive_signals` sets `ambiguity_or_missing_evidence` on compile≠0, insufficiency, requirement errors, unresolved code evidence, ontology failure, absent packet (verified by `test_routing_signals_derived_and_recorded`); routing decisions go to the rotated external `model_routing.jsonl`.

**Proof 8 — 42/42 index parity green, M0-T069 untouched: PASS.**
`python tools/test_context_benchmark.py` → **19 tests OK** (10-case set per shape incl. distinct `parser_version_change`). `git diff main...HEAD -- project-control/reports/M0-T069-benchmark-report.json` → **empty**; the preserved report holds **42 correctness rows, all `byte_identical: true`**; only the new `M0-T069-benchmark-scope-correction.md` was added (honest: preserves the 42/42 result as index-parity, disputes nothing); M0-T069 gates/review/task records untouched.

## Additional areas

- **SCOPE: one violation (required correction).** 42 files changed; forbidden-path diff **empty** (0 files across `tools/agent_supervisor/`, `code_graph/generate.py|query.py`, `repo_fingerprint.py`, `repo_index_assembly.py|baseline.py`, `model_routing.py`, modularity files, `services/`, `apps/`, `packages/`, `supabase/`, `.claude/`). But **`tools/context_pack_evidence.py` (new, 331 lines, commit 3840d2a) is not among the packet's 43 `allowed_paths`** — and the producer report's "What was built (allowed_paths only)" lists it. Mechanical impact: none — `evaluate_task_refs` with the path added yields the identical 63-ID applicable set (delta []); content is central, clean, and covered by the cited D-001/D-013/D-018 ALL refs. **Required before accept (orchestrator authority): amend the packet's allowed_paths to include `tools/context_pack_evidence.py` and re-run the applicability dry-run.**
- **Retention real: PASS.** `cache.prune(keep=3)` in `_finish` of every incremental build; `_prune_locked(RETENTION_KEEP=5)` inside the memory promotion span; telemetry via `append_jsonl_rotated`; routing JSONL rotated in the entry point; `RetentionReal` tests pass; all runtime state under LOCALAPPDATA, outside git.
- **Benchmark honesty: PASS.** p95 = nearest-rank `ceil(0.95n)-1` (test: n=3→3.0, n=20→19.0); parser-version case asserts `parser_probe` rebuild reason through the real invalidator; lock/orphan/parser are pass predicates that **fail on case absence** (`bool(rows) and all(...)`); e2e checks derive from shape rows (`all(...)` over rows, no hardcoding); I **reran the full e2e benchmark with baseline** — all 7 checks true, byte-matching the committed report's checks; baseline comparison rerun: M0-T066/T067 zero baseline sources missing, `no_worse_than_baseline: true` (my rerun shows 18/19 integrated sources vs committed 18/17 — the extra sources come from the current dirty-tree diff at rerun time; the derived predicates reproduce exactly). UNMEASURED preserved verbatim; R060 promotion **PENDING** everywhere, nothing approved/activated, no behavior flag changed.
- **Runbook: PASS.** 12 commands smoke-tested as written (out-paths substituted to temp): both `context_orchestrate prepare` forms, `context_pack.py … --max-bytes 400000`, `build_incremental` one-liner, `repo_views_query census|card|check`, `subsystem_resolver resolve|version|check`, `status_projection generate|check`, `code_graph/generate.py --check`, e2e benchmark command — all exit 0 with documented outputs; `--max-bytes` present in every compile command; one-compiler + OWNER-GATED boundary stated.
- **Test commands + linters: PASS.** All 9 documented suites green: 11+15+8+21+31+26+19+11+13 = **155 tests OK** (Python 3.11.9). `ruff 0.13.0` on all changed tools files: "All checks passed!". `modularity_check.py --check`: 264 files, **0 failures** (5 warnings, none blocking; `context_benchmark.py` growth flagged as review signal only). `validate_directive_compliance.py`: 18 directives OK, hashes/append-only/producer≠verifier verified.
- **D-018 capture integrity: PASS.** `source-001.md` (57 lines, frozen at c123b5e) ↔ 70 requirements: 12 rows spot-checked forward all trace verbatim to their `source_ref` paragraphs; 8 reverse probes (M0-T069 preservation, UNMEASURED, R060, agent_supervisor, symlink, two-writer, --max-bytes, hermetic fixtures, owner bundle) all have rows. Classes: 49 obligation / 11 prohibition / 8 harness / 1 hold / 1 return. **Evidence map: 63 rows == the 63 mechanically applicable IDs (`evaluate_task_refs` ok=true), missing [], extra []** — exactly as required. D-018 `verification.json` is honestly capture-only pending the independent verifier (correct pre-accept state).
- **No NYC app logic:** benchmark/e2e `services/api/*` fixtures exist only inside `tempfile.TemporaryDirectory()` repos; no `services/`/`apps/` diff.

## Findings

**BLOCKING (required correction, administrative — before accept):**
1. `tools/context_pack_evidence.py` is outside the packet's `allowed_paths` while being a production deliverable of the task (and the producer report claims allowed_paths-only). Amend the packet (orchestrator), re-verify applicability (already dry-run clean: 63/63, delta empty). No code change needed.

**Observations (non-blocking; suggest follow-up tasks, never reopening accepted work):**
1. Seed crowding: `MAX_SEEDS = 5` takes the first 5 of the alphabetically sorted candidate set, so in this dirty-tree run the control-plane/docs paths displaced all 4 implementation paths from graph seeding (all 5 graph queries unresolved; code evidence still resolved via source excerpts, and the e2e fixtures prove graph resolution works). Prioritizing implementation paths before control-plane paths would strengthen real-repo packs.
2. Pre-existing `SingleWriterLock.acquire()` stale-reclaim TOCTOU (unchanged accepted A2 code): between `mkdir` and `owner.json` write, a competing acquirer reading empty metadata computes aged=True/pid=-1 and could reclaim a live lock. Microsecond window; suggest atomic dir-rename acquisition in a follow-up.
3. `PathContainmentError.detail` echoes the caller-supplied string (truncated to 120 chars); a caller-supplied absolute `--include` is therefore echoed into the packet's omission reason. Resolved/private paths never leak (asserted by tests and my probes); the design docstring states this intentionally. Also, packets faithfully reproduce absolute `worktree` fields already present in authoritative control-plane content (task packet, handoff) — content fidelity, not a containment leak; noted because D-018-R034's sentence reads broadly.
4. Whole-tree `ruff check .` reports 53 pre-existing errors, all in files untouched by this task (agent_supervisor, test_directive_compliance, directive_registry, etc.); changed files are clean.
5. Committed e2e report's `integrated_sources` counts (18/17) differ from a dirty-tree rerun (18/19) — environmental; the pass predicates derive from the missing-source set and reproduce exactly.

## Verdict

**PASS** — all 8 directive proofs independently reproduced; scope otherwise clean, forbidden diff empty, CI purely additive, M0-T069 preserved, no promotion/behavior-flag change — conditioned on the one BLOCKING administrative correction (add `tools/context_pack_evidence.py` to the packet's `allowed_paths` and re-run the applicability dry-run) being applied and validated before acceptance.


---

# M0-T075 independent review — correction attestation — PASS

> Saved VERBATIM by the orchestrator from the same reviewer's agent-return
> channel (transport entity-decoding only). Delta attestation at the
> corrected HEAD db82e0a.

**Reviewed HEAD:** `db82e0abb86aa6fe5e2858a29978315a553c881c` (worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m0t064` confirmed; commit "M0-T075: apply required review correction - context_pack_evidence.py added to packet allowed_paths", parent = my reviewed `df2468d`).

**(a) HEAD confirmed:** `git rev-parse HEAD` = `db82e0abb86aa6fe5e2858a29978315a553c881c`.

**(b) Delta is control-plane-only.** `git diff df2468d..db82e0a --name-only` = exactly 4 files:
- `project-control/reports/M0-T075-review-PASS.md` (saved verbatim review report)
- `project-control/reports/M0-T075.json` (submission record)
- `project-control/state.json` (lifecycle bookkeeping)
- `project-control/tasks/M0-T075.json` (packet amendment)

No tools/, docs/, or `.github/` file changed — every code/doc/CI artifact I reviewed and every proof I reproduced at `df2468d` is byte-identical at `db82e0a`. (Working tree additionally carries only post-HEAD orchestrator bookkeeping: `progress_log`/`updated_at` in the packet plus state/submission records; zero non-control-plane dirty files.)

**(c) Correction verified.** The committed packet at `db82e0a` has **44 allowed_paths** and `tools/context_pack_evidence.py` is present (working copy identical in `allowed_paths`). Applicability dry-run re-run at this HEAD: `directive_registry.evaluate_task_refs` -> `ok: true`, **63 applicable**, evidence-map coverage **missing [] / extra []** — unchanged from my original review, as predicted by my dry-run.

**(d) Verdict.** The single BLOCKING administrative finding is **closed**. My observations (seed-ordering, pre-existing lock-reclaim TOCTOU, supplied-string echo, pre-existing whole-tree ruff noise, e2e source-count environment variance) remain non-blocking follow-up candidates and do not condition the verdict.

**FINAL: PASS — unconditional at db82e0abb86aa6fe5e2858a29978315a553c881c.**
