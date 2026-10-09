# Validation-collection expectations (D-073-R004)

A **small, FIXED** collection of real NYC properties with **expected outcomes documented BEFORE
consulting the application** — the production calculation is never its own reference (D-073-R004).
Expectations are established from **authoritative sources only** and the repo's **sha-pinned ZR
snapshots + rulesets**. Where an expectation cannot be established confidently, the case is
classified accordingly rather than forced into a positive (D-073-R004), and a supported positive
is supplied in its place.

- **Established / retrieved:** 2026-09-18 (all SODA/ArcGIS/snapshot lookups this date).
- **Constraint honoured:** the deployed product and its API were **NOT** consulted; these are
  independent expectations for a later, permitted end-to-end verification pass.
- **Authoritative sources:** PLUTO SODA `64uk-42ks` (channel version **26v2**; `ResidFAR`,
  `BldgArea`, `LotArea` are **reference/recorded** fields — D-073-R006 — never the calculated
  allowance); ZTLDB SODA `fdkv-4t4z` (authoritative **lot-level** district assignment); NYC GIS
  Zoning Features **nyzd** + **MAPPLUTO** ArcGIS (`services5.arcgis.com/GfwWNkhOj9bNBqoJ`).
- **Pinned rule authority (repo):**
  - `services/api/app/rules/rulesets/r6_r12_residential_far.rule.json` — flat R6–R12 lookup.
  - `services/api/app/rules/rulesets/r6_r7_r8_wide_street_conditional_far.rule.json` — R6/R7-1/
    R7-2/R8 wide-street conditional (returns the CONSERVATIVE value by DSL; the higher value is
    selected server-side ONLY on an affirmative within-100-ft determination, never on
    uncertainty).
  - `r5_residential_far.rule.json`, `r1_r2_r3_residential_far.rule.json` — R5 / R1-R3.
  - Snapshot `zr-23-22` (FAR table; `content_digest_sha256
    943b65f9005df8bd4d868e9656998d2c831faabc0df19d280fb1f9b98df1a38e`; last amended 2024-12-05).
  - Snapshot `zr-12-10` (wide/narrow street + named overrides; `content_digest_sha256
    23a9ccad31f1081fd15de94d796c22d540e7e8bcfe986e64c9ba302bf8fa4fde`; "street, wide" last
    amended 2026-03-26).
- All rulesets are `status: needs_review` / `extraction_status: extracted_draft` — DRAFT pending
  G6 qualified-human approval; **no expectation below is a Verified zoning determination.** Every
  computed FAR carries the qualifying-affordable/senior-housing higher value as a **conditional
  alternative** (never auto-applied), because whether a development qualifies is a separate legal
  determination.

**Expected-value convention:** `max_residential_far` = the district's standard-residences FAR;
`max_residential_floor_area = LotArea x FAR` (the ruleset's two outputs). LotArea is the PLUTO
recorded value (a reference input); the FAR is the pinned-ruleset value (the rule authority).

---

## Category A — Ordinary in-scope positives (flat R6–R12; street-independent) — HIGH confidence

These districts are a single flat lookup in `r6_r12_residential_far` (no wide-street condition);
the outcome does not depend on street width.

| # | Address | BBL | Expected outcome (standard residence) | Basis / provenance | Conditions under which the expectation holds |
|---|---|---|---|---|---|
| A1 | 289 Convent Avenue, Manhattan | 1020500007 | `max_residential_far = 3.00`; floor area = 9,800 x 3.00 = **29,400 sq ft** | Ruleset `r6_r12` `standard_far_by_district.R6A = 3.0` (snapshot zr-23-22). ZTLDB/PLUTO: single **R6A**, `SplitZone false`, no overlay/special district; PLUTO `ResidFAR 3.00`, `LotArea 9800` | zoning_district = R6A resolved; lot_area > 0; standard residence. Qualifying-housing alt (3.90) surfaced conditional |
| A2 | 610 East 191 Street, Bronx | 2032730287 | `max_residential_far = 2.00`; floor area = 3,790 x 2.00 = **7,580 sq ft** | Ruleset `r6_r12` `R6B = 2.0`. ZTLDB/PLUTO single **R6B**, clean; PLUTO `ResidFAR 2.00`, `LotArea 3790` | R6B resolved; standard residence. Qualifying alt (2.40) conditional |
| A3 | 195 Stanton Street, Manhattan | 1003440013 | `max_residential_far = 4.00`; floor area = 10,000 x 4.00 = **40,000 sq ft** | Ruleset `r6_r12` `R7A = 4.0`. ZTLDB/PLUTO single **R7A**, clean; PLUTO `ResidFAR 4.00`, `LotArea 10000` | R7A resolved; standard residence. Qualifying alt (5.01) conditional |
| A4 | 63 Pitt Street, Manhattan | 1003430062 | `max_residential_far = 6.02`; floor area = 5,000 x 6.02 = **30,100 sq ft** | Ruleset `r6_r12` `R8A = 6.02`. ZTLDB/PLUTO single **R8A**, clean; PLUTO `ResidFAR 6.02`, `LotArea 5000` | R8A resolved; standard residence. Qualifying alt (7.20) conditional |
| A5 | 9 West 64 Street, Manhattan | 1011170025 | `max_residential_far = 10.00`; floor area = 5,021 x 10.00 = **50,210 sq ft** | Ruleset `r6_r12` `R10A = 10.0`. ZTLDB/PLUTO single **R10A**, clean; PLUTO `ResidFAR 10.00`, `LotArea 5021` | R10A resolved; standard residence. Qualifying alt (12.00) conditional |

Note: PLUTO's recorded `ResidFAR` equals the pinned-ruleset FAR in every A-row — an independent
corroboration of the ruleset values (not a substitute for them).

## Category B — C-overlay residential positive — HIGH confidence

| # | Address | BBL | Expected outcome | Basis / provenance | Conditions |
|---|---|---|---|---|---|
| B1 | 3881 Sedgwick Avenue, Bronx | 2032630284 | `max_residential_far = 3.00`; floor area = 17,895 x 3.00 = **53,685 sq ft** — the **C1-3 commercial overlay does NOT change residential FAR**, which is governed by the underlying residence district R6A | Ruleset `r6_r12` `R6A = 3.0`. PLUTO: `ZoneDist1 R6A`, `Overlay1 C1-3`, `SplitZone false`, no special district; `ResidFAR 3.00`, `LotArea 17895`. A C1/C2 overlay is a commercial overlay mapped over a residence district; the residence district governs residential FAR | Underlying residence district = R6A resolved; standard residence; commercial/overlay FAR is a separate output not in scope of the residential-FAR rule |

## Category C — Materially different street conditions

`zr-12-10`: **wide street = >= 75 ft; narrow street = < 75 ft.** The canonical property profile
exposes **no street-width field**, so any wide/narrow-predicated result **fails closed** unless the
accepted wide-street stack supplies a typed within-100-ft determination (M5-T034). The conditional
rule's DSL therefore returns the **CONSERVATIVE** value; the higher value is selected server-side
ONLY on an affirmative within-100-ft-of-a-wide-street determination, never on uncertainty.

| # | Address | BBL | Expected outcome | Basis / provenance | Conditions |
|---|---|---|---|---|---|
| C1 (conditional district, narrow-street context) | 494 East 167 Street, Bronx | 2023710029 | **Conservative default `max_residential_far = 3.44`**; floor area = 3,772 x 3.44 = **12,976 sq ft**. Higher **4.00** applies ONLY on an affirmative within-100-ft wide-street determination | Ruleset `r6_r7_r8` `standard_far_by_district."R7-1" = 3.44`, `wide_street_far_by_district."R7-1" = 4.00` (zr-23-22 footnote 1). ZTLDB/PLUTO single **R7-1**, clean; PLUTO `ResidFAR 3.44` (the conservative value), `LotArea 3772` | R7-1 resolved; standard residence. If NO wide street within 100 ft → 3.44 is definitively correct. "or portions thereof" split is a geometry the draft does not compute |
| C2 (conditional district, wide-street-eligible) | 157 Broome Street, Manhattan | 1003410075 | **Conservative default `max_residential_far = 6.02`**; floor area = 6,221 x 6.02 = **37,450 sq ft**. Higher **7.20** applies ONLY on an affirmative within-100-ft determination; R8 footnote-2 **8.64** is compound-conditional (outside MIH area AND within 100 ft of wide street AND UAP/qualifying-senior) — surfaced only | Ruleset `r6_r7_r8` `"R8" = 6.02` conservative / `7.20` wide-street / `8.64` footnote-2. ZTLDB/PLUTO single **R8**, clean; PLUTO `ResidFAR 6.02`, `LotArea 6221` | R8 resolved; standard residence. Conservative 6.02 is the fail-safe; the higher value requires the wide-street determination from the accepted stack |
| C3 (named-street override → refusal) | 2521 Broadway, Manhattan | 1012420010 | **INDETERMINATE / professional-review refusal** for any street-dependent (wide-street) determination — the correct current outcome | Snapshot `zr-12-10` `named_street_overrides`: Broadway between **W94th–W97th, CD7 Manhattan** "shall be considered a wide street" **but** conditioned on "separated by mapped public park" — `qualifier_predicate_resolvable_from_text: false`, scope is open legal question **G6-Q1**, `disposition_when_located: indeterminate`. Lot is on that named segment (PLUTO/ZTLDB `2521 Broadway`, CD7). It is ALSO split `C4-6A/R8` in Special District **EC-3**, which independently forces professional review | Lot fronts the named Broadway W94–97 segment. The named override must NOT self-execute to "wide" (a coding assumption) nor be ignored — it returns indeterminate with provenance until G6 + a map-backed park predicate exist |

Alternate named-street lot (same class): **101 Allen Street (BBL 1004147501, C6-2A)** on the Allen
St **Rivington–Delancey, CD3** named segment (`zr-12-10` row `allen-st-cd3-rivington-delancey`,
same indeterminate disposition).

## Category D — Correct unresolved / unsupported outcomes — HIGH confidence

These are the cases whose CORRECT outcome is a specific unresolved/unsupported result. A refusal
here is the right answer; forcing a positive would be the defect.

| # | Address | BBL | Expected outcome | Basis / provenance | Conditions |
|---|---|---|---|---|---|
| D1 (condo billing BBL) | 298 Wallabout Street, Brooklyn | 3022647515 | **Unresolved / no lot-level zoning data** — correct refusal; needs condo→land-lot resolution | ZTLDB `bbl=3022647515` → **[]** (billing lot 7515, condono 1313, absent by design); ZTLDB block 2264 has 39 land lots, zero 75xx. PLUTO carries the condo aggregate (R7-1) but is not the lot-level source. See regression file case 2 | Correct until the condo billing-lot → base land-lot connection (ACRIS/DOF) exists; second-order R7-1 wide-street determination then still required |
| D2 (split-zoned lot) | 350 Fifth Avenue (Empire State Bldg), Manhattan | 1008350041 | **Professional-review refusal** — split zoning is never collapsed into one district | ZTLDB `zoning_district_1 C5-3`, `zoning_district_2 C6-4.5`, `special_district_1 MiD`; PLUTO `SplitZone true`, `C5-3 / C6-4.5`, Special Midtown District. Also both are **commercial** districts in a Special Purpose District — outside the R-district rulesets. Precedent DB-001 (verified against city records) | Correct while split-lot apportionment (ZR 77-series) + commercial/special-district FAR coverage are unbuilt; NEVER collapse to one district (D-073-R005) |
| D3 (unsupported rule coverage) | 1279 37th Street → 3622 13 Avenue, Brooklyn | 3052960043 | **Unsupported / professional-review refusal** — Special Mixed Use District FAR not covered | ZTLDB/PLUTO `M1-2/R6A`, `special_district_1 MX-12` (paired manufacturing/residential MX district; ZR Article XII). Rulesets cover only R1–R12; the special-district FAR modifier is "not yet implemented". See regression file case 1. Entered address "1279 37th St" also has no PLUTO/DTM lot (identity mismatch) | Correct until MX / Article XII FAR coverage exists AND the address→DTM-lot identity resolves. The R6A reference 3.00 must NOT be shown as the calculated allowance (D-073-R006) |

## Boundary-confidence class (Part-1 cross-reference; NOT forced as positives)

Per D-073-R004 ("if an expectation cannot be established confidently, classify accordingly and
pick another supported positive"), the two boundary-confidence regression cases are recorded here
by cross-reference rather than as validation positives, because their **exact** end-to-end
expectation depends on the geometry↔ZTLDB reconciliation that this authoritative-sources pass
cannot fully settle without a permitted server-log re-run:

- **401 Columbia Street, Brooklyn — BBL 3005250001.** Authoritative lot-level = single **R5**
  (ZTLDB, PLUTO `SplitZone N`, nyzd centroid R5); **split zoning refuted.** IF the geometric
  assignment reconciles to R5, the expected outcome is the R5 residential FAR (`r5` ruleset);
  IF geometric assignment is genuinely uncertain, a professional-review refusal is correct.
- **69-02 Kessel Street, Queens — BBL 4032110010.** Authoritative lot-level = single **R2**
  (ZTLDB, PLUTO `SplitZone N`, nyzd centroid R2). Same conditional expectation via the `r1_r2_r3`
  ruleset. Details + evidence: `docs/research/live-case-regression-properties.md` cases 3 & 4.

---

## Collection size by category

- **Category A (flat R6–R12 positives):** 5 — R6A, R6B, R7A, R8A, R10A.
- **Category B (C-overlay residential positive):** 1 — R6A + C1-3 overlay.
- **Category C (street conditions):** 3 — 1 conservative/narrow-context conditional (R7-1),
  1 wide-street-eligible conditional (R8), 1 named-street override refusal (Broadway W94–97;
  Allen St alternate recorded).
- **Category D (correct unresolved/unsupported):** 3 — condo billing BBL, split-zoned lot,
  unsupported MX coverage.
- **Total documented validation cases: 12**, plus **2 boundary-confidence cross-references**
  (401 Columbia, 69-02 Kessel) carried by reference, not counted as positives.

## Cases NOT established confidently (and why)

1. **The higher wide-street FAR outcome for C1/C2** (R7-1 4.00 / R8 7.20): the CONSERVATIVE
   default is established with high confidence; whether the higher value applies depends on the
   wide-street stack's within-100-ft determination and street-width data not computed in this
   thin-client research. Classified as conditional-on-affirmative-determination, not asserted.
2. **The exact end-to-end result for the two boundary-confidence lots** (401 Columbia, 69-02
   Kessel): authoritatively single, rule-covered districts (R5 / R2) with split zoning refuted,
   but the precise governing outcome hinges on geometry↔ZTLDB reconciliation and a permitted
   server-log re-run barred here. Recorded as boundary-confidence cross-references and replaced in
   the positive count by the Category-A/B positives.

## Scope of what this collection can prove

These are **independent, pre-registered expectations** for a later verification pass that runs the
**ordinary user path on real property data through the actual interface and existing report**
(D-073-R004). This document alone proves nothing about the application; it fixes the yardstick so
that a subsequent end-to-end run cannot become its own reference. Component evidence (a passing
internal test, a successful data request, a manually-fed calculation) does **not** substitute for
that user-path verification.
