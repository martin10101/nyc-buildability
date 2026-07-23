# M4-T006 — targeted legal-semantics proof (owner verification)

**Scope:** owner's targeted legal-semantics verification of R5A (§23-421), the §23-423 setback, and
evidence wording. Evaluated against the actual evaluator output.
**Prior frozen SHA (R5A + heights, unchanged):** `6509db3`. **New frozen SHA (after the setback
correction):** `5d605d4`. Draft `needs_review` throughout; nothing Verified; **G6 unchanged.**

> Evidence wording (item 3): every value below is a **DRAFT extraction from the current official ZR
> portal (`zr.planning.nyc.gov`, effective 2024-12-05), pending qualified-human G6 byte-level
> verification** (`raw_html_verified:false`, `extraction_status:extracted_draft`). It is **not**
> conclusively verified current law.

## Item 1 — R5A / §23-421 — SATISFIED (no change; R5A rule byte-identical to `6509db3`)
Actual evaluator output:
- `evaluate("r5a-height", {zoning_district:"R5A", building_type:"detached"})` →
  `coverage=conditional`, `outputs={"max_perimeter_wall_height":25.0, "max_building_height":35.0}`,
  `exceptions_applied=[{id:"pitched_plane_setback_professional_review", effect:"documented_limitation",
  "…governed by pitched-plane (sky-exposure) geometry rising from the perimeter-wall height to the 35 ft
  ridge, NOT the flat section 23-423 10/15-ft rule … requires professional review"}]`.
- `evaluate("r5a-height", {zoning_district:"R5A"})` (real-world — no canonical building-type field) →
  `coverage=professional_review_required`, `outputs={}` (fails closed).

Proof: perimeter-wall height (25) and ridge/building height (35) are **separate typed outputs**, both
"above the base plane / not a buildable-envelope result" — **not** flattened to "25 ft max base + 35 ft
flat max building," and **not** the ordinary-R5 flat setback. The sloping-plane setback geometry is
**not emitted as a value**; it is flagged for professional review via the exception. No complete R5A
vertical envelope is claimed. Meets the owner's requirement (accurately typed partial constraints +
remaining envelope constraint flagged professional review).

## Item 2 — §23-423 setback — CORRECTED at `5d605d4` (was a gap at `6509db3`)
**Gap found at `6509db3`:** the output labeled 10/15 "minimum required setback depth" (coverage
conditional) with **no** marking that §23-423 reductions/modifications are unevaluated — and since a
reduction can lower the required setback *below* 10 ft (to a **7 ft floor**), labeling 10/15 the
"minimum" was legally imprecise and could read as a final applicable setback.

**Correction (2-file, no value change — 10 wide / 15 narrow unchanged; coverage unchanged):**
`r5_setback.rule.json` now (a) labels 10/15 as the **STANDARD UNMODIFIED minimum starting** depth under
§23-423, and (b) adds an always-on `documented_limitation` exception
**`section_23_423_modifications_unresolved`** stating the section's reductions/modifications —
street-wall location beyond the minimum front yard (with a **7 ft floor**), recesses/outer courts,
optional treatment for walls >50 ft from a street line or with a qualifying orientation, and dormer
penetrations — depend on inputs **absent from the canonical property_profile** and are **NOT evaluated**,
so the **modified/final applicable setback is UNRESOLVED (professional review)** and 10/15 is **never**
the final legally applicable setback.

Actual evaluator output after correction (`5d605d4`):
- `evaluate("r5-setback", {zoning_district:"R5", street_width_class:"wide"})` → `coverage=conditional`,
  `outputs={"required_setback_depth":10.0}`, `exceptions_applied` includes
  `section_23_423_modifications_unresolved` (documented_limitation). (narrow → 15.0, same marking.)
- `evaluate("r5-setback", {zoning_district:"R5"})` (real-world — no canonical street-width field) →
  `coverage=professional_review_required`, `outputs={}` (fails closed; 10/15 never surfaces for a real
  property).

Tests added: `test_as1_r5_setback_10_15_are_standard_unmodified_not_final` (wide+narrow) asserts the
marker is present, effect `documented_limitation`, and its text carries "standard unmodified" +
"never be presented as the final."

## Re-validation at `5d605d4` (orchestrator; thin client, Python)
- `ruff check` → All checks passed
- `pytest tests/rules/test_r5_height_setback.py` → **47 passed** (was 45; +2 correction tests)
- `pytest -q` (full API) → **928 passed** (no regression)
- `sync_zr_snapshots.py --check` → byte-identical (6) — **snapshots/values untouched**
- `test_zr_snapshot_bundle.py` + `test_installed_deployability.py` → 8 passed
- Change scope vs `6509db3` = exactly 2 files: `r5_setback.rule.json` + `test_r5_height_setback.py`;
  R5A rule, other rules, all 5 snapshots, evaluator, FAR rule, canonical contracts byte-unchanged.
- **Source self-check:** no snapshot or dimensional value changed (10/15/25/35/45/55 all as captured);
  the correction is labeling + unresolved-modification marking only.

Independent **G3/G4/G5** re-review + full CI re-run at `5d605d4` follow. Nothing published/verified/
accepted; **G6 qualified-human legal approval remains the boundary — not weakened; independent of B-010.**
