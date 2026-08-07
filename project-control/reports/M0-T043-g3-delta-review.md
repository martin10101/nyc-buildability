# G3 DELTA Re-Review — M0-T043 Bounded context-pack builder (rework 1)

- Task: M0-T043 "Bounded context-pack builder (AD-044..AD-046; 0A.4 budgets)"
- Reviewed worktree: `C:/Users/MLFLL/Downloads/nyc-zoning/orch`, branch `task/M0-T043-context-pack`
- Reviewed content SHA (producer rework): `e41dad3` (`reviewed_sha` in `M0-T043.json`); worktree HEAD `52c3813`
- Later commits `e41dad3..HEAD` verified control-plane only (`git diff --name-status` = `project-control/reports/M0-T043.json`, `state.json`, `tasks/M0-T043.json`) — no code/doc drift
- Producer rework commit `e41dad3` in isolation (`git diff --name-status e41dad3^ e41dad3`) touched only: `docs/CONTEXT_PACKS.md`, `tools/context_pack.py`, `tools/test_context_pack.py`, and its own `project-control/reports/M0-T043-producer-report.md`
- Reviewer: code-reviewer (read-only). Producer ≠ reviewer.
- Delta scope: F1 fix correctness, regression risk of the rewrite, new-test genuineness, F2–F6 dispositions, scope discipline. Unchanged first-pass PASSes not re-litigated.

## Verdict: PASS

The MAJOR F1 defect (footer-blind bound decision → exit-0 over-bound packets) is genuinely fixed at all three decision points, verified by independent reproduction inside the old blind window. F2/F3 fixed; F4/F5/F6 advisories fixed. The rewrite preserves determinism, digest-over-rendered-bytes provenance, and AD-046 material integrity. No new blocking findings.

## Reproduction environment
- Python 3.11.9.
- `python tools/test_context_pack.py` → "Ran 15 tests … OK" (14.9s); rerun → "Ran 15 tests … OK" (15.1s) — no flake. Test count 13→15 as claimed.
- `python -m pytest -q tools/test_context_pack.py` → "15 passed" (13.9s).
- All three drift-lock tests RAN (not skipped): `test_drift_constants_equal`, `test_drift_effective_ceiling_equal`, `test_drift_estimate_equal` = ok.
- Live CLI reproductions written only to the session scratchpad; no repo file modified.

## F1 fix — traced and independently reproduced (FIXED)

New `_finalize_md(header, sources, digests, truncations, footer_fn)` renders `context.md` and iterates the footer's self-referential byte/token count to a fixpoint (cap 8 iterations). `_footer_for(...)` / `_emitted_bytes(...)` in `build()` render the REAL footer (default exclusions + conditional omissions, role sufficiency, overflow block reflecting the candidate resolution) and are used at all three decision points:

1. Initial within-bound: `full_bytes = _emitted_bytes(digests, {}, overflow=within_bound)` (context_pack.py:707)
2. Post-summarize re-check: `after_bytes = _emitted_bytes(digests, truncations, overflow=summarized)` (context_pack.py:731)
3. Split trigger: `after_bytes > effective_bound_bytes` → `split_required` → exit 2 (context_pack.py:733–738)

`emit()` (context_pack.py:963–969) renders the non-split path through the SAME `_finalize_md` with `result["final_digests"]`, `result["truncations"]`, `result["overflow"]` — which are byte-for-byte the inputs `build()` decided against (`final_digests` recomputed from the same `content_rendered`; the footer reads only `omissions`/`sufficiency`/`triggered`/`resolved`/`actual_bytes`/`estimated`/`effective_bound_bytes`, all identical between the `partial` dict used in `build()` and `result` used in `emit()`). Therefore the size the bound was enforced against == the size written. `_make_footer_two_pass` deleted; `emit()` no longer uses `"PLACEHOLDER_FOOTER"`.

Termination/determinism: footer length is a non-decreasing step function of `total` (digit-width of `actual_bytes` and of `estimated = ceil(total/bpt)`, both non-decreasing; header bound values are fixed and do not depend on `total`). Iterating from `total=0` gives a monotone, bounded, integer sequence → it stabilizes (no oscillation possible); observed convergence in ≤3 iterations, well under the cap of 8. `actual_bytes` returned = `len(md)`, so `meta.actuals.context_md_bytes` equals the real file size (verified: b16000 meta `context_md_bytes=15459`, `wc -c`=15459). Meta honesty preserved.

Independent reproduction (live CLI on the real repo, worker role, 200k window; natural `context.md` = 17959 B):

```
bound    exit  emitted  resolved      within_eff_bound
17958    0     17956    within_bound  true    (17956 <= 17958)
17900    0     15459    summarized    true    (15459 <= 17900)
17000    0     15459    summarized    true
16500    0     15459    summarized    true
16000    0     15459    summarized    true    <-- G4 D-1 repro: was 17097 > 16000 exit0
15500    0     15459    summarized    true    (41 B under; deepest exit-0 in blind window)
15000    2     2370     split_required  (fail-closed diagnostic; exempt)
12000    2     ...      split_required
 9000    2     ...      split_required
```

At the G4 D-1 exact repro (`--max-bytes 16000`) the emitted file is now 15459 ≤ 16000 at exit 0 (`within_effective_bound=true`); previously it was 17097 > 16000 at exit 0. Across the entire old blind window (bounds just below natural down to ~15500) the tool either summarizes to ≤ bound at exit 0 or fails closed at exit 2 — no exit-0-over-bound observed at any swept bound. The G3-cited window (3653..5053 on the old 5253-byte fixture) corresponds to this behavior. Both decision points confirmed footer-aware from meta: b17958 → `resolved=within_bound, triggered=false`; b15500 → `resolved=summarized, triggered=true`.

Residual-path check: (a) split-report path is exit 2, exempt and documented; (b) summarize does not add omission entries post-decision — summarization writes to `truncations`/`content_rendered` (captured before `after_bytes`), never to `omissions`; (c) the byte bound is a pure integer byte comparison (`effective_bound_bytes = min(max_bytes, int(ceiling_tokens*bpt))`), so no byte→token rounding hole in the enforcement decision. No residual exit-0 over-bound path found.

## Regression risk of the rewrite
- Determinism preserved: repo_sha is the only time anchor; sources sorted by `sort_key`, omissions sorted by category, exclusions fixed order. `test_determinism_byte_identical` and the new `test_determinism_byte_identical_summarized_fixpoint` (which asserts `resolved=="summarized"` first, then byte-identical) both pass.
- Provenance preserved: `_write_evidence` still writes `content_rendered`; `final_digests` = sha256 over `content_rendered`; summarized sources still preserve the full original (`.orig`) with `original_sha256`. AS-1 digest test passes.
- AD-046 untouched: summarize loop still guards `if not src.material`; material never reduced; oversize material → exit 2 with full material in evidence. `test_as3_material_never_silently_truncated_failclosed` passes.

## New tests — genuine, non-vacuous
- `assert_bound_invariant()` (test_context_pack.py:144): on exit 0 asserts `emitted <= effective_bound_bytes` AND `within_effective_bound` AND `resolved ∈ {within_bound, summarized}`; on non-zero asserts `exit==2` and `resolved=="split_required"`. Reads the REAL file size (`os.path.getsize`), not the self-reported meta number — genuinely proves the contract.
- `test_as3_bound_boundary_never_over_bound_exit0`: sweeps bounds INSIDE the old blind window (`natural-1, -40, -200, -900, -1500`, plus `natural//2`, `natural//4`), asserts `assert_bound_invariant` at each, and on exit 0 additionally asserts `md_bytes(out) <= bound`. Requires `saw_exit2` (fail-closed hit) so the fail-closed path is exercised. Directly probes the region where the old bug produced exit-0-over-bound.
- `test_as3_summarize` now adds `assert_bound_invariant` + `assertLessEqual(md_bytes, 9000)` on the summarize path.
- `test_as1` adds `assert_bound_invariant` on the within-bound path.
- Vacuity: all assertions execute (confirmed by suite passing with real file sizes); the boundary test's `saw_exit2` guard prevents an all-trivially-passing sweep.

## Per-finding disposition

| Finding | Sev | Disposition | Evidence |
|---|---|---|---|
| F1 footer-blind bound decision | MAJOR | FIXED | `_finalize_md`/`_emitted_bytes` at all 3 decision points; emit renders identical inputs; live sweep shows exit-0 always ≤ bound, G4 16000 repro now 15459 ≤ 16000; fixpoint monotone-convergent + deterministic (build-twice byte-identical). |
| F2 drift-lock skips on import failure | MINOR | FIXED | `_import_review_packet` now `self.fail(...)` not `self.skipTest(...)` (test:447); 3/3 drift tests RAN in my run. |
| F3 dead split branch in `_make_footer` | MINOR | FIXED | split branch removed; replaced with explanatory comment (context_pack.py:827–829); split renders only via `_render_split_report`. |
| F4 code-graph runs without `--no-regen` | ADVISORY | FIXED | `_run_graph_query` passes `--no-regen` before subcommand (context_pack.py:389–391); flag exists as top-level arg in `tools/code_graph/query.py:407` and is read at `:445` — placement valid. |
| F5 `content_rendered` unset in `__init__` | ADVISORY | FIXED | `self.content_rendered = content` initialized in `Source.__init__` (context_pack.py:207). |
| F6 misc (`rc_names`, `ensure_ascii`, `_safe_name` collision) | ADVISORY | FIXED | `rc_names`→`_` (:262); split report `json.dumps(..., ensure_ascii=False)` (:989); `_make_footer` no longer dumps JSON; `_safe_name` appends deterministic `sha256(sid)[:8]` when a separator is flattened (:847–848), applied consistently across evidence path / write / summarize artifact / split report — injective and determinism-preserving. |

## Requirement row (updated)

| Req | First-pass | Delta verdict | Evidence |
|---|---|---|---|
| D-010-R085 (enforce §0A.4 ceilings) | FAIL | PASS | Footer-aware fixpoint makes the emitted `context.md` (footer included) ≤ effective byte bound whenever exit 0; drift-lock constants/estimate/effective-ceiling still equal the real `agent_supervisor/review_packet.py` (3/3 drift tests pass); new boundary test proves the contract inside the old blind window. |

Other rows (R044/R045/R046/R093/R116/R117) remain PASS — not touched by the rework except in ways re-verified above (digest provenance, material integrity, shadow-only scope, stdlib-only).

## Scope & cross-cutting
- Producer rework commit `e41dad3` changed only `tools/context_pack.py`, `tools/test_context_pack.py`, `docs/CONTEXT_PACKS.md`, and its own producer report. No `tools/agent_supervisor/`, `.github/`, `.claude/`, `apps/`, or `services/` edits. Shadow-only preserved.
- Stdlib-only maintained: imports are argparse, hashlib, json, math, os, subprocess, sys (tests add tempfile/unittest). No new dependencies, no lockfile/manifest change.
- Docs (`CONTEXT_PACKS.md`) accurately document the new exit-0 byte-bound guarantee and footer-inclusive enforcement; no scope creep.

## New findings
- None blocking. Two informational notes: (N1) `_finalize_md` caps at 8 iterations — unreachable given proven monotone-bounded convergence (≤3 observed); in the impossible non-convergence case `actual_bytes` still equals the real `len(md)` and build/emit run identical sequences, so no decision/emit divergence. (N2) the exit-2 split report remains unbounded — pre-existing, documented as exempt (a diagnostic, not the work packet). Neither requires action.

## Recommendation
PASS. F1 fixed and independently verified; F2–F6 addressed; no regressions; scope clean. The prior worst-of rework driver (G3 F1 / G4 D-1) is resolved.
