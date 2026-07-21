<!-- Preserved VERBATIM by the orchestrator from the code-reviewer agent return, 2026-07-21 (transport entity-decoding only: &gt; &lt; &amp; decoded). -->

Both hard invariants independently confirmed with fresh inputs. My review is complete. Here is the gate report.

---

# G3 GATE REPORT — M2-T013 Production spatial-intersection engine

**Reviewer role:** Independent human-style walkthrough (G3), read-only
**Branch / review SHA:** `task/M2-T013-spatial` @ `59dbe65` (matches assignment)
**Verdict: PASS**

## What I did
Read all seven modules (`app/spatial/{engine,geometry,coverage,crosscheck,models,policy,adapter}.py`) and the test pack from acceptance criteria (SI-S1..S12, SI-CF1..CF7), not from the producer report. Reran suites from clean state, verified the two hard invariants in code, hand-traced representative cases, and ran an independent live invariant check with fresh inputs.

## Reproducible evidence (run from `<worktree>/services/api`)
- `python -m pytest tests/spatial -q` → **26 passed** (0.72s)
- `python -m ruff check .` → **All checks passed!**
- `python -m pytest -q` → **564 passed** (12.56s) — regression intact
- `git diff --name-only main...HEAD` → changes confined to `app/spatial/**`, `tests/spatial/**`, `docs/research/M2-T013-*.md`, and orchestrator ledger files. **No** `app/connectors/**`, `app/profile/**`, `packages/contracts/**`, `_contract_schemas/**`, or `apps/web/**` edits (SI-S12 holds).
- `git status --porcelain` after tests → **clean** (no stray artifacts; engine is offline/in-memory, tests reuse committed ZF03/MPG06 fixtures). Low-storage OK.

## Hard invariants — verified IN CODE (not just via tests)
**(a) No code path emits a `verified` status/class value.** Grep over `app/spatial/**`: "verified" appears only in disclaimer prose and the `verified_at` provenance *timestamp* field (`policy.py`) — never as a status/class literal. The full class vocabularies (`models.py:20-47`) contain no `verified`. Two dedicated tests enforce this (JSON-blob ban + source-literal regex). Confirmed live on a data_conflict record: no `"verified"`/`confirmed_*` literal present.

**(b) Uncertain cases never collapse to a definitive district; ZTLDB agreement only sets `display_upgrade='conditional'`.** In `engine.py:199`, `lot_overall_class` is exactly `geom_class`, or escalates to `LOT_DATA_CONFLICT` on set-conflict (strictly more conservative). ZTLDB influence lives only in `crosscheck.display_upgrade` (a separate field never read back to mutate the class) and `geometric_probable_label` is internal-only (not stored on the record). Independent live checks with fresh inputs:
- near-boundary + ZTLDB agreement → `lot_overall_class=boundary_uncertain`, `display_upgrade=conditional`, `review=True` (not collapsed)
- sliver + ZTLDB agreement on both → `sliver_ambiguous` (not single_district)

## Classification order & precedence — correct and deterministic
`geometry._preliminary_class` order (exterior→interior-within-erode→firm-split→sliver-like→near-boundary) is sound; I hand-verified SI-S1 (raw=10000, share=1.0), SI-S3 (raw=800, sliver-like→near-boundary), and the 50ft narrow district (erode empty → `band_exceeds_feature_width`, not interior). `engine` lot-overall precedence (any near→uncertain; any sliver→sliver; ≥2 firm→split; exactly-1 interior→single; else uncertain) is conservative and correct; lone split_confident falls to boundary_uncertain. The `_sliver_like` sentinel is always resolved before counting. Determinism backed by pinned shapely 2.0.7/GEOS 3.11.4 (asserted at entry via `assert_geometry_pins`), 4/8-decimal quantization, and stable sort keys; SI-S10 and the real holed-lot test assert byte-identical reruns.

## Test quality
Meaningful, non-tautological: assertions check exact computed areas/shares and specific classes, cover normal (SI-S1) / boundary (SI-S3) / missing (SI-S11 empty districts, adapter no_feature) / failure (SI-S7 degenerate + invalid geometry), and exercise real committed connector fixtures + the adapter path. Coverage-honesty negatives (cross-family stacking, overlay absence) and positives (same-family gap/overlap) are distinctly asserted.

## Observations (non-blocking; not corrections required for PASS)
1. `coverage.py:90-106` — per family, overlap vs gap is mutually exclusive (overlap wins). A base family with a *simultaneous* same-family overlap AND coverage gap would emit only `overlap_area`, dropping the gap quantity. Requires overlapping base polygons (an upstream anomaly already surfaced as `overlaps_detected`), so low severity; consider emitting both quantities independently.
2. `engine.py:201-227` — coverage-audit `gaps_detected`/`overlaps_detected` does not itself feed `professional_review_required`. In every tested case a coincident trigger (ZTLDB-absent or boundary_uncertain) forces review, but a `split_lot_confident` lot with ZTLDB agreement and a genuine base gap could carry `review=False` while `unassigned_area` is non-empty. Honesty is preserved (quantity is explicit, never renormalized); flagging review would be more conservative. Hardening suggestion only.
3. Process note (not code): the branch also carries orchestrator-authored ledger files (`project-control/gates/*.json`, `state.json`, report json). Within orchestrator authority, not producer scope — flagged only for integration awareness.

**Final: PASS.** No blocking defects. Both mandated invariants hold in code and live; all required suites green; scope and low-storage discipline respected. Observations 1–2 are optional follow-up hardening the orchestrator may track separately.

Relevant paths (absolute):
- `c:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T013-spatial\services\api\app\spatial\` (engine.py, geometry.py, coverage.py, crosscheck.py, models.py, policy.py, adapter.py, __init__.py)
- `c:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T013-spatial\services\api\tests\spatial\test_spatial_intersection.py`
- `c:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\.claude\worktrees\M2-T013-spatial\project-control\tasks\M2-T013.json`
