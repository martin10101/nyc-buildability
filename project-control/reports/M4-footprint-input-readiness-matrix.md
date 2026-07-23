# M4 footprint — canonical-input-readiness matrix (SHARED across M4-T007..T010)

Maps every applicability condition of the R5-series **footprint** rule families (yards + lot
coverage) to an EXACT canonical `property_profile` field path (schema v1.4.0 +
`services/api/app/profile/builder.py`), classifies readiness, and states the fail-closed outcome when
the input is missing/uncertain/contradictory/unavailable. **Nothing here authorizes emitting a guessed
value; every gap fails closed to a typed, visible outcome** (`missing` / `unsupported` /
`rule_conflict` / `professional_review_required` / `data_conflict` / `not_applicable`). Values remain
`needs_review` / `conditional` at most, never `verified`; acceptance is gated on G6.

This matrix incorporates owner corrections (2026-07-23): **§11-25 applicability** (row 1; see
`M4-footprint-r5-11-25-applicability-decision.md`) and **tax-lot vs zoning-lot area** (row 3).

Canonical paths referenced (READ-ONLY): `zoning.districts[]`, `zoning.commercial_overlays[]`,
`zoning.special_districts[]`, `zoning.mapped_features[]` (feature ∈ {histdist, landmark, transitzone,
splitzone, …}), `lot_facts.{lotarea,lotfront,lotdepth,lottype,irrlotcode}`, `lot_geometry.area_sq_ft`,
`spatial_intersection.lot_overall_class`, `existing_building_facts.{unitsres,unitstotal,…}`.

Readiness legend: **available** · **available-as-flag** (present as a mapped-feature boolean;
absence ≠ proof of absence) · **conditional** (available but caveated — must fail closed under the
stated condition) · **unusable-semantics** (value present but its meaning is not established for this
use) · **unavailable** (no canonical field).

| # | Applicability condition | Canonical field path | Readiness | Fail-closed outcome when not confidently available |
|---|---|---|---|---|
| 1 | District variant (R5 / R5A / R5B / R5D) | `zoning.districts[]` (exact string) | available | Null/absent → `professional_review_required` + `missing_critical`, no value. Non-R5 or unknown suffix (e.g. `R5X`) → `not_applicable`, no value; **never mapped to a nearest variant**. Each variant is represented EXPLICITLY. **Per §11-25**, a base-`R5` provision applies to a suffixed district (R5A/R5B/R5D) UNLESS the controlling section supplies a separate suffix provision; a suffix value derived through §11-25 cites **§11-25 + the substantive section** (not a silent family default). Residual (narrow) interpretive point: which building types a variant PERMITS still governs which building-type-keyed regime applies (a use-regulation determination, e.g. side yards) — flagged, not resolved mechanically. |
| 2 | District geometric certainty | `spatial_intersection.lot_overall_class` | conditional | `data_conflict` class → `data_conflict`; any non-`single_district_confident` class (split/sliver/boundary-uncertain/invalid) → `professional_review_required`; positional uncertainty is **never** collapsed into a definitive district. Split-share ranges pass through as ranges. |
| 3 | Lot area (for coverage %, large-site, ≥5,000 sf QRS) | `lot_facts.lotarea` (DOF/PLUTO) + `lot_geometry.area_sq_ft` (MapPLUTO geometry) | **conditional** | **Both are TAX-LOT facts, not proof of the legal ZONING-LOT area** the ZR regulates (a zoning lot may aggregate multiple tax lots or be a portion, §12-10). **Zoning-lot area is `conditional`**: tax-lot area is a documented proxy; a tax-lot↔zoning-lot mismatch signal (e.g. multi-tax-lot ownership, `splitzone`, portion) → **documented limitation / `professional_review_required`**. The two tax-lot measurements are compared under a **documented tolerance + comparison policy** (producer-defined, deterministic); a **within-tolerance** difference is NOT a conflict; only an **out-of-tolerance** difference → `data_conflict`. Absent → `missing`. |
| 4 | **Lot type (interior / corner / through)** — drives all four dimensions | `lot_facts.lottype` (DOF CAMA, dict p.31) | **unusable-semantics** | PLUTO `LotType` **cannot establish the ZR lot type** → `professional_review_required`, no value. Reasons (dictionary-grounded): tax lot ≠ zoning lot; **FALSE FRIEND** — PLUTO code 6 "Interior lot" = *no street frontage*, whereas the ZR "interior lot" the rules key on = ordinary one-street lot = PLUTO code 5 "Inside"; lossy "lowest-code" collapse hides corner/through-ness; PLUTO has no 135°/portion/opposite-street concepts. A dedicated NC **guards the false friend** (code 6 must never map to ZR interior). |
| 5 | Lot width (ZR "lot width" = mean distance between side lot lines, §12-10) | `lot_facts.lotfront` (DOF PTS, feet, dict p.29) | **conditional** | `LotFront` is one-side **frontage** (chosen by the PTS building address for multi-street lots), **not** ZR lot width; reliable only on a rectangular one-street lot. `irrlotcode`=Y or corner/through → `professional_review_required`. Width-predicated values (QRS ≥150 ft, §23-334 narrow-lot, §23-342 <40 ft) fail closed absent a professional lot-width determination. |
| 6 | Lot depth (rear-yard-equivalent / shallow-lot) | `lot_facts.lotdepth` (DOF PTS, feet, dict p.29) | conditional | Irregular/corner/through → `professional_review_required`; the §23-343 ≥190 ft / <110 ft and §23-342 <95 ft triggers require a professional depth determination when the tax-lot proxy is unreliable. |
| 7 | Irregular-lot flag | `lot_facts.irrlotcode` (Y/N) | available | Gates the reliability of rows 3/5/6: Y → those rows fail closed to `professional_review_required`. |
| 8 | Building type (detached / semi-detached / attached / zero-lot-line) — drives side + rear yards | **none** (`bldgclass`/`proxcode` describe the *existing* structure; `proxcode` 1/2/3 ≠ ZR taxonomy, no ZLL value) | **unavailable** | `professional_review_required`, no value. Also a *proposed*-building attribute (project intent), doubly unavailable. |
| 9 | Number / type of residences (1–2-family vs multiple dwelling) | `existing_building_facts.unitsres` / `unitstotal` (EXISTING only) | conditional (existing-only) | Rules key on the **proposed** residences (project intent); the existing count does not establish the proposed condition → `professional_review_required` / documented limitation, not a silent assumption. |
| 10 | Qualifying residential site (Greater Transit Zone geography) | **none** (needs ≥5,000 sf + GTZ location + frontage/short-block + district/CF exclusions, §12-10) | **unavailable** | `professional_review_required`. `transitzone` mapped feature is a partial signal and does NOT establish QRS. Unlocks §23-333 (no side yard), §23-321 front reduction, coverage/short-block provisions — none emitted without a professional QRS determination. |
| 11 | Commercial overlay present | `zoning.commercial_overlays[]` non-empty | available | `true` → `professional_review_required` (modification may apply); the base value is surfaced only with a PRR flag + recorded exception, never silently. Empty → no downgrade. |
| 12 | Special district present | `zoning.special_districts[]` non-empty | available | `true` → `professional_review_required` + recorded exception. Special-Purpose-District chapters can supersede Ch. 3; those overrides live outside Ch. 3 (not captured) → named limitation. |
| 13 | Historic district / landmark | `zoning.mapped_features[]` feature ∈ {histdist, landmark} | **available-as-flag** | Presence → `professional_review_required`. **Absence ≠ proof of non-historic** (SODA null-omission) → documented limitation. NOTE: no historic-district *yard/coverage* modifier was found in Ch. 3 (contrast §23-426 for height); LPC jurisdiction is a separate approval track. |
| 14 | Geographic (transit zone; CD-12 Brooklyn; parks) | `zoning.mapped_features[]` transitzone (partial); **none** for CD-12/park adjacency | available-as-flag (partial) / unavailable | Presence of a geographic modifier signal → `professional_review_required` / limitation. §23-72/§23-723 (CD-12 Brooklyn) and §23-381 (park) modifiers are not lot-locatable from canonical inputs → named limitation. |
| 15 | Adjacent front-yard / prevailing street-wall line-up (§23-321) | **none** (off-lot facts about neighboring buildings) | **unavailable** | `professional_review_required`; the line-up depth cannot be computed from on-lot canonical inputs. |
| 16 | Pre-1961 existing-condition (shallow-lot §23-342/343; narrow-lot §23-334) | **none** (historical fact "in existence on 12/15/1961, neither increased nor decreased") | **unavailable** | `professional_review_required`; the reduction is never applied from current data alone. |
| 17 | `as_of` evaluation date | supplied by caller | available | Before the controlling amendment (candidate `2024-12-05`) → `not_applicable` (not effective), no value. Malformed/impossible → `professional_review_required`. |

## Fail-closed reading by dimension (which task consumes which rows)

- **Lot coverage (M4-T007, §23-361/363):** rows 1,2,3,4,7,9,11,12,13,14,17 (+ large-site via row 3). Corner-vs-interior coverage and the shallow/short-block/corner increases fail closed on lot type (row 4); the multiple-dwelling table fails closed on proposed dwelling type (row 9); large-site fails closed on zoning-lot area (row 3). R2X/R3A/R3X "remainder-after-yards" is a documented limitation (coverage-follows-yards, not evaluated here).
- **Rear yards + rear-yard equivalents (M4-T008, §23-342/343/344):** rows 1,2,4,5,6,7,8,16 (+ height, corner/short-block via §23-344). Interior-vs-through **routing** fails closed on lot type (row 4); the 20/30/40/60 ft values fail closed on building type (row 8) and height; shallow-lot fails closed on row 16.
- **Front yards (M4-T009, §23-321):** rows 1,2,4,5,10,15,17. Candidate R5/R5A 10 ft vs R5B/R5D 5 ft is per §11-25 (row 1); corner reduction fails closed on lot type (row 4); QRS ≥150 ft width fails closed on rows 5+10; the adjacent line-up fails closed on row 15.
- **Side yards (M4-T010, §23-332/331/333/334):** rows 1,2,5,8,9,10,16. The three building-type regimes fail closed on row 8 (the decisive, unavailable input); §23-333 QRS on row 10; §23-334 narrow-lot on rows 5+16; adjacency conditions on off-lot facts (limitation).

**Headline (unchanged by the corrections):** the footprint family is fail-closed-HEAVY — the dominant
driver **lot type** is unusable from PLUTO, **building type** is unavailable, and **zoning-lot** area/
width are only conditionally proxied by tax-lot facts. For most real lots these rules surface
`[CANDIDATE]` values only with PRR flags, never as final constraints. That is the correct, honest
behavior and is exactly what the four separate `legal_rule` slices encode.
