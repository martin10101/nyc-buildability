<!-- Preserved VERBATIM by the orchestrator from the geospatial-engineer advisory agent return, 2026-07-20 (transport entity-decoding only: &gt; &lt; &amp; decoded). Commissioned under owner directive 2026-07-20 section 2 for M2-T013 pre-implementation policy. -->

# M2-T013 Geospatial Advisory — District Assignment Under Positional Uncertainty

**Role:** geospatial-engineer (advisory, read-only). **Date:** 2026-07-20. **Repo state reviewed:** main at 949f071.

---

## 1. Evidence reviewed

| Artifact | What it establishes |
|---|---|
| `services/api/app/connectors/mappluto_geometry_arcgis.py` (2,169 lines) | Lot-geometry channel. `BOUNDARY_TOLERANCE_FT = 20.0` at line 208, justified at lines 203–207 by the nyzd statement plus the claim that "MapPLUTO geometry derives from the same DTM/DCP production chain" — an analogy, not a documented MapPLUTO accuracy figure. `classify_spatial_relation` (lines 1029–1084) is the TEST-level classifier: relations `inside` / `outside` / `split_intersection` / `boundary_uncertain`, single 20 ft tolerance applied once via erode/dilate of the reference polygon (lines 1057–1058). It already outputs `distance_ft`, `intersection_area_sq_ft`, `subject_area_sq_ft`, `tolerance_basis`, and CRS (lines 1072–1084). Canonical digest precision 0.01 ft (line 221). CRS EPSG:2263 US survey feet enforced everywhere (lines 187–193, 463–481). |
| `services/api/app/connectors/zoning_features_arcgis.py` | District-polygon channel. Same EPSG:2263 (lines 139–145). Module header lines 55–58 records the official use limitation verbatim: *"These features are not intended for determining zoning at the individual tax lot level"* — lot-level work belongs to ZTLDB/PLUTO. No spatial intersection in this module. |
| `services/api/app/connectors/ztldb_soda.py` | Official per-lot assignment channel. 16-column schema (lines 178–195) — **no percentage columns exist**; only ordered `zoning_district_1..4` where order = greatest lot-area percentage first, since 2019-12-31 even below 10% (lines 291–298). Blank `zoning_district_2` officially means "not divided by a zoning boundary line" (lines 231–234). `zoning_district_1` can be absent live (lines 217–220, observed BBL 1000010201). Special-district `/` tie semantics at lines 304–309. |
| `services/api/tests/connectors/test_mappluto_geometry_arcgis.py` | Spatial scenario pack at lines 845–975: named-tolerance assertion (854–859), inside (865), outside (874), boundary-touch → `boundary_uncertain` never inside/outside (882–890, 943–944), within-band-outside → `boundary_uncertain` (898–903), split beyond tolerance (906–913), hole cases (930–934), 3-run reproducibility (963–973). |
| `project-control/reports/M2-T009-G4-geospatial-review.md` | G4 PASS. **Observation O4 (line 72)** is the trigger for this advisory: "both the lot and district geometries independently carry plus-or-minus 20 ft accuracy, so worst-case combined boundary uncertainty approaches ~40 ft… the future production intersection task should decide explicitly whether to compound tolerances." |
| `docs/research/zoning-features-ztldb-2026-07-16.md` | Line 149, official nyzd metadata PDF (Z11), verbatim: *"The estimated horizontal accuracy is +/- 20 feet."* — confirmed by independent direct read at G1 (OQ-10 resolved, line 262). Line 148: all six layers EPSG:2263. **OQ-5 (line 257) still OPEN:** the five other layer metadata PDFs (nyco, nysp, nysp_sd, nylh, nyzma) are unread — per-layer accuracy for those layers is NOT documented in the repo. OQ-3 (line 255) OPEN: ZTLDB Socrata rows possibly frozen at 2026-04-05 while nyzd refreshes monthly. Fixture plan ZF-F9 (line 235) already anticipated the three-way cross-check. |
| `docs/research/pluto-mappluto-2026-07-16.md` | **No positional-accuracy statement for MapPLUTO anywhere in the document** (grep for accuracy/tolerance/horizontal returns only the general DCP disclaimer, line 176). Lineage only: MapPLUTO = PLUTO merged with the DCP-modified DOF Digital Tax Map, clipped to shoreline (line 72). |

---

## 2. Recommended conservative production policy

### 2.1 Per-source positional accuracy model

Model accuracy as a **first-class provenance record per input geometry**, never a bare number:

```
source_accuracy: {
  value_ft: <float>,
  basis: "documented" | "assumed",
  citation: <exact official document + section, or the assumption rationale>,
  applies_to: <source_id + layer>,
  verified_at: <date of the official read>
}
```

Current honest values:

| Input | value_ft | basis | citation |
|---|---|---|---|
| nyzd district polygons | 20.0 | **documented** | nyzd_metadata.pdf Data Quality section, verbatim "+/- 20 feet" (research line 149; G1-confirmed) |
| nyco/nysp/nysp_sd/nylh/nyzma polygons | 20.0 | **assumed** (same production chain, per-layer PDFs unread — OQ-5) | must be marked `assumed` until OQ-5 is closed |
| MapPLUTO lot polygon | 20.0 | **assumed** (analogy in `mappluto_geometry_arcgis.py:203-207`; no documented figure in repo) | must be marked `assumed`; see §4 verification item V1 |
| ZTLDB rows | n/a (attribute data, no geometry) | — | carries its own vintage/staleness dimension instead (OQ-3) |

The engine must stamp both records (lot accuracy, district accuracy) on every intersection result. When a `basis: "assumed"` accuracy participates in a classification, the result must carry a visible `accuracy_basis_assumed` note — this is the direct implementation of the owner's directive that source accuracy never hides behind one arbitrary constant.

### 2.2 Combining tolerances: **linear sum, not root-sum-square**

Recommendation: `combined_band_ft = lot_accuracy_ft + district_accuracy_ft` (currently 40 ft), recorded with `combination_rule: "linear_sum"` and a rule version.

Reasoning for a legal-decision-support context:

1. **RSS is only valid for independent, zero-mean, roughly Gaussian errors.** Neither independence nor distribution shape is documented. The two products are NOT independent: nyzd was digitized against "DCP's Tax Block Base Map Files" (research line 149) and MapPLUTO derives from the DOF Digital Tax Map (pluto research line 72) — partially shared cadastral lineage means errors may be correlated, and correlated errors make RSS *underestimate* the band. "±20 ft" is stated as an estimated bound, not a standard deviation; treating a bound as 1-sigma and RSSing it (√(20²+20²) ≈ 28.3 ft) would manufacture 11.7 ft of confidence out of an undocumented statistical assumption.
2. **Asymmetric error cost.** A false "confident" district assignment can propagate into a Verified FAR/height result (legal exposure); a false "uncertain" merely asks for review. Conservatism must run one direction.
3. **Explainability.** "Each source states ±20 ft; we require agreement beyond the sum, 40 ft" survives evidence-viewer scrutiny and professional challenge. An RSS number requires defending an independence assumption nobody documented.
4. Keep the per-source values and the combination rule separately in the record so a future, evidence-backed switch to RSS (if DCP ever publishes error statistics) is a versioned policy change, not a silent recalibration.

Where only ONE source's boundary is in question (e.g., distance from a lot centroid to a district edge for display), use that single source's band; the compound band applies whenever a lot polygon is tested against a district polygon (both geometries uncertain).

### 2.3 Classification taxonomy

Per **(lot, district) pair**, computed with B = combined_band_ft, `erode = district.buffer(-B)`, `dilate = district.buffer(+B)` (direct extension of the proven M2-T009 semantics at `mappluto_geometry_arcgis.py:1055-1071`):

| Class | Deterministic condition | Meaning |
|---|---|---|
| `interior_confident` | lot ⊆ erode(district, B) and erode non-empty | Inside beyond any plausible compound error |
| `exterior_confident` | distance(lot, district) > B | Outside beyond any plausible compound error |
| `split_confident` | area(lot ∩ erode) > 0 AND area(lot ∖ dilate) > 0, and BOTH firm portions exceed the sliver floor (§2.5/O3) | Genuine split: firm area on both sides |
| `near_boundary_uncertain` | intersects/touches but no firm area on at least one side (everything inside the band) | Boundary indistinguishable from measurement error — never collapsed to inside/outside |
| `sliver_ambiguous` | raw intersection area > 0 but area(lot ∩ erode) = 0 (or below sliver floor), while the lot has firm area in a *different* district | The apparent second district could be pure registration error between the two geometry products |

Two additions to the pair record, per the owner's six preserved quantities:

- Always store the **exact geometric results**: raw intersection area, firm (eroded) intersection area, dilated intersection area, `distance_ft` to the nearest boundary, lot area — regardless of class. The class is an interpretation; the numbers are the facts.
- A degenerate-district guard: if `erode(district, B)` is empty (district narrower than 2B — real for narrow commercial-overlay strips in `nyco`, which are mapped ~150 ft deep), `interior_confident` is unattainable by construction; classify at best `near_boundary_uncertain` and record `band_exceeds_feature_width` so the UI can explain *why* confidence is impossible rather than showing an unexplained uncertainty.

Per **lot overall**: `single_district_confident` (exactly one `interior_confident`, all others `exterior_confident`), `split_lot_confident` (≥2 firm districts, cross-checked per §2.6), `boundary_uncertain` (any pair `near_boundary_uncertain` involving material lot area), `sliver_ambiguous`, `data_conflict` (§2.6), `invalid_geometry_review` (lot or district assessment was `review_required`/`invalid_geometry` per the M2-T009 taxonomy). Boundary **touch** (distance = 0, zero interior overlap) stays inside `near_boundary_uncertain` — the M2-T009 tests already prove touch is never material overlap (`test_mappluto_geometry_arcgis.py:882-890, 943-944`); preserve that exact behavior.

### 2.4 Split-lot percentage reporting: **ranges, not point values**

For each district d on a split lot report all three, in the lot's own area units:

- `share_min = area(lot ∩ erode(d,B)) / area(lot)`
- `share_point = area(lot ∩ d) / area(lot)` (the exact geometric result — preserved, labeled as the raw intersection)
- `share_max = area(lot ∩ dilate(d,B)) / area(lot)` (capped at 1.0)

Rules: the point values across districts sum to ~100% (assert within a small numeric epsilon); the min/max values do **not** sum to 100% and must not be renormalized — document this on the record. Any downstream deterministic rule that keys off a split percentage threshold (ZR split-lot provisions are an M4 rule matter, not this engine's) must receive the *range*; when the threshold falls inside [share_min, share_max], the rule result is `conditional`/`professional_review_required`, never a definitive pass/fail. Display: show the point value with the range ("62% (55–68%)"), never a naked point value when range width exceeds a display epsilon.

### 2.5 ZTLDB cross-check: agreement/disagreement semantics

Foundational asymmetry (both officially documented): the zoning-features layers are officially **not for lot-level determination** (`zoning_features_arcgis.py:56-58`), while ZTLDB is DCP's official per-lot assignment product — but ZTLDB has **no percentages** (schema `ztldb_soda.py:178-195`) and a suspected stale vintage (OQ-3). So: **ZTLDB is the authority for the district *set and ordering*; our geometry is the only source of *percentages*; neither alone yields a confident assignment.**

| Geometric result | ZTLDB says | Outcome |
|---|---|---|
| `single_district_confident` for d | `zoning_district_1 = d`, `zoning_district_2` blank (official "not divided" semantics, `ztldb_soda.py:231-234`) | **Confirmed assignment** — the only state eligible to feed a Verified rule result |
| `split_lot_confident` {d1, d2} | Same set; ZTLDB order matches our point-percentage order | **Confirmed split** — percentages still reported as ranges |
| `split_lot_confident` set matches, order differs | — | Downgrade to `conditional` with `ordering_disagreement` note (plausible when point percentages are close or vintages differ); NOT professional review by itself unless a rule depends on which district is primary |
| Any confident geometric result | ZTLDB set differs (extra/missing/different district) | **`data_conflict`** — never pick a winner. First compare vintages (nyzd `source_data_last_edited` vs ZTLDB row vintage): if they differ, tag `possible_vintage_skew` (OQ-3); either way → professional_review_required |
| `near_boundary_uncertain` | ZTLDB agrees with the more-probable side | **Upgrade to `conditional` at most** (see owner choice C2): display the ZTLDB assignment as the official lot-level record, retain the geometric-uncertainty flag; never upgrade to confident/verified, because ZTLDB itself derives from the same ±20 ft geometry chain — agreement between two products sharing lineage is corroboration, not independent confirmation |
| `near_boundary_uncertain` | ZTLDB says split but geometry finds no firm second area (or vice versa) | `sliver_ambiguous` + `data_conflict` note → professional_review_required |
| Anything | `zoning_district_1` absent (observed live, `ztldb_soda.py:217-220`) | Geometric-only result capped at `conditional`; professional review if not `interior_confident` |

Disagreement never *downgrades the geometry silently* and agreement never *erases the band*: both channels' raw values stay on the record (the conflict-visibility principle, PRD §9/§12).

### 2.6 `professional_review_required` — exact trigger set

1. Any lot whose overall class is `near_boundary_uncertain` or `sliver_ambiguous` where the uncertain area could change any applicable rule outcome (if rule sensitivity is unknown at this milestone: always).
2. Any ZTLDB set disagreement (`data_conflict`), including vintage-skew-suspected cases.
3. Geometric split where any share range [min, max] straddles a rule-relevant threshold (once M4 rules exist; until then, record the range and flag `threshold_sensitivity_unknown`).
4. Lot or district geometry assessment `review_required` / `invalid_geometry` (M2-T009 taxonomy) feeding the intersection.
5. `multiple_features` lot outcome, condo billing-lot ambiguity, or identifier conflicts from the lot channel (`mappluto_geometry_arcgis.py` safeguard 1).
6. `band_exceeds_feature_width` (§2.3) on a district the lot materially interacts with.
7. Any classification computed with a `basis: "assumed"` accuracy where the class would change if the true accuracy were 2× the assumed value (cheap to compute: reclassify once at 2B; if the class flips, review). This makes the undocumented-MapPLUTO-accuracy gap fail safe instead of silently optimistic.

Hard invariant (test it): **no code path maps `near_boundary_uncertain`, `sliver_ambiguous`, or `data_conflict` into a single definitive district assignment**, regardless of scores, percentages, or ZTLDB agreement.

---

## 3. Genuine owner choices (policy knobs)

Only four; everything else above is engineering.

**C1 — Tolerance combination rule.** Options: (a) linear sum (40 ft band today); (b) root-sum-square (~28.3 ft). **Recommended default: (a) linear sum** — reasons in §2.2. This is an owner choice because it trades analysis coverage (sum classifies more lots as uncertain → more review workload, fewer "clean" answers) against legal conservatism; that cost/risk balance is a business decision.

**C2 — Can ZTLDB agreement upgrade a geometrically uncertain lot?** Options: (a) no — ZTLDB agreement is a note only, class stays uncertain; (b) upgrade to `conditional` with the ZTLDB assignment displayed as the official lot-level record and the geometric uncertainty flag retained; (c) upgrade to confident. **Recommended default: (b).** (c) should be rejected: shared lineage means agreement is not independent evidence. Choice between (a) and (b) is genuinely the owner's: (b) produces materially more usable analyses, at the cost of leaning on a product whose vintage currency is unresolved (OQ-3).

**C3 — Sliver floor for `split_confident`.** The minimum firm (eroded) intersection area for a second district to count as a real split rather than a sliver. Options: (a) band-derived only — firm area must be > 0 after erosion by B (pure geometry, no extra constant); (b) additionally require the firm share to exceed a percentage of lot area (e.g., 1–2%); (c) additionally require an absolute area floor (e.g., B² = 1,600 sq ft). **Recommended default: (a) + report any district whose firm share is under 2% with a `minor_portion` flag rather than suppressing it.** How small a real split still matters is a legal/business judgment (ZR split-lot provisions can matter at any percentage), so the suppression threshold — if any — must be the owner's, and I recommend suppressing nothing.

**C4 — Split-percentage display form.** Options: (a) range only; (b) point + range (point labeled "exact intersection of mapped geometry"); (c) point only with an uncertainty footnote. **Recommended default: (b).** (c) contradicts the 2026-07-20 directive and should be rejected; between (a) and (b), how much numeric detail the analyst-facing UI carries is a product decision.

---

## 4. Facts I could NOT verify from the repo (verify in the task, do not assume)

- **V1 — MapPLUTO/DTM horizontal accuracy.** No accuracy figure exists anywhere in `docs/research/pluto-mappluto-2026-07-16.md` (only the general disclaimer, line 176) or elsewhere in the repo. M2-T009's 20 ft for lots is an analogy (`mappluto_geometry_arcgis.py:203-207`). The M2-T013 packet must include a G1-style source-verification step: read the official MapPLUTO FGDC metadata / `meta_mappluto.pdf` (and, if silent, the DOF Digital Tax Map metadata) for a stated positional accuracy. Until then MapPLUTO accuracy is `basis: "assumed"` and trigger §2.6(7) applies.
- **V2 — Per-layer accuracy for nyco/nysp/nysp_sd/nylh/nyzma.** OQ-5 is still OPEN (research line 257); the ±20 ft citation is documented for **nyzd only** (line 149). The five other layer metadata PDFs must be read before their accuracy records can say `documented`.
- **V3 — ZTLDB build methodology.** The 10%/50% assignment rules are documented for overlays/special districts (`ztldb_soda.py:243-259`) and ordering semantics for districts (lines 291–298), but the repo does not document *how* DCP computes the underlying percentages (which geometry vintage, any sliver handling). Needed before treating an ordering disagreement as anything stronger than a note.
- **V4 — ZTLDB vintage currency.** OQ-3 remains OPEN (research line 255): Socrata rows apparently frozen at 2026-04-05 while nyzd refreshes monthly. The cross-check's `possible_vintage_skew` tag depends on resolving what the reliable ZTLDB version signal is.
- **V5 — Legal split-lot treatment (ZR 77-11 et al.).** Nothing in this taxonomy is a legal determination; the geometric classes must feed the M4 rule engine as *facts with uncertainty*, and no class name should ever be surfaced as a zoning-law conclusion without a published rule and G6 review.

**Relevant paths:** `services/api/app/connectors/mappluto_geometry_arcgis.py`, `services/api/app/connectors/zoning_features_arcgis.py`, `services/api/app/connectors/ztldb_soda.py`, `services/api/tests/connectors/test_mappluto_geometry_arcgis.py` (lines 845–975), `project-control/reports/M2-T009-G4-geospatial-review.md` (O4), `docs/research/zoning-features-ztldb-2026-07-16.md` (lines 146–155, 232, 255–262), `docs/research/pluto-mappluto-2026-07-16.md` (lines 72, 176).

**Requested status:** advisory complete — no code changed, no ledger action needed from me. One project memory saved at `.claude/agent-memory/geospatial-engineer/project_source-accuracy-facts.md` (documented-vs-assumed accuracy facts and citations; stable technical learning only).
