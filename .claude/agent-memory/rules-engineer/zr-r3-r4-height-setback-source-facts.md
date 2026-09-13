---
name: zr-r3-r4-height-setback-source-facts
description: Verified R3/R4-series ZR height & setback source facts (23-42/421/422), captured fresh 2026-09-13 for M4-T014 - variant enumeration, numeric caps, section asymmetry, A2 gaps
metadata:
  type: project
---

Verified against `zr.planning.nyc.gov` on **2026-09-13** (City of Yes, Last Amended
**2024-12-05**) for M4-T014. Analogue of the (torn-down) `zr-r1-r2-height-setback-source-facts`
the M4-T012/B-023 producer wrote; those R1/R2 facts now live in blocker **B-023**.

**Why:** so a future wave (R5-family extensions, an R1/R2 re-dispatch after B-023, or a
G6 review) need not re-fetch. **How to apply:** these are the numeric caps + enumeration
anchors already encoded as `needs_review` DRAFT rules; re-verify against a fresh snapshot
before publishing (nothing here is G6-approved).

## §23-42 (overview/routing, districts "R1 R2 R3 R4 R5")
Routes to §23-421 (pitched) + §23-422 (flat); §23-423 setback where applicable;
§23-424/425 qualifying-site / large-site increases; §23-426/§23-44 modifications.
Height measured from the **base plane**. All the 424/425/426/44 provisions are
CONDITIONAL = A2 gaps (D-045-R008).

## §23-421 pitched-roof envelope
Opening district list (anchor): **R1 R2 R3A R3X R3-1 R3-2 R4 R4-1 R4A R5A**. ONE uniform
envelope for the whole list: perimeter wall **max 25 ft** above base plane; ridge/building
**max 35 ft** above base plane. Applies to single-/two-family detached, semi-detached, or
zero-lot-line forms "where permitted" (building-type gate). Setback above the wall =
sloping-plane geometry (apex points, ≤80° pitch, paras a–g) = A2 gap, NOT numeric. The
"5 ft reference plane" special provision is R1/R2-without-suffix ONLY (not R3/R4).

## §23-422 flat-roof envelope
Opening district list (anchor): **R3-2 R4 R4B R5 R5B R5D**. Per-statement:
- **R3-2, R4** (grouped): "for residences not subject to the provisions of Section 23-421,
  the maximum building height shall be **35 feet**" (single cap, no base/setback split).
- **R4B**: "the maximum building height shall be **25 feet**" (single cap, no building-type
  condition, flat-only).

## Variant × section asymmetry (recorded, NEVER symmetrized)
Dual-section (building type selects): R3-2, R4. Pitched-only: R3A, R3X, R3-1, R4-1, R4A.
Flat-only: R4B. R1/R2 = B-023 (blocked). R5/R5A/R5B/R5D = accepted M4-T006 pilot.

## Encoded (M4-T014, uncommitted at handoff)
`r3-r4-pitched-height` (25/35), `r3-2-r4-flat-height` (35), `r4b-height` (25); family
`residential_height_setback_r3_r4`; snapshots `zr-23-42`, `zr-23-421-r3-r4`, `zr-23-422-r3-r4`.
See [[zr-height-setback-extraction-mechanism]] for the how.
