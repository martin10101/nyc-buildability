# M0-T065 Unit B — coverage, determinism & budget-contract evidence (D-013)

## Determinism (same source state + args → byte-identical)
- `test_context_pack.py::TestDeterminism.test_determinism_byte_identical` — cold vs
  warm build produce byte-identical `context.md` AND `context.meta.json`.
- `test_context_pack.py::...summarized_fixpoint` — determinism holds across the
  footer-aware summarized fixpoint.
- `test_context_pack_index.py::AS6_Determinism` — determinism holds WITH index
  consumption (a content edit, then build twice; md + meta byte-identical).
- Why it holds: the pack embeds only source-identity provenance
  (`source_manifest_digest`, `export_digest`, HEAD/branch, census, versions) — all
  invariant to the pack's own `--out` output and to cache state. The volatile
  snapshot fingerprint + dirty digest (which include the out/ dir when written
  in-repo) and cache-state fields (mode/hit-miss/files-parsed) are recorded ONLY
  in the external run-record JSONL, never in the deterministic artifact.

## Budget contract preserved (drift-lock intact)
- `test_context_pack.py::TestBudgetDriftLock` (constants / estimate / effective
  ceiling) still passes: the four `DEFAULT_*` constants and `estimate_tokens` /
  `effective_ceiling_tokens` are byte-equal to `tools/agent_supervisor/
  review_packet.py`. The adaptive tier is a SEPARATE section that never touches
  them (`amendment.changes_constants == false`).
- The hard ceiling remains `min(ordinary_ceiling, relative_ceiling)`; the tier only
  sets the TARGET. AS-5 confirms overflow still refuses-or-splits against the
  unchanged ceiling; AS-2 confirms `hard_ceiling_unchanged == true`.

## One total budget (R039)
- `AS1_SingleBudget`: `budget.single_total_budget == true`; a single
  `effective_bound_bytes` across all sources; no per-source budget fields.

## Adaptive tier honesty (R041/R042)
- `AS2_NormalTier`: low breadth → normal tier, target ∈ [5000, 8000].
- `AS3_MediumJustification`: high breadth without a justification does NOT raise the
  target above normal (withheld larger target recorded); WITH a justification the
  medium target is granted and never exceeds the accepted 32,000.

## Coverage/provenance (R040/R024/R002/R058)
- `AS4_CensusProvenance`: meta carries `source_manifest_digest`, `export_digest`,
  HEAD/branch, `census` (with `reconciles == true`), versions, `coverage_mode`,
  `dependency_breadth`; a `repo_census` source is present; the code-graph
  neighborhoods carry `graph_queries` parameters.

## Refuse-or-split, fail-safe (R003/R013/R040)
- `AS5_RefuseOrSplit`: a large material `--include` under a tiny `--max-bytes` →
  exit 2, `overflow.resolved == "split_required"`, material preserved under
  `evidence/`, effective bound ≤ max_bytes (ceiling never relaxed by the tier).
- `NoIndexEscapeHatch`: `--no-index` degrades to a recorded coverage omission
  (`coverage_mode == "disabled"`), never a crash or a silent gap.

## Modularity (permanent law)
- 6 focused modules + a facade, all < 600 SLOC; `modularity_check --check` → 0
  failures. Public imports preserved via the facade; the existing suite (incl. the
  drift-lock) passes unchanged — extract-first behavior preservation confirmed.
