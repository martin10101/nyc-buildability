---
name: zr-lowdensity-height-setback-structure
description: Post-City-of-Yes ZR height/setback structure for R1-R5 low-density districts; where the values and definitions live
metadata:
  type: project
---

City of Yes for Housing Opportunity (effective/last-amended 2024-12-05) restructured LOW-DENSITY
(R1-R5) height & setback into ZR §23-42 (Article II, Ch.3). The legacy §23-66x / §23-45 Quality-
Housing-vs-non-QH split no longer governs R1-R5 — third-party summaries (UpCodes, law firms) still
cite the stale §23-66x numbers, so go to official ZR text.

Envelope is selected by BUILDING TYPE, not district alone:
- §23-421 basic PITCHED-roof envelope: R1 R2 R3A R3X R3-1 R3-2 R4 R4-1 R4A R5A (detached/semi-
  detached/zero-lot-line). Uniform: perimeter wall max 25 ft, ridge 35 ft above base plane.
- §23-422 basic FLAT-roof envelope: R3-2 R4 R4B R5 R5B R5D. R5=base 35/bldg 45 + setback per 23-423;
  R5B=flat 35 (no setback); R5D=flat 45 (no setback). R5 and R5D both cap at 45 ft but only R5 has a
  base+setback — encode variants separately.
- §23-423 standard setback: at/below max base height, >=10 ft from wall on WIDE street, >=15 ft on
  NARROW street (reductions for front-yard depth, 7 ft floor, optional >50 ft / <=65deg).
- §23-424 qualifying residential sites: R5/R5A/R5B/R5D -> base 45 / bldg 55 (conditional on the
  §12-10 "qualifying residential site" test: >=5,000 sf + Greater Transit Zone geography + frontage).
- §23-426 Historic District + articulation (>150 ft walls); §23-44 special-district overrides.

Key §12-10 defs: wide street = >=75 ft; narrow street = <75 ft; qualifying residential site
(last amended 2024-12-05) is Greater-Transit-Zone-geography-dependent (hard for a system to evaluate
-> fail-closed).

**Why:** M4-T006 established these from raw ZR HTML (all sections Last-Amended 2024-12-05). No genuine
legal ambiguity — values are CLEAR; only input-dependence (street width, building type, QRS geography,
overlays) is conditional -> professional_review_required fail-closed.

**How to apply:** For any R1-R5 bulk (height/setback) rule task, pull §23-42 series, not §23-66x.
Distinguish the four R5 variants; never assume shared dimensions. See [[nyc-source-fetch-channels]]
for the curl/parse technique on the ZR portal.
