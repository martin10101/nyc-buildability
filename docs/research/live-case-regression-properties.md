# Live-case regression properties (D-073-R005)

Standing record for the four real properties where the deployed analysis stopped during the
external (Codex) product review, kept as explicit regression cases. Rule (D-073-R005): each
case needs the precise stopping condition, its evidence, the affected calculations, and the
capability or information that resolves it; cause classes are distinguished (source
uncertainty / split zoning vs property-identity connection vs unsupported rule coverage vs
data-geometry problems vs implementation defects). A refusal can be CORRECT — protective
checks are never relaxed to produce more successful-looking results; fixes are new
capability, with a defensible basis, preserving protection against unsupported conclusions.

Status vocabulary matches the discovery backlog (D-069). This file records; the ledger and
backlog queue the work.

| # | Property | Known cause class (evidence) | Affected calculations | Resolving capability | Status |
|---|---|---|---|---|---|
| 1 | 1279 37th Street, Brooklyn | Cause class NOT yet pinned from repository records — the recorded facts are the built-FAR 2.61 vs residential-reference 3.00 distinction (labels corrected in an accepted packet); the review reports its live analysis stopped | Complete per-property computed allowance (FAR chain) | Pin the exact stopping condition from a live re-run + server logs, then classify | OPEN — investigation owed in the validation packet |
| 2 | 298 Wallabout Street, Brooklyn (BBL 3022647515) | Property-identity connection: condo BILLING lot (condono 1313, 75xx billing lot) absent from ZTLDB by design; the app honestly reports no data (DB-002; M5-T033 owner-confirmation; docs/WORKING_KNOWLEDGE.md walkthrough notes) | Zoning-lot lookup and everything downstream | Condo billing-lot → base land-lot resolution through authoritative records (ACRIS/DOF), BEFORE zoning-lot lookup; a D-059-R007 benchmark hard class | OPEN — capability packet (DB-002), priority set by D-073-R008 |
| 3 | 401 Columbia Street, Brooklyn | Cause class NOT yet pinned from repository records (candidate classes per the review: split zoning or boundary confidence) | Per-property computed allowances | Same investigation as #1; if split-zoning: refusing to guess is CORRECT (precedent DB-001, 350 Fifth Ave verified against city records); resolution = split-lot apportionment capability (ZR 77-series), legal research first | OPEN — investigation owed in the validation packet |
| 4 | 69-02 Kessel Street, Queens | Cause class NOT yet pinned from repository records (candidate: boundary-confidence limit) | Per-property computed allowances | Same investigation; boundary-confidence cases get data/logic investigation BEFORE any threshold change proposal | OPEN — investigation owed in the validation packet |

Standing findings that bind any resolution work:

1. A stopped analysis is not automatically a defect: the split-zoning refusal was verified
   correct against city records (DB-001). The correct-refusal outcome must stay a supported,
   explained product state: the interface owes the user WHAT condition stopped the answer,
   WHICH conclusions are affected, and WHAT would resolve it.
2. Prohibition (owner, D-073 item 5): protective thresholds are never relaxed merely to
   produce more successful-looking results.
3. These four cases join the fixed validation collection (D-073-R004) as
   expected-refusal / expected-specific-outcome rows where their cause class is confirmed;
   none is required to become a positive result in the street-data milestone.

Next action: the validation-collection packet (contracted after M5-T035 acceptance) runs the
four live re-runs, pins each stopping condition with server-log evidence, fills the cause
class column, and registers each case in the validation collection with its expected outcome.

---

## Part-1 authoritative-source records (extension, D-073-R005; retrieved 2026-09-18)

This section EXTENDS (does not replace) the provisional table above. It records, per property,
the resolved BBL(s), the precise stopping condition established from **authoritative sources
only**, the evidence + retrieval date, the affected calculations, the resolving capability, and
a cause-class. It was produced under the D-073-R004/R005 research dispatch with the explicit
constraint **do NOT consult or exercise the deployed product or its API** — so where the exact
internal step that refused can only be pinned by a live re-run + server logs, that pinning is
stated as an out-of-scope limitation and the classification is grounded instead in what the
authoritative zoning data itself determines. `NEVER collapse split zoning into one district`
and `NEVER relax a protective threshold to manufacture a positive` (D-073-R005 prohibition)
both continue to bind.

**Sources / channels used (all live-queried 2026-09-18):**
- PLUTO tabular SODA `64uk-42ks` (`https://data.cityofnewyork.us/resource/64uk-42ks.json`);
  channel version observed **26v2** (advanced from the 26v1 in the 2026-07-16 research capture).
  PLUTO `ResidFAR`/`BldgArea`/`LotArea` are **city reference / recorded-existing fields**, not
  the platform's calculated allowance (D-073-R006).
- ZTLDB tabular SODA `fdkv-4t4z` (`https://data.cityofnewyork.us/resource/fdkv-4t4z.json`) —
  the **authoritative lot-level** district-assignment source (per its dictionary; NYC GIS
  Zoning Features are "not intended for determining zoning at the individual tax lot level").
- NYC GIS Zoning Features **nyzd** ArcGIS layer
  (`services5.arcgis.com/GfwWNkhOj9bNBqoJ/.../nyzd/FeatureServer/0`) and **MAPPLUTO**
  ArcGIS layer (same org) for lot geometry / centroid / boundary intersection.
- Repo pinned snapshot **zr-12-10** (wide/narrow street; named overrides; digest
  `23a9ccad31f1081fd15de94d796c22d540e7e8bcfe986e64c9ba302bf8fa4fde`).

### Case 1 — 1279 37th Street, Brooklyn  → RESOLVED to BBL 3052960043

- **Resolved BBL(s):** **3052960043** (Brooklyn block **5296**, lot **43**). PLUTO **address of
  record = "3622 13 AVENUE"** (a corner lot at 37th St & 13th Ave), NOT "1279 37 Street".
- **Precise stopping condition (authoritative):** the entered address **"1279 37th Street" does
  not exist as a PLUTO/DTM tax-lot address** in 26v2. The 37th-St frontage of block 5296 runs
  1201–1277 with **lot 44 absent** between lot 45 (1277 37 St) and the 13th-Ave corner lots
  36–43; a query for `address like '1279 37%'` returns **[]** (empty) citywide. The building the
  review's figures describe is the **corner lot 43 (3622 13 Ave)**: its recorded **built
  FAR = 6271/2400 = 2.61** and **ResidFAR reference = 3.00** match the seed's "built 2.61 vs
  residential reference 3.00" exactly. That lot is **M1-2/R6A** within **Special Mixed Use
  District MX-12** (a paired manufacturing/residential district), not a plain residence district.
- **Evidence (retrieved 2026-09-18):** PLUTO `64uk-42ks` — no record for "1279 37 STREET";
  block-5296 enumeration shows lot 43 `address 3622 13 AVENUE, zonedist1 M1-2/R6A, spdist1 MX-12,
  residfar 3.00, bldgarea 6271, lotarea 2400` and lot 45 `1277 37 STREET, M1-2/R6A, MX-12`.
  ZTLDB `fdkv-4t4z` — `bbl 3052960043 → zoning_district_1 M1-2/R6A, special_district_1 MX-12`
  (lot 45 identical; lot 46 = plain R5).
- **Affected calculations:** the entire per-property computed-allowance chain (residential FAR
  and every downstream envelope element) — none can run correctly on the entered identity.
- **Resolving capability:** (a) an **authoritative address→DTM-lot identity** step that, for a
  range/corner address with no matching PLUTO address string, resolves to the governing DTM lot
  and surfaces its **address-of-record** so the user sees which lot was analysed; (b)
  **Special Mixed Use District (MX / ZR Article XII) FAR rule coverage** — currently the
  rulesets cover only R1–R12 residence districts (special-district FAR modifier is "not yet
  implemented").
- **Classification:** **incomplete/ambiguous property-identity connection** (address↔lot
  mismatch) **+ unsupported rule coverage** (MX paired M/R special mixed-use FAR out of scope).
  **A refusal is CORRECT.** Per D-073-R006 the residential reference **3.00 (R6A) must NOT be
  presented as the calculated allowance**, and the built FAR **2.61** is an existing-building
  reference, not an allowance. (Refines the seed row 1, which had not yet pinned the cause.)

### Case 2 — 298 Wallabout Street, Brooklyn  (BBL 3022647515) — CONFIRMED condo-identity gap

- **Resolved BBL(s):** **3022647515** (Brooklyn block **2264**, lot **7515** — a DOF **condo
  BILLING lot**, 7501–7599 range; **condono 1313**). Underlying land lot is one of block 2264's
  DTM lots (see below); its exact number needs ACRIS/DOF (not resolvable from the open datasets
  queried).
- **Precise stopping condition (authoritative):** **ZTLDB has NO row for BBL 3022647515**
  (query returns **[]**). ZTLDB block 2264 contains **39 land lots (1–74) and ZERO 75xx billing
  lots** — condo billing lots are absent from ZTLDB **by design**. The app's lot-level zoning
  lookup keys on ZTLDB, so it honestly returns **no data**. (PLUTO *does* carry the condo record
  — R7-1, conservative ResidFAR 3.44 — but PLUTO's condo aggregate is not the lot-level zoning
  source.)
- **Evidence (retrieved 2026-09-18):** ZTLDB `fdkv-4t4z?bbl=3022647515` → `[]`; ZTLDB block-2264
  enumeration → lots `1,2,3,4,5,7,10,15,18,21,22,23,24,25,29,30,32,33,40,44,45,47,48,49,50,51,52,
  53,55,57,59,61,63,65,66,67,68,69,74` (no 75xx). PLUTO `bbl 3022647515 → 298 WALLABOUT STREET,
  lot 7515, zonedist1 R7-1, residfar 3.44, condono 1313`.
- **Affected calculations:** the zoning-lot lookup and **everything downstream** (FAR, height,
  yards, setbacks).
- **Resolving capability:** **condo billing-lot → base land-lot resolution through authoritative
  records (ACRIS / DOF)** BEFORE the zoning-lot lookup (a D-059-R007 benchmark hard class).
  **Second-order dependency:** the base land lot is **R7-1**, a wide-street-conditional district
  — so even after identity resolves, the FAR still requires the **wide-street determination**
  (conservative 3.44 vs within-100-ft 4.00), never silently assumed (D-052).
- **Classification:** **incomplete property-identity connection** (condo billing BBL). Correct
  outcome = honest no-data / unresolved. (Confirms seed row 2.)

### Case 3 — 401 Columbia Street, Brooklyn  (BBL 3005250001) — split-zoning candidate REFUTED

- **Resolved BBL(s):** **3005250001** (Brooklyn block **525**, lot **1**; a large ~88,000 sq ft
  lot, 1-story building, built 1952).
- **Precise stopping condition (authoritative):** authoritative **lot-level** sources agree on a
  **single, rule-covered district R5** — ZTLDB `zoning_district_1 = R5` with **no ZD2, no
  overlay, no special district**; PLUTO `SplitZone = N`, `ZoneDist1 = R5`, `ZoneDist2 = null`;
  and the **nyzd polygon at the lot centroid = R5**. The lot's *bounding box* intersects four
  districts (M1-1, M1-2A/R7A, R5, R6) only because it is a large parcel at a complex
  multi-district junction — those neighbours lie **outside** the lot. Therefore the seed's
  candidate **"split zoning" is REFUTED**: this is not a genuine split. The most consistent
  remaining explanation for a prior stop is a **geometric-assignment boundary-confidence
  fail-closed** (an M2-T013 lot-polygon intersect near the junction can return an
  uncertain/sliver result and downgrade to professional_review_required) — but the **exact
  internal step cannot be pinned without a live re-run + server logs**, which this
  authoritative-sources research is barred from doing, so the class is **PROVISIONAL** at that
  level of detail while being **definitive** that it is not split zoning and not unsupported
  coverage.
- **Evidence (retrieved 2026-09-18):** ZTLDB `bbl=3005250001 → R5` (single); PLUTO
  `SplitZone N, R5, ResidFAR 1.50, LotArea 88000`; MAPPLUTO centroid (982821, 186259, EPSG:2263),
  `ZoneDist1 R5 / ZoneDist2 null / SplitZone N`; nyzd point-query at that centroid → `R5`; nyzd
  envelope-intersect over the lot bbox → `{M1-1, M1-2A/R7A, R5, R6}` (bbox over-capture).
- **Affected calculations:** per-property computed allowances (FAR + envelope). R5 **is** covered
  (`r5_residential_far`), so a reconciled identity would compute.
- **Resolving capability:** **reconcile the geometric district assignment with the authoritative
  lot-level ZTLDB** (ZTLDB is purpose-built for lot-level; nyzd is officially not); flag a true
  conflict only when ZTLDB itself carries a ZD2. **Boundary-confidence cases get data/logic
  investigation BEFORE any change proposal; do NOT relax any threshold** (D-073-R005). A
  professional-review refusal on *genuine* geometric uncertainty remains a CORRECT outcome.
- **Classification:** **data-geometry / boundary-confidence** (NOT split zoning; NOT unsupported
  coverage; NOT condo). (Corrects seed row 3's "split zoning or boundary confidence" candidate to
  **boundary-confidence only**.)

### Case 4 — 69-02 Kessel Street, Queens  (BBL 4032110010) — boundary-confidence, single R2

- **Resolved BBL(s):** **4032110010** (Queens block **3211**, lot **10**; small ~6,000 sq ft
  lot, 2.5-story single-family, built 1940; Forest Hills).
- **Precise stopping condition (authoritative):** authoritative lot-level sources agree on a
  **single, rule-covered district R2** — ZTLDB `zoning_district_1 = R2` (no ZD2/overlay/special);
  PLUTO `SplitZone = N`, `ZoneDist1 = R2`, `ZoneDist2 = null`; **nyzd at the lot centroid = R2**.
  The small lot's bbox touches `{R2, R3A, R4B}` (a nearby junction), but centroid + both
  authoritative sources resolve to R2. Same shape as Case 3: a geometric-assignment
  boundary-confidence fail-closed is the most consistent explanation, but the exact internal
  step **cannot be pinned without a barred product/server-log re-run** → class is **PROVISIONAL**
  at that detail, **definitive** that it is not split and not unsupported coverage.
- **Evidence (retrieved 2026-09-18):** ZTLDB `bbl=4032110010 → R2`; PLUTO `SplitZone N, R2,
  ResidFAR 0.75, LotArea 6000`; MAPPLUTO centroid (1024898, 199661, EPSG:2263) `ZoneDist1 R2 /
  ZoneDist2 null / SplitZone N`; nyzd point-query at centroid → `R2`; nyzd envelope-intersect →
  `{R2, R3A, R4B}`.
- **Affected calculations:** per-property computed allowances. R2 **is** covered
  (`r1_r2_r3_residential_far`), so a reconciled identity would compute.
- **Resolving capability:** same as Case 3 — trust the authoritative lot-level ZTLDB assignment;
  investigate geometry/logic before any threshold change; keep the fail-closed refusal available
  as a correct state on genuine uncertainty.
- **Classification:** **data-geometry / boundary-confidence** (NOT split). (Confirms seed row 4's
  boundary-confidence candidate and adds the authoritative single-R2 basis.)

### Cross-cutting notes and limitations

- **Two seed candidates corrected by authoritative data:** Case 3 (401 Columbia) is **not** split
  zoning (single R5 in ZTLDB, PLUTO, and centroid); Case 1 (1279 37th) is an **identity +
  unsupported-MX-coverage** case resolving to BBL 3052960043 (3622 13 Ave), not a bare FAR-label
  issue.
- **Cause-class map:** Case 1 = identity mismatch **+** unsupported coverage (correct refusal);
  Case 2 = property-identity (condo billing BBL) (correct no-data); Cases 3 & 4 = data-geometry /
  boundary-confidence (authoritatively single, rule-covered districts; NOT split).
- **Limitation (scope-bound):** the *exact* internal refusing step for Cases 3 & 4 was NOT pinned,
  because the dispatch forbids consulting the deployed product / server logs. The authoritative
  finding — clean single rule-covered district, split zoning refuted — stands regardless; the
  boundary-confidence sub-classification is the best-supported reading pending a permitted
  server-log re-run.
- **No threshold was proposed for relaxation.** Every "resolving capability" above is new
  capability (identity resolution, MX rule coverage, geometry↔ZTLDB reconciliation), never a
  loosened protective check (D-073-R005 prohibition).
