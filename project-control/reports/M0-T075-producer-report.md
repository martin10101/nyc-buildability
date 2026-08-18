# M0-T075 producer report — context pipeline end-to-end integration (D-018)

Producer: orchestrator (sole writer, wt-m0t064, branch
`task/M0-T075-context-integration` — the ONE branch of the ONE corrective
task). Base: accepted main c123b5e. The D-018 capture (70 requirements) and
the full packet contract ride this same branch/PR.

## What was built (allowed_paths only)

1. **`tools/context_paths.py`** — THE shared canonical-path + real-path
   containment rule (R031..R034), adopted by compiler `--include`/contract/
   excerpt reads, deep views, view seeds/cards, ontology inputs, and memory
   evidence digests. Junction/symlink escapes refuse; no error ever carries
   a private absolute path.
2. **Integrated compiler** (`context_pack_evidence.py` + wiring through
   sources/assembly/render/index): exact applicable requirement IDs AND
   texts (deterministic `ALL` resolution), real-path graph seeding (prose
   only via the strict extractor, every candidate recorded), reopened
   source/test excerpts, bounded Unit C ontology, explicitly ADVISORY Unit D
   memory, all under the unchanged single budget with full provenance —
   and ENFORCEABLE role sufficiency: insufficient → bounded meta + exit 3;
   over-budget split → exit 2 (preserved). Public facade + CLI unchanged.
3. **`tools/context_orchestrate.py`** — the canonical orchestrator-facing
   entry point (outside protected paths) that invokes the integrated
   compiler, derives `model_routing.Signals` from compiled evidence (missing
   evidence → ambiguity, never silent LOW), emits `dispatch_manifest.json`,
   records the decision via the accepted rotated runtime JSONL, and states
   the OWNER-GATED supervisor boundary honestly.
4. **Memory-graph transaction fix** — the single-writer span now covers
   load-current → conflict check → mutation → validation → promotion
   (`write_generation_locked`), with explicit `concurrent_writer` + retries;
   the exact two-writer stale-read/lost-update regression is on file and a
   lost node is structurally impossible.
5. **Real retention** — generation `prune` invoked on every index build and
   inside the memory transaction (current + rollback preserved, lock-
   serialized); telemetry + routing JSONL bounded/rotated.
6. **Extended benchmark** — G0 baseline captured pre-change; 42 index cases
   retained; distinct parser-version case via the real invalidator path;
   lock/orphan/parser folded into the R059 predicates; nearest-rank p95;
   NEW e2e corpus invoking the ACTUAL compiler across the five shapes
   (all checks true; representative-task correctness no worse than baseline:
   8 → 18/17 sources, none missing). Provider savings UNMEASURED.
7. **Projection repair** — deterministic input-manifest digest over every
   material input; uncommitted control-plane edits stale the snapshot with
   HEAD unchanged; full status map incl. `self_check`/`canceled`;
   generated-current vs committed-snapshot distinction.
8. **Runbook + CI + records** — runbook rewritten around the one canonical
   compiler with all 13 commands smoke-tested (incl. `--max-bytes`); ONE
   additive `context-pipeline` CI job (pure insertion); the honest
   `M0-T069-benchmark-scope-correction.md` (index-parity scope preserved,
   never disputed); doc corrections appended to the four pipeline docs.

## Reconciliation + baseline discipline (R002/R004/R039)

Live reconciliation preceded every edit (clean main == origin c123b5e,
97 accepted, M0-T075 free, no overlapping PR, validator exit 0) and the G0
baseline was captured from accepted code BEFORE the first behavior change
(`M0-T075-baseline-g0.json` — it honestly records the pre-integration gap:
8 generic sources, no requirement texts, no excerpts, no resolved seeds).

## Self-check results (documented_test_commands)

- `python tools/test_context_integration.py` → **11 OK** (two-writer race,
  containment probes incl. junction, real-task proofs, entry point,
  retention).
- `python tools/test_context_pack.py` → **15 OK**;
  `test_context_pack_index.py` → **8 OK** (drift-lock intact).
- `test_subsystem_resolver.py` **21 OK** · `test_memory_graph.py` **31 OK** ·
  `test_repo_views.py` **26 OK** · `test_context_benchmark.py` **19 OK** ·
  `test_status_projection.py` **11 OK** · `test_repo_index_cache.py` OK ·
  (`test_repo_index_incremental.py` **25 OK**).
- `python tools/modularity_check.py --check` → **failures 0**.
- `validate_directive_compliance.py` → exit 0 (18 directives).
- e2e benchmark → **exit 0**, all checks true, no-worse-than-baseline.
- All 13 runbook commands executed as written.

## Modularity note (warn band, justification recorded)

`tools/context_benchmark.py` entered the 600-SLOC warn band (review_signal,
0 failures): the e2e mode deliberately lives beside the index-parity mode
because both consume the SAME frozen corpus generators, git fixtures, and
manifest digests — splitting them would duplicate the corpus or create a
shared-fixture module used by exactly two siblings. Cohesion: one module =
one benchmark boundary (corpus + both measurement modes). If a third mode
ever appears, extract the corpus into its own module first.

## Scope compliance

Diff touches ONLY allowed_paths + the packet's own control-plane records and
the D-018 capture. Protected surfaces untouched: `tools/agent_supervisor/`,
code-graph builders, fingerprint/assembly/baseline, `model_routing.py`,
modularity tooling, `services/ apps/ packages/ supabase/ .claude/` — and no
behavior flag, promotion state, or history changed. The owner-gated items
(controller bundle, live probe, D-013-R060 promotion) were NOT executed.

Evidence: `M0-T075-coverage-evidence.md`; per-requirement map:
`M0-T075-evidence-map.json` (63/63 mechanical match); benchmark evidence:
`M0-T075-baseline-g0.json` + `M0-T075-e2e-benchmark-report.{json,md}`.
