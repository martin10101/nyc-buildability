# M4-T006 — Input-readiness matrix (R5 height & setback DRAFT rule family)

Maps every rule condition/input of the `residential_height_setback` family to an
EXACT canonical `property_profile` field path (schema v1.4.0), classifies its
readiness, and states the fail-closed outcome when the input is
missing/uncertain/contradictory/unavailable. Nothing here authorizes emitting a
guessed value; every gap fails closed to a typed, visible outcome.

Canonical field paths referenced (READ-ONLY, `packages/contracts/schemas/v1/property_profile.schema.json`):
- `zoning.districts[]` (array of strings)
- `zoning.commercial_overlays[]` (array of strings)
- `zoning.special_districts[]` (array of strings)
- `lot_geometry.area_sq_ft` (number)
- `spatial_intersection.lot_overall_class` (string; M2-T013 certainty class)

Readiness legend: **available** (a canonical field can supply it) / **uncertain**
(available but may be geometrically uncertain) / **contradictory** (conflicting
signals) / **unavailable** (NO canonical field exists).

| # | Rule input / condition | Canonical field path | Readiness | Fail-closed outcome when not confidently available |
|---|---|---|---|---|
| 1 | `zoning_district` (which R5 variant) | `zoning.districts[]` | available | missing/null → `professional_review_required`, `missing_critical`, no value (NC-5). Non-R5 or unknown variant (e.g. `R5X`) → `not_applicable`, no value; never mapped to nearest variant (NC-1). |
| 2 | District geometric certainty | `spatial_intersection.lot_overall_class` | uncertain / contradictory | `data_conflict` class → `data_conflict` coverage (NC-6). Any non-`single_district_confident` class (split/sliver/uncertain) → `professional_review_required`; uncertainty never collapsed into a definitive district (uncertainty_policy). |
| 3 | `street_width_class` (wide ≥75 ft / narrow <75 ft, §12-10) — R5 & §23-424 setback DEPTH | **none** (no street-width / frontage field exists) | **unavailable** | REQUIRED input on `r5-setback`; unavailable → `professional_review_required`, `missing_critical`, NO depth value (NC-2). Out-of-enum/guessed class → invalid, fail closed (NC-2). |
| 4 | `building_type` (detached / semi-detached / zero-lot-line, §23-421) — R5A applicability & flat-vs-pitched selection | **none** (no building-type field exists) | **unavailable** | REQUIRED input on `r5a-height`; unavailable → `professional_review_required`, `missing_critical`, NO value (NC-4). |
| 5 | `qualifying_residential_site` (§12-10 test) — §23-424 alternative envelope unlock | **none** (needs ≥5,000 sf lot + Greater-Transit-Zone geography + frontage/short-block + district exclusions) | **unavailable** | REQUIRED input on `r5-qrs-height`; unavailable → `professional_review_required`, no value (NC-4). Even `lot_geometry.area_sq_ft` alone cannot establish it (geography missing). |
| 6 | `overlay_present` (commercial overlay modifies height, §23-44) | `zoning.commercial_overlays[]` non-empty | available | Optional boolean derived from the array. `true` → `professional_review_required` (never the silent base value); the base value is surfaced only with a PRR flag + recorded exception (NC-3). Empty array → no downgrade. |
| 7 | `special_district_present` (special district modifies height, §23-44) | `zoning.special_districts[]` non-empty | available | Optional boolean. `true` → `professional_review_required` + recorded exception (NC-3). Empty array → no downgrade. |
| 8 | `historic_district` (base-height match, §23-426) | **none** (no historic-district field) | **unavailable** | Optional boolean. When a caller supplies `true` → `professional_review_required`. When absent it is a documented limitation (the override is not silently cleared); the citywide value is not asserted as final for a lot that may be historic. |
| 9 | `large_site` (large-site context, §23-425) | **none** (no large-site field) | **unavailable** | Optional boolean. When a caller supplies `true` → `professional_review_required`. Absent → documented limitation. |
| 10 | Ground-floor / frontage condition (post-City-of-Yes) | **none** | **unavailable** | No R5 height/setback constraint in this family is predicated on a ground-floor condition per the captured source; any future such condition inherits the same fail-closed rule (unavailable input → `professional_review_required`). Recorded as a limitation. |
| 11 | `as_of` evaluation date (temporal effectiveness) | supplied by caller | available | Date before `2024-12-05` → `not_applicable` (not effective), no value (AS-3). Malformed/impossible date → `professional_review_required`, no value (evaluator FH-1). |

## Fail-closed summary by district variant

- **R5** — base height 35 / building height 45 emitted (heights are street-width **independent**); setback DEPTH is a SEPARATE rule and is `professional_review_required` unless `street_width_class` is supplied (row 3). No minimum base height stated → documented limitation, never a zero.
- **R5A** — perimeter-wall 25 / ridge 35 emitted ONLY when `building_type` is supplied (row 4); otherwise fail closed. Pitched setback = sky-exposure-plane geometry, documented limitation (professional review), no numeric depth.
- **R5B** — building height 35 emitted; no base/setback split invented.
- **R5D** — building height 45 emitted; no base height and NO setback invented (encoded SEPARATELY from R5 despite the shared 45 ft building cap).
- **§23-424 alternative (all variants)** — base 45 / building 55 emitted ONLY when `qualifying_residential_site` is supplied (row 5); otherwise fail closed. Competes with the base-district height rules → `rule_conflict`, no selected value (NC-7).

Every emitted value is `needs_review` / `conditional` at most, never `verified`; final acceptance and publication remain gated on G6 qualified-human legal approval.
