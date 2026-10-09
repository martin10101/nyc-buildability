# M5-T124 producer report — D-087 PKT-L2: drawing-to-lot alignment service (phase C2)

Producer: backend-engineer (orchestrator-dispatched subagent).
Worktree: `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t124` (branch `task/M5-T124-drawing-alignment`).
Claim-seam base (parent of my commit): `4c7437dd3eb0068ebff6c15221913e5bb7e6b801`.

## Files written (allowed_paths only)

- `services/api/app/drawings/drawing_alignment.py` (NEW; placeholder replaced) — the pure rigid-fit alignment service: 2D rigid least-squares fit through user-confirmed control pairs, every discrepancy disclosed never reconciled, the transformed draft re-validated through `validate_proposed_massing`. No route, no I/O, no persistence.
- `services/api/tests/drawings/test_drawing_alignment.py` (NEW; placeholder replaced) — 39 offline tests incl. 10 reddening in-process mutations.
- `project-control/reports/M5-T124-producer-report.md` — this report.

`git status --short` shows exactly the two code files modified (plus this report). No forbidden path touched: `sheet_import.py`, `dxf_import.py`, every `sheet_*`/`pdf_*`/`dxf_reader` module, `app/scenario/`, `app/connectors/`, `app/documents/`, `app/api/`, `app/main.py`, `app/cad/`, `tests/api/`, `apps/`, `packages/`, `docs/`, `requirements*`, `.github/` all unchanged. Zero new dependencies (uses stdlib + already-admitted shapely).

## Public API

Function:
- `align_draft_to_lot(draft_block, provenance, lot_ring, control_pairs, *, tolerance_ft=DEFAULT_TOLERANCE_FT) -> AlignmentResult | AlignmentRefusal` — duck-typed on the documented draft-block shape; fetches nothing; raises nothing (every failure a typed `AlignmentRefusal` VALUE).

Types (defined locally):
- `ControlPair(local: (x,y), target: (x,y))` — a user-confirmed pair (local feet <-> 2263). Also accepts a plain `(local, target)` 2-tuple.
- `PlaneTransform(m00, m01, m10, m11, tx, ty)` with `.apply(x, y)` and `.determinant` — the applied transform is always a PROPER rigid motion (det = +1).
- `AlignmentResult(ok, proposed_massing, provenance, alignment, discrepancies)`.
- `AlignmentRefusal(ok, reason, detail, field=None, discrepancies=())`.

Refusal reasons (closed vocabulary): `too_few_pairs`, `too_many_pairs`, `bad_control_pair`, `non_finite_input`, `coincident_source`, `indeterminate_rotation`, `bad_draft_block`, `bad_lot_ring`, `aligned_invalid`, `non_finite_result`.

Discrepancy `type` tokens (SHOWN, never reconciled): `two_pairs_unchecked`, `residual_exceeds_tolerance`, `scale_mismatch`, `better_mirror_fit`, `outline_outside_lot`.

## Fit formula (MATH AUTHORITY, cited in the module + `_cross_dot_sumsq`/`_rigid_fit`/`_mirror_fit`)

2D rigid least squares (Kabsch / orthogonal Procrustes, PROPER rotations only). For the centred pairs (`a` = source − source_centroid, `b` = target − target_centroid): `dot = Σ(ax·bx + ay·by)`, `cross = Σ(ax·by − ay·bx)`. Then `theta = atan2(cross, dot)`; the rotation is built directly from `cos = dot/hypot(dot,cross)`, `sin = cross/hypot(dot,cross)` (no atan2→cos/sin round-trip, so an exact right-angle fit stays exact — verified: 90° gives max vertex error 0.0), and `translation = target_centroid − R @ source_centroid`. NO scaling, NO reflection are applied. The IMPLIED scale (a similarity fit, DISCLOSED only) is `hypot(dot, cross) / Σ|a|²`. The mirror fit (DISCLOSED only) uses `F(phi) = [[c2, s2],[s2, −c2]]`, optimum at `2·phi = atan2(q, p)`, `p = Σ(bx·ax − by·ay)`, `q = Σ(bx·ay + by·ax)`.

## Bounds / tolerances declared (fail-closed; NOT legal or survey values)

- `MIN_CONTROL_PAIRS = 2` (exactly 2 = determined but UNCHECKED, disclosed), `MAX_CONTROL_PAIRS = 1000`.
- `MAX_LOT_RING_VERTICES = 100_000` (the only unbounded caller input; caps the outside-lot shapely work).
- Finite coordinates required on every control point and lot-ring vertex; distinct source picks required (coincident → `coincident_source`; zero `hypot(dot,cross)` → `indeterminate_rotation`).
- `DEFAULT_TOLERANCE_FT = 2.0` (residual disclosure threshold; caller-overridable), `SCALE_DISCREPANCY_REL = 0.01` (implied-scale disclosure), `_MIRROR_IMPROVEMENT_REL = 1e-9` (mirror disclosed only when strictly better). `CONFIRMED_SCALE = 1.0`.
- Every output number checked finite (`_finite_numbers`); a non-finite result → `non_finite_result`.

## Per-AS evidence

- **AS-1 (fit).** Pure translation lands the outline on the asserted 2263 vertices; 90° and arbitrary (31.7°) rotations land on the true-transform vertices (abs 1e-6); rotation reported; the applied transform is a proper rigid motion (orientation preserved) → `test_translation_fit_lands_outline_on_asserted_2263_vertices`, `test_ninety_degree_rotation_fit_exact_vertices`, `test_arbitrary_rotation_fit_matches_true_transform`, `test_applied_transform_is_a_proper_rigid_motion`. Formula cited next to the code.
- **AS-2 (discrepancies shown, never reconciled).** Per-pair residuals + max vs tolerance → `test_residuals_reported_per_pair_and_max_against_tolerance`; 2-pair unchecked disclosed → `test_two_pair_fit_disclosed_as_unchecked`; implied-scale (=2) disclosed and the outline NOT rescaled (local edge length preserved) → `test_implied_scale_disclosed_never_applied`; a better mirror disclosed and the outline NOT flipped (orientation preserved) → `test_better_mirror_fit_disclosed_never_flipped`; the outside-lot area (300 sq ft) disclosed and the outline NOT clipped → `test_outside_lot_area_disclosed_never_clipped`.
- **AS-3 (contract).** The aligned draft passes `validate_proposed_massing`, `provenance.kind` stays `'proposed'`, per-level outlines also transformed → `test_aligned_draft_passes_validate_and_keeps_kind_proposed`, `test_per_level_outline_is_also_transformed_into_2263`. A still-out-of-bounds fit (identity → near-origin) is a typed `aligned_invalid` naming the outline field → `test_still_out_of_bounds_result_is_a_typed_refusal`. Alignment provenance block complete → `test_alignment_block_is_complete`.
- **AS-4 (honesty + safety).** Precision label kept exactly and echoed unchanged → `test_precision_label_kept_exactly_and_never_upgraded`; no permit/approved/maximum-allowed wording anywhere → `test_no_permit_or_approved_or_maximum_allowed_wording`; every output number finite → `test_every_output_number_is_finite`; bounded/invalid inputs each refuse typed → the `*_refused_typed` tests below.
- **AS-5 (scope).** Pure (imports only `copy`, `math`, `dataclasses`, `shapely`, `app.scenario.proposal`); two identical calls equal; the input block is not mutated in place → `test_two_identical_calls_are_equal_no_persistence`, `test_input_block_is_not_mutated`, `test_module_imports_no_io_or_network`. Zero new deps; unmounted; the import/reader modules, `app/scenario` and the connectors untouched; ruff clean; modularity exit 0; exactly the allowed paths.

Typed-refusal tests (AS-4/AS-5): `test_too_few_pairs_refused_typed`, `test_too_many_pairs_refused_typed`, `test_non_finite_control_coordinate_refused_typed`, `test_coincident_source_points_refused_typed`, `test_indeterminate_rotation_refused_typed`, `test_bad_control_pair_shape_refused_typed`, `test_bad_draft_block_refused_typed`, `test_bad_lot_ring_refused_typed`, `test_lot_ring_over_cap_refused_typed`, `test_non_finite_lot_coordinate_refused_typed`.

## Mutation table (each mutation monkeypatches a module seam in-process and asserts the FLIPPED outcome; no harness committed)

| # | AS | Guard | Guarding test | Reddening mutation |
|---|---|---|---|---|
| 1 | AS-1 | translation present | `test_translation_fit_lands_outline_on_asserted_2263_vertices` | `test_mutation_translation_dropped_reddens_translation_fit` — `da._rigid_fit`→identity → outline stays local → `aligned_invalid` |
| 2 | AS-1 | rotation sense | `test_ninety_degree_rotation_fit_exact_vertices` | `test_mutation_rotation_sign_flipped_reddens_rotation_fit` — negate off-diagonal → vertices differ |
| 3 | AS-1 | rotation applied | `test_arbitrary_rotation_fit_matches_true_transform` | `test_mutation_identity_rotation_reddens_arbitrary_rotation` — `da._rigid_fit`→translation-only → vertices differ |
| 4 | AS-2 | per-pair residuals | `test_residuals_reported_per_pair_and_max_against_tolerance` | `test_mutation_drop_residual_reddens_residual_report` — `da._residuals`→drop last → count != pairs |
| 5 | AS-2 | 2-pair disclosure | `test_two_pair_fit_disclosed_as_unchecked` | `test_mutation_two_pair_disclosure_suppressed` — `da._is_unchecked_two_pair`→False → disclosure absent |
| 6 | AS-2 | scale not applied | `test_implied_scale_disclosed_never_applied` | `test_mutation_apply_implied_scale_reddens_scale_disclosure` — `da._applied_scale`→2.0 → outline edge doubled |
| 7 | AS-2 | no reflection | `test_better_mirror_fit_disclosed_never_flipped` | `test_mutation_allow_reflection_reddens_mirror_disclosure` — `da._choose_transform`→mirror → orientation flipped |
| 8 | AS-2 | never clip to lot | `test_outside_lot_area_disclosed_never_clipped` | `test_mutation_clip_to_lot_reddens_outside_lot_disclosure` — `da._final_outline_vertices`→intersect lot → extent shrinks |
| 9 | AS-3 | re-validation | `test_still_out_of_bounds_result_is_a_typed_refusal` | `test_mutation_skip_revalidation_reddens_out_of_bounds_refusal` — `da.validate_proposed_massing`→no-op → out-of-bounds returned ok |
| 10 | AS-4 | precision honesty | `test_precision_label_kept_exactly_and_never_upgraded` | `test_mutation_precision_upgraded_reddens_honesty` — `da._input_precision`→upgraded label |

Each mutation, taken as real behaviour, breaks its guarding test's assertion (the mutation tests confirm the displaced value moves, per the CODING_RULES "assert the field the bug displaces" rule).

## Commands (explicit cwd; verbatim result tails) — all [OBSERVED] on local Python 3.11.9; CI py312 is authoritative

- cwd `services/api`: `python -m ruff check .` → `All checks passed!` [OBSERVED]
- cwd `services/api`: `python -m pytest tests/drawings/test_drawing_alignment.py -q` → `39 passed` (0.62s–3.86s across runs) [OBSERVED]
- cwd `services/api`: `python -m pytest tests/drawings/test_drawing_alignment.py tests/drawings/test_sheet_import.py tests/drawings/test_dxf_import.py -q` → `99 passed in 0.81s` (siblings still green — no regression) [OBSERVED]
- cwd repo root: `python tools/modularity_check.py --check` → `EXIT=0`; `drawing_alignment.py` NOT in the warning list (592 SLOC, under WARN 600) [OBSERVED]

### LOCAL PYTHON note (NOT a defect)
The test imports only `app.drawings.drawing_alignment` (which imports `app.scenario.proposal`, shapely and stdlib) — none pulls the 3.12-only `app.documents` chain, so the file collects and runs on the sandbox's Python 3.11.9 WITHOUT the `shim311` fallback (confirmed the same way M5-T121 did). CI (3.12) is the authority.

## Deviations

1. **Input is the documented draft-block SHAPE, not a live `build_draft` return.** `sheet_import.build_draft` / `dxf_import.build_draft` REFUSE a genuinely local-frame draft today (`draft_invalid`, the DB-092 limit), so the aligner's caller supplies a block of that documented shape whose outline is in the local frame (never through the unchanged contract). This module is duck-typed on the shape and never imports either import module. See OPEN QUESTION 1.
2. **The rigid fit uses no scaling and no reflection by construction; the implied scale and mirror are computed only to DISCLOSE.** The applied `PlaneTransform` is always a proper rigid motion (`determinant` = +1). `_applied_scale` (=1.0), `_choose_transform` (=rigid) and `_final_outline_vertices` (=identity) are deliberate seams so a mutation can prove applying a scale / flip / clip would change the geometry.
3. **`tolerance_ft`, the scale/mirror thresholds and the caps are DISCLOSURE / fail-closed parameters, not legal or survey values** — declared as module constants and reported in the alignment block; they never modify geometry.

## OPEN QUESTIONS (owner asleep — recommended answers; orchestrator decides/queues)

1. **Where does the local-frame draft block come from, given `build_draft` refuses it?** Today both importers refuse a local-frame draft at the contract (DB-092). This aligner consumes a block of the documented shape whose outline is still local. **Recommendation:** the mount/wiring packet builds the pre-alignment block from the importer's candidate ring + service-measured scale (the same values `build_draft` uses) WITHOUT the premature NYC-bounds validate, hands it to `align_draft_to_lot`, and only the ALIGNED block is validated. Do not weaken `validate_proposed_massing`. Recorded as DISCOVERY DISC-A.
2. **Default residual tolerance value.** I chose `DEFAULT_TOLERANCE_FT = 2.0` ft as a disclosure threshold (residuals above it are shown, never applied). The MapPLUTO source accuracy is ±20 ft. **Recommendation:** keep 2.0 ft as a tight "good-fit" disclosure default and let the route pass a caller value; this is disclosure-only and never legal.
3. **Control-point source.** This packet takes user-confirmed pairs; it does not auto-match corners. **Recommendation:** the UI/route packet owns pair entry (click a drawing point, click the map) and must never auto-match — matches keep the user in the loop (D-087 honesty).

## DISCOVERIES (for the orchestrator to record in docs/DISCOVERY_BACKLOG.md at the seam)

- **DISC-A (the mount must build the pre-alignment block without the premature contract check).** Because `build_draft` validates against NYC-2263 bounds, a local-frame draft cannot be produced by the importers today. The C2 mount/wiring packet must assemble the pre-alignment `proposed_massing` block from the candidate ring + service-measured scale (skipping the early bounds validate) and let `align_draft_to_lot` do the only validation, at the aligned coordinates. This closes DB-092 end-to-end. Same gap for non-georeferenced DXF.
- **DISC-B (this packet is UNMOUNTED and pure).** A later mount packet owns the flag-gated route, per-caller rate limiting, an `allow_nan=False` pre-render guard and body ceilings (the PKT-H items). The service already refuses non-finite results typed, so the route needs only the defense-in-depth pre-render guard.
- **DISC-C (control-point capture UI is a separate C-track step).** Pair entry (click drawing point ↔ click map / place-on-lot) and the residual/discrepancy display belong to a UI packet; this service is the deterministic core it calls. Auto-matching corners is explicitly out (honesty).

## AS-5 scope confirmation

Pure, offline, unmounted; zero new dependencies (shapely already admitted); the module imports only stdlib + already-admitted internal modules; exactly the three allowed paths changed; the import/reader modules, `app/scenario` and the connectors are untouched; ruff clean; modularity exit 0.

END-OF-REPORT
