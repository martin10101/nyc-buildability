# M0-T076 — Producer requirement-to-counterexample matrix (D-019-R006)

For every requirement carrying absolute language (every / never / atomic / same /
complete / exact / cannot / must-be-impossible), the most likely counterexample was
stated and EXECUTED. Commands were run from the branch worktree and, for the
clean-checkout proofs, from a fresh clone pinned to the branch head. Test counts and
exits are recorded below.

Baseline (pre-change, clean clone @ `3c10894`): the five blockers reproduced (see
`M0-T076-G0-readiness.md`). Post-change full context-pipeline suite: **252 passed,
1 skipped** (env-gated symlink test). Modularity: 0 failures. Directive validator:
exit 0.

| # | Requirement (absolute) | Counterexample attempted | Command / probe | Exit / result | Verdict |
|---|---|---|---|---|---|
| A1 | R015 "metadata **complete before** public lock visible" | Peer observes an owner-less `writer.lock` (the former publication window) | `test_owner_less_publication_window_is_never_reclaimed` | refuses `concurrent_writer`; lock untouched | HOLDS |
| A2 | R016 "**every** owner has an unguessable token" | Two acquisitions reuse/guess a token | `test_unguessable_token_and_token_matched_release` | tokens differ, ≥32 hex chars | HOLDS |
| A3 | R017 "stale takeover uses an **atomic** move" | Two reclaimers race the same stale lock | direct `_atomic_quarantine_stale` race probe | exactly one wins; lock moved away | HOLDS |
| A4 | R018 "missing/partial metadata **cannot** reclaim a live lock" | Young owner-less / partial-owner lock reclaimed | `test_partial_metadata_is_never_reclaimed` | refuses `concurrent_writer` | HOLDS |
| A5 | R019 "release removes the lock **only** when the token matches" | A superseded owner releases and deletes the successor's lock | `test_unguessable_token_and_token_matched_release` | successor lock survives | HOLDS |
| A6 | R021 both-promoted/one-lost "**must be impossible**" | Two valid writers, forced interleave | `test_two_valid_writers_no_lost_node` + store-level probe | both nodes survive (2 nodes) | HOLDS |
| B1 | R023 absolute/traversal "**never** read" | `--ci-summary <abs>`, `--include <abs>`, `--include ../../etc/passwd` | `D019ContainmentRedactionInsufficiency` (3 tests) | exit 3; marker never read | HOLDS |
| B2 | R024 "**must not** repeat a supplied private absolute path" | Grep packet/streams for the supplied absolute path | same, + meta `generated_from` inspection | absolute path absent; `[redacted:non_canonical_path]` | HOLDS |
| B3 | R025 refused explicit request "marker content **absent** from context.md, metadata, evidence, stdout, stderr" + nonzero | Scan every packet file + streams for the unique marker | `test_absolute_ci_summary_refused_no_leak` | exit 3; marker absent everywhere | HOLDS |
| B4 | Raced escaping link "refuse" (proof 3) | Junction to outside materialized before the read | `test_link_present_at_read_time_refuses` | `path_escapes_repository`; no leak | HOLDS (skips only if OS forbids links) |
| C1 | R026 "**not silently** HEAD for active reviewer" | Committed reviewer packet with default base | `test_committed_change_visible_against_frozen_base` | resolves `frozen_g0_gate_sha`, ≠ HEAD | HOLDS |
| C2 | R028 "worker/reviewer packets **must still** contain committed hunks" | Diff a committed change against the frozen base | same test | committed hunk present; empty vs HEAD | HOLDS |
| C3 | R026 no-frozen-base | No G0 gate + no explicit base | `test_no_frozen_base_refuses_instead_of_head` | refuses (`unresolved_require_explicit`) | HOLDS |
| D1 | R029 "consume **actual** Unit E … not 'Unit E-class'" | Prove the compiler only *imports* a module | `test_compiler_neighborhood_calls_unit_e_primitive` (spy on `rv.neighborhood_edges`) | spy called once; real call path | HOLDS |
| D2 | R030 deterministic seed order | Docs/control-plane paths sort alphabetically first | `test_seed_order_impl_before_docs_control_plane` | impl always precedes docs | HOLDS |
| D3 | R031 "clean M0-T066 … **before** documentation consume the five-seed cap" | Clean-checkout M0-T066 compile | clean-clone `context_pack.py --task M0-T066` | 4 `allowed_impl` + 1 prose; no docs/control-plane in cap | HOLDS |
| D4 | R031 "**avoid duplicate** source/test excerpts" | A file that is both impl and its own test | clean M0-T066 excerpt/test disjointness | excerpts ∩ tests = ∅ | HOLDS |
| E1 | R032 "**never silently** false for unknown … impact" | A code task with undetermined concurrency | `test_concurrency_task_never_false_without_ambiguity` | undetermined → ambiguity raised | HOLDS |
| E2 | R033 concurrency "**cannot** emerge …=false with no ambiguity" | Force a sufficient concurrency task | same test | `not (concurrency False and ambiguity False)` | HOLDS |
| E3 | R032 "**every** field derived or undetermined" | Enumerate signal provenance | `test_every_signal_has_a_basis` | every risk field has a basis | HOLDS |
| F1 | R034 "bounded useful fields … **never** substitutes for source" | A real promoted digest's advisory row | `test_advisory_digest_contributes_useful_bounded_fields` + `_is_bounded` | note/reqs/files/evidence/source present, bounded, advisory | HOLDS |
| G1 | R036 "exact command **exits 0 twice** from independent clean checkouts" | Run the documented e2e twice from a clean clone | clean-clone `--e2e --baseline M0-T076-baseline-g0.json` ×2 | exit 0, exit 0 | HOLDS |
| G2 | R036 "no worse … **not only** source-ID counts" | Inject an evidence regression into the fingerprint | `test_no_worse_compares_required_evidence_not_counts` | regression detected on required evidence | HOLDS |
| G3 | R037 "add … to **permanent CI**" | Confirm additive CI step | `.github/workflows/ci.yml` context-pipeline job | e2e step added; no job removed | HOLDS |
| X1 | R011 "**Do not** remove/skip/weaken any existing test" | Diff test files for deletions/skips | `git diff <base> -- tools/test_*.py` | 0 removed defs, 23 added, 0 new skips | HOLDS |
| X2 | Proof 9 "status projection **still** catches uncommitted changes" | Confirm no regression | `test_status_projection.py` (unchanged module) | staleness tests pass; module unchanged | HOLDS |
| X3 | Proof 11 "expanded index parity **remains byte-identical**" | Rerun index benchmark | `context_benchmark.py --samples 2` | all R059 integrity checks True | HOLDS |
| X4 | Proof 12 "**all** pre-existing suites remain green" | Run all 14 context-pipeline suites | `pytest` (14 files) | 252 passed, 1 skipped | HOLDS |

## Absolute-language coverage note
Governance/return rows (R001–R014) are process obligations verified through the
lifecycle (reconciliation record, this matrix, the fresh adversarial review, DCV,
gates, and the final return), not code probes; they carry no code counterexample.
`tools/model_routing.py` and every protected surface were left byte-unchanged
(forbidden-path diff empty — see the producer report).
