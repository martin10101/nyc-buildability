# M2-T013 — Post-Review Fail-Safe Hardening (additive)

**Applied by:** orchestrator (lead) · **Date:** 2026-07-21
**After:** G1/G3/G4 all PASS at review SHA `59dbe65` (reports M2-T013-G{1,3,4}-*.md)

The three independent gates PASSED with no blocking findings. Two reviewers left
matching **non-blocking, optional** fail-safe recommendations and explicitly deferred
to the orchestrator to apply-or-track. For a legally-sensitive tool the conservative
choice is to close them now: each change is **strictly additive** (it only ADDS
professional-review flags or preserves an extra explicit quantity — it never removes a
flag, changes a geometry result, or collapses an uncertain case). All prior invariants
and gate evidence remain valid; the changes were re-verified by the full suite.

## Changes

1. **G4 F1 — non-base-family uncertainty now reaches the review rollup** (`engine.py`).
   The lot-overall class is (correctly) computed over base zoning only, so a genuine
   `near_boundary_uncertain` / `sliver_ambiguous` on an **overlay / special district**
   over material lot area previously did not set `professional_review_required`. Added a
   pair-scoped trigger for any non-base uncertain pair (advisory §2.6.1: "if rule
   sensitivity is unknown at this milestone: always"). The pair record is unchanged and
   never collapsed. Test: `test_f1_non_base_overlay_uncertainty_triggers_review`.

2. **G3 obs 2 — coverage anomalies now force review** (`engine.py`). A same-family
   `gaps_detected` / `overlaps_detected` audit now adds a review reason, so an explicit
   coverage gap/overlap is not left visible-but-unflagged even when the lot class is
   otherwise confident and ZTLDB agrees. Test:
   `test_coverage_anomaly_triggers_review_in_isolation`.

3. **G3 obs 1 — simultaneous overlap AND gap both stay explicit** (`coverage.py`). The
   `unassigned_area` and `overlap_area` quantities are now computed independently, so a
   base family with both an overlap and a gap emits both (status still labels the
   stronger overlap signal). Test: `test_g3_obs1_simultaneous_overlap_and_gap_both_explicit`.

## Re-verification (local; CI authoritative on push)
- `python -m ruff check .` → All checks passed
- `python -m pytest tests/spatial -q` → **29 passed** (26 + 3 new)
- `python -m pytest -q` (full API suite) → **567 passed** (no regression)

## Control-plane note
Gates G1/G3/G4 are recorded PASS against the exact reviewed SHA `59dbe65`; this hardening
is a documented additive follow-up committed afterward. It does not change the geometry
engine's results or any invariant the reviewers verified. Because the change is additive
and was reviewer-recommended, no re-review is required for the current (blocked)
acceptance; the owner may request a light re-confirmation at integration if desired.
Acceptance remains blocked (M0-T019 sequencing exception + separate owner authorization).
