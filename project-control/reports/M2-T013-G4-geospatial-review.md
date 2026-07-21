<!-- Preserved VERBATIM by the orchestrator from the geospatial-engineer agent return, 2026-07-21 (transport entity-decoding only: &gt; &lt; &amp; decoded). -->

---

# G4 Geospatial Domain Review — M2-T013 Spatial-Intersection Engine

**Reviewer:** geospatial-engineer (independent; did not implement). **Review SHA:** 59dbe65, branch `task/M2-T013-spatial`. **Runtime:** Python 3.11.9, shapely 2.0.7 / GEOS 3.11.4 (pinned build present). **Verdict: PASS** (one non-blocking fail-safe recommendation, F1).

## Commands run (independent)
- `python -m pytest tests/spatial -q` → **26 passed in 0.56s**.
- Version probe → shapely 2.0.7 / GEOS 3.11.4 (matches the pin `assert_geometry_pins` enforces).
- Throwaway shapely spot-checks (scratchpad, deleted) recomputing split shares, near-boundary, boundary-touch, and an overlay edge case by hand and diffing against engine output.

## Geometry-correctness verification (all 9 points confirmed)
1. **Compound band / erode-dilate (C1):** `combined_band_ft = lot.value_ft + district.value_ft` (policy.py:186-189); `_erode_dilate = buffer(-B)/buffer(+B)` (geometry.py:69-72) — byte-for-byte the proven M2-T009 `classify_spatial_relation` semantics (connector:1065-1079), extended to the two-source sum. Linear sum, not RSS. ✓
2. **Five-class taxonomy + facts preserved (geometry.py:89-107, engine.py:132-140):** interior=`(not erode.is_empty) and lot.within(erode)`; exterior=`distance>B`; split=`firm>eps and firm_outside>eps`; sliver-like=`raw>eps and firm<=eps` → engine resolves to `sliver_ambiguous` iff firm area exists in a **different same-family** district (engine.py:135-140), else `near_boundary_uncertain`. Raw/firm/dilated/distance/lot_area stored regardless of class. Spot-check A (split: raw 30000 / firm 22000 / dil 38000 exact) and B (straddle→near_boundary raw=800; **boundary touch→near_boundary, raw=0, never inside/outside**) match hand geometry exactly. ✓
3. **Share ranges (§2.4, geometry.py:150-156):** min=firm/lot, point=raw/lot, max=min(dilated/lot,1.0). Spot-check A: min/point/max = 0.3667/0.5/0.6333; per-district min sums=0.733, max sums=1.267 — **not renormalized**; point not forced to 100% (test CF6). ✓
4. **Degenerate guard (geometry.py:132, 91; engine.py:214-218):** `erode.is_empty ⇒ band_exceeds_feature_width`; firm forced 0 and `within(erode)` unreachable, so interior/split impossible by construction; feeds review when raw>eps. Test S7 (50-ft strip vs 80-ft 2B) confirms. ✓
5. **2x-band fail-safe (§2.6.7, geometry.py:140-148; engine.py:208-213):** when any input basis=`assumed`, reclassify at 2B; a class change sets `sensitivity_flip`→review. Test S8 confirms interior→near_boundary flip escalates. ✓
6. **Coverage-family invariants (coverage.py, engine.py:105-146,237-254):** audit runs per family; only `base_zoning` carries `expected_full_coverage` so only it emits `unassigned_area`; same-family inclusion-exclusion overlap emits `overlap_area`; cross-family stacking never counted (tests CF1-4); `CoverageAudit`/audit-status internal, no contract import (test CF7). ✓
7. **ZTLDB cross-check (§2.5/C2, crosscheck.py):** set (`set()`) vs order (`==`) semantics; agreement/ordering_disagreement/set_conflict; `possible_vintage_skew` only when both vintages known and differ. Crucially, crosscheck can only **downgrade** geom class to `data_conflict` (engine.py:199) or leave it — it never upgrades; the sole "upgrade" is the separate `display_upgrade` capped at `"conditional"` (crosscheck.py:126-134). Never confident/verified. ✓
8. **HARD invariant:** uncertain pairs are never rewritten to a definitive assignment (sliver/near-boundary preserved with exact geometry); base uncertain classes + set_conflict always force `professional_review_required` (engine.py:201-227); no `"verified"` literal anywhere (tests CF5 x2; `coverage_note` explicitly disclaims). ✓
9. **Reproducibility:** pins asserted fail-closed (geometry.py:57-66); outputs quantized (areas 4dp, shares 8dp); test S10 asserts `first==second` and the exact pins. ✓

## Finding F1 (non-blocking; recommended fail-safe)
The lot-level `professional_review_required` rollup does **not** fire for positional uncertainty on **non-base families** (overlays/special districts) unless that pair independently `sensitivity_flip`s or hits `band_exceeds_feature_width`. Root cause: the lot-overall class and its review trigger are computed over `base_pairs` only (engine.py:149-183, 202-207), while the pair-level review triggers (engine.py:208-218) cover only sensitivity-flip and narrow-feature.

Empirical confirmation (spot-check C): base R5 `interior_confident` + a commercial overlay `C1-4` grazing the lot within the band → overlay pair correctly `near_boundary_uncertain` (raw=1000 preserved, firm=0, `flip=False`, `bxfw=False`), **yet** `lot_overall_class=single_district_confident`, `professional_review_required=False`, `review_reasons=[]`. A persistent overlay sliver does not flip at 2B (raw is band-independent, firm stays 0), so the fail-safe misses it.

**Why this is PASS, not FAIL:** (a) the overlay uncertainty is fully preserved at the pair level and is never collapsed into a definitive in/out-of-overlay assignment — the stated hard invariant holds; (b) computing the single/split lot-overall class over `base_zoning` only is defensible and arguably required by the owner's coverage-family amendment (invariant 2 makes base+overlay stacking legitimate, so folding overlay pairs into the single/split test would misfire on normal stacking); (c) nothing is labeled Verified; (d) downstream M4 overlay-applicability rules consume the pair record directly and must treat `near_boundary_uncertain` as conditional per §2.4/2.6.3. The gap is a review-completeness rollup issue, not a geometry error, and touches none of the 9 enumerated criteria.

**Recommendation:** also set `professional_review_required` (with a pair-scoped `review_reason`) whenever **any** pair — regardless of family — is `near_boundary_uncertain`/`sliver_ambiguous` over material lot area. ~3 lines in engine.py; strictly fail-safe. Orchestrator to decide whether to make it blocking-for-acceptance or a tracked follow-up.

## Minor notes (no action)
- `share_max`/dilate use shapely's default round-join buffer (curved convex corners) — identical to the proven, pinned M2-T009 primitive, so deterministic and consistent; not a defect.
- `_preliminary_class` orders exterior before interior (M2-T009 ordered interior first); the two are mutually exclusive, so no behavioral difference.
- Share denominator is the geometric EPSG:2263 lot area (connector:1028/1814), so `raw ⊆ lot`; shares stay in [0,1] with no unit mismatch.

**Scope/limits:** I reviewed geometry correctness and policy conformance of `app/spatial/**` against the approved advisory + owner decisions C1-C4 + coverage-family amendment, and ran `tests/spatial`. I did not run the full 564-test API suite (SI-S12 regression) or the G1 V1/V2 metadata-source verification — those belong to the data-contract/integration gates. No ledger action taken; read-only.
