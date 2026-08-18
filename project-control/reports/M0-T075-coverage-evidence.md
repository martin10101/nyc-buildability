# M0-T075 — vertical-integration evidence (D-018)

## The gap this task closed (recorded honestly at G0)
The pre-change baseline (`M0-T075-baseline-g0.json`, captured from accepted
code BEFORE any edit) shows the accepted compiler included only 8 generic
sources per pack — NO requirement texts, NO reopened source excerpts, NO
resolved graph seeds (prose-output seeds all unresolved) — while reporting
sufficiency true. Every D-018 correction below is verified by executable
tests plus a live compile of the real accepted task M0-T066.

## Integrated compiler (R008..R018 / AS-1)
- Real-task compile (M0-T066): 12 source groups incl. `requirements`
  (24 exact IDs+texts via deterministic registry resolution),
  `source_excerpts` (4 implementation sources + 3 tests, contained reads,
  per-file sha256), `ontology` (Unit C placements + version stamp),
  `memory_advisory` (honest `store_empty`); seeds from changed +
  implementation paths only; every prose candidate recorded
  resolved/unresolved; unresolved seeds listed; single budget unchanged
  (drift-lock suites green).
- Baseline comparison: integrated packs carry 18/17 sources vs baseline 8
  with ZERO baseline sources missing (`no_worse_than_baseline: true`).

## Enforceable sufficiency (R014/R019/R021 / AS-2)
- In-regime requirement failure, missing groups, or code-evidence-without-
  resolution → bounded meta + **exit 3** (suite + e2e `reviewer_insufficiency
  _exit==3`); split refusal unchanged (**exit 2**, e2e tiny-budget case).

## Memory transaction + two-writer regression (R027..R030 / AS-3)
- The promotion span holds the single-writer lock from load-current through
  generation promotion (`write_generation_locked`); `Proof3TwoWriterRace`
  reproduces the exact stale-read interleave: the interleaved writer gets
  the explicit `concurrent_writer` refusal, succeeds on retry, and BOTH
  nodes survive (a lost update is structurally impossible).

## One containment rule (R031..R034 / AS-4)
- `tools/context_paths.py` adopted by --include, contracts, excerpts, deep
  views, view seeds/cards, ontology inputs, memory evidence digests.
- Probes: absolute, drive, `.`/`..`, doubled separators, backslash, and a
  REAL junction/symlink whose target leaves the checkout — every refusal
  machine-readable with zero private-path leakage (asserted).

## Projection staleness (R048..R050 / AS-5)
- Deterministic input-manifest digest over every consumed control-plane file
  + index digests + git identity; `check` regenerates live: an UNCOMMITTED
  task-status edit stales the snapshot (exit 3) with HEAD unchanged (test).
- `self_check` → "gates pending", `canceled` → "superseded";
  `generated_current` vs committed-snapshot note explicit.

## Entry point + grounded routing (R022..R026 / AS-6)
- `context_orchestrate.py` executes the INTEGRATED compiler (Proof7 asserts
  the integrated meta) and derives Signals from compiled evidence; missing
  evidence → `ambiguity_or_missing_evidence` with notes (never silent LOW);
  bounded `dispatch_manifest.json`; decision recorded via the accepted
  rotated runtime JSONL; supervisor boundary stated OWNER-GATED.

## Benchmark (R038..R047 / AS-7)
- Baseline captured pre-change; 42 index cases retained (suite asserts the
  full case set); NEW distinct `parser_version_change` case through the REAL
  invalidator path; lock/orphan/parser folded into the R059 predicates;
  nearest-rank p95 (n=3 → max, n=20 → rank 19); e2e corpus: five shapes
  through the ACTUAL compiler — all checks true, exit 0; provider savings
  UNMEASURED preserved.

## Retention real (R035..R037 / AS-8)
- `prune` invoked on every index build (lock-serialized) and inside the
  memory transaction; current + rollback generations preserved (test);
  telemetry + routing JSONL rotated with a bounded live file (test);
  runtime state external; redaction unchanged.

## CI + runbook (R051..R054 / AS-9)
- ONE additive `context-pipeline` job (pure +29-line insertion) running the
  complete Units B–F suites + the integration/adversarial suite; no existing
  job touched.
- Runbook rewritten around the one canonical compiler; ALL 13 commands
  smoke-tested as written (incl. the required `--max-bytes`); owner-gated
  supervisor boundary stated.

## Full battery at submit (local, Python 3.11.9, ruff 0.13.0 = CI version)
- test_context_integration 11 OK · test_context_pack 15 OK ·
  test_context_pack_index 8 OK · test_subsystem_resolver 21 OK ·
  test_memory_graph 31 OK · test_repo_views 26 OK ·
  test_context_benchmark 19 OK · test_status_projection 11 OK ·
  test_repo_index_cache OK · test_repo_index_incremental 25 OK ·
  test_repo_fingerprint/assembly/baseline OK · ruff clean ·
  modularity --check failures 0 · validate_directive_compliance exit 0.
- e2e benchmark exit 0 (all checks true; no-worse-than-baseline).
