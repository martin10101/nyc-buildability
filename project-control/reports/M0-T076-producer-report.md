# M0-T076 — Producer report (D-019)

**Task:** M0-T076 — Context pipeline promotion-blocker closure and adversarial
completion protocol. **Directive:** D-019 (active, owner-authorized).
**Branch:** `task/M0-T076-context-blocker-closure`. **Producer:** orchestrator.
**G0 base (frozen):** `3c108944f6b1abf23866351c696e7f09562ea498`.

One task, one branch, one PR. No rebuild. No NYC application work, controller
change, or promotion. D-013-R060 remains PENDING for the owner.

## Blockers closed (each reproduced pre-change, then fixed + regression-tested)

**A — SingleWriterLock publication/reclaim race (R015–R021).**
`tools/repo_index_cache.py`: the lock is now published by building a
fully-populated staging directory (owner metadata + an unguessable
`secrets.token_hex(16)`) and atomically `os.rename`-ing it onto `writer.lock`, so
the lock is only ever observed WITH complete metadata. A peer treats a present
lock as live unless ownership is complete AND provably abandoned (dead pid + aged),
or the directory itself has aged past the timeout; a young owner-less/partial lock
(the former publication window) is never reclaimed. Stale takeover is an atomic
`os.rename` to a unique quarantine name (exactly one racing reclaimer wins).
Release removes the lock only while our token still owns it. The promotion
transaction (`tools/memory_graph.py`) holds this lock across
load→conflict→mutation→validation→promotion→retention. New deterministic
regressions prove the former two-promoted/one-lost schedule keeps both nodes.

**B — Containment + private-path redaction (R022–R025).**
`--ci-summary` now routes through the shared containment rule
(`tools/context_paths.py`) exactly like `--include`; caller-supplied absolute /
traversal strings are redacted (`[redacted:non_canonical_path]`) in every omission
reason, error, and packet-metadata echo (`generated_from` records only accepted
canonical includes). A refused EXPLICIT `--include`/`--ci-summary` now makes the
packet INSUFFICIENT (nonzero) — verified that the marker content is absent from
`context.md`, metadata, evidence files, stdout, and stderr.

**C — Frozen diff base (R026–R028).**
`tools/context_orchestrate.py` resolves and validates the task's frozen G0 reviewed
SHA as the default diff base (explicit `--diff-base` is a trusted override; no
frozen base + no explicit ⇒ refuse, never silent HEAD). The dispatch manifest
records the chosen base SHA, resolution method, current head SHA, dirty/clean
state, and the exact diff command. A committed reviewer packet now contains the
committed hunks against the frozen base (empty against HEAD — the former failure).

**D — True Unit E consumption + seed order (R029–R031).**
Extracted the shared primitive `repo_views.neighborhood_edges` (Unit E) and made
the compiler (`tools/context_pack_index.py`) CONSUME it (traced call, spy-verified)
instead of a reimplemented neighborhood; `neighborhood_view` also consumes it, so
the two cannot drift. Seeds follow a deterministic tier order — changed impl →
allowed impl → graph-derived test/dependent → strict prose → docs/control-plane —
with every selected / skipped-over-cap / refused candidate recorded. A clean
M0-T066 compile seeds its subsystem implementation files before any
docs/control-plane. Source and test excerpts are de-duplicated.

**E — Honest routing (R032/R033).**
`derive_signals` records a per-signal `basis`. Path-derivable signals (security,
protected-config, control-plane, schema, legal) are structured; behavioral risks
(destructive, external-side-effect, concurrency) are affirmed absent ONLY when no
code is in scope, otherwise marked undetermined and raise
`ambiguity_or_missing_evidence`. A concurrency-focused (code) task can never emerge
`concurrency_or_performance=false` with `ambiguity=false`. `tools/model_routing.py`
is byte-unchanged (protected model configuration untouched).

**F — Useful bounded advisory memory (R034).**
`tools/context_pack_evidence.py` advisory rows now carry bounded useful fields
(digest id, outcome+agent, bounded note, requirement ids, file paths, evidence
refs, unresolved/quarantined state, source/repository identity), still explicitly
advisory and reducible under the single global budget; never a substitute for
reopened authoritative source.

**G — Reproducible clean-checkout e2e benchmark (R035–R037).**
`tools/context_benchmark.py`: the baseline comparison is now a frozen,
state-invariant required-evidence + relevance fingerprint over the hermetic shapes
(sufficiency, exit, requirement ids/texts, resolved graph/source evidence,
ontology, advisory-memory handling) — never a working-tree-diff source-id count. A
new clean-captured baseline `project-control/reports/M0-T076-baseline-g0.json`
(`context_benchmark_e2e_baseline/v1`) is committed; the exact documented `--e2e`
command exits 0 twice from independent clean checkouts and now runs in the
permanent `context-pipeline` CI job. Provider token savings remain UNMEASURED.
M0-T075's baseline is unmodified; `M0-T075-reconciliation-correction.md` records
what the earlier dirty-capture "no-worse" result actually demonstrated.

## Verification summary
- Full context-pipeline suite (14 files): **252 passed, 1 skipped** (env-gated
  symlink/junction test). 23 new tests added; **0 existing tests removed, skipped,
  or weakened** (`git diff` verified).
- Modularity check: 0 failures (5 pre-existing warnings; `context_benchmark.py` is
  795 SLOC — a single cohesive benchmark module: corpus shapes + index parity +
  e2e + baseline are one responsibility; splitting would fragment the benchmark).
- Directive validator: exit 0 (19 directives).
- Clean-checkout proofs from a fresh clone @ branch head: e2e exit 0 ×2; clean
  M0-T066 impl-first seeding; forbidden-path diff EMPTY.
- Producer counterexample matrix: `M0-T076-counterexample-matrix.md` (all HOLD).

## Scope confirmation
Changed files are entirely within M0-T076 allowed paths + the D-019 control-plane
records. Forbidden-path diff empty: no `tools/agent_supervisor/**`, no protected
config, no `model_routing.py`, no code-graph generators / fingerprint / baseline /
incremental engines, no `apps|services|packages|supabase`, no `.claude/`. R060
left pending; controller bundle not run; no live probe.
