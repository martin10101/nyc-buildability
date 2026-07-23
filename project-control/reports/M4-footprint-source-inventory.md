# M4 footprint — CLOSED source inventory (SHARED across M4-T007..T010)

Every material section for the R5-series footprint dimensions (front/side/rear yards, rear-yard
equivalents, max lot coverage) is classified below. **Zero unresolved entries — no question marks.**
Raw-HTML-verified from `zr.planning.nyc.gov` (2026-07-23). All numeric values remain `[CANDIDATE]`
pending the gated producer's byte-level verification and G6.

**Legend:**
- **captured-controlling** — verbatim text MUST be snapshotted (byte-identical + hash); it drives an
  emitted constraint, an applicability gate, or a definition the rules depend on.
- **captured-context-only** — snapshotted for context/definition; emits NO footprint dimension.
- **excluded** — NOT captured/evaluated; carries the NAMED fail-closed limitation stated in the row
  (the packet surfaces `professional_review_required` / a `documented_limitation` for that condition;
  no value is emitted for it).

## Primary sections

| § | Exact title | Classification | If excluded: named fail-closed limitation |
|---|---|---|---|
| 23-01 | Applicability of This Chapter | **captured-controlling** (applicability gate: residential building/portion) | — (CF portion routes to §24-04/§24-05 exclusion below) |
| 23-11 | Lot Area and Lot Width Regulations in R1 Through R5 Districts | **captured-controlling** (supplies the lot-width threshold §23-334 depends on) | — |
| 23-311 | Permitted obstructions in all yards, courts and open areas | **captured-context-only** | — |
| 23-312 | Additional permitted obstructions generally permitted in all yards | **captured-context-only** (carries front-yard parking prohibitions = occupancy, outside dimensional scope) | — |
| 23-313 | Level and measurement of yards | **captured-controlling** (measurement basis for every yard dimension) | — |
| 23-321 | Basic front yard requirements in R1 through R5 Districts | **captured-controlling** (front-yard constraint) | — |
| 23-331 | Permitted obstructions in certain side yards | **captured-context-only** | — |
| 23-332 | Basic side yard requirements in R1 through R5 Districts | **captured-controlling** (side-yard constraint) | — |
| 23-333 | Modified side yard requirements for qualifying residential sites | **captured-controlling** (QRS-gated side-yard) | — |
| 23-334 | Modified side yard requirements for existing narrow zoning lots | **captured-controlling** (narrow-lot side-yard, gated on §23-11 width + pre-1961) | — |
| 23-341 | Permitted obstructions in required rear yards or rear yard equivalents | **captured-context-only** | — |
| 23-342 | Rear yard requirements | **captured-controlling** (rear-yard constraint, interior lots) | — |
| 23-343 | Rear yard equivalent requirements | **captured-controlling** (RYE constraint, through lots) | — |
| 23-344 | Additional rear yard modifications | **captured-controlling** (rear-yard/RYE modifications) | — |
| 23-361 | Maximum lot coverage in R1 through R5 Districts | **captured-controlling** (lot-coverage constraint) | — |
| 23-363 | Special rules for certain interior or through lots | **captured-controlling** (coverage modifications) | — |
| 23-425 | Height and setback modifications for large sites | **excluded** | Large-site eligibility/envelope not evaluated → captured coverage/RYE values do NOT reflect §23-425 large-site modifications (incl. the 50% MF coverage cap) → `professional_review_required` when large-site status is signalled. |
| 23-434 | Height and setback modifications for eligible sites | **excluded** | Eligible-site alternative RYE location not evaluated → standard RYE location applied; §23-434-based alternatives → `professional_review_required`. |
| 23-435 | Tower regulations | **excluded** | Tower-based alternative RYE location not evaluated → `professional_review_required`. |
| 23-38 | Special Rules for Certain Areas | **captured-context-only** (heading/scope marker) | — |
| 23-381 | Special provisions in other geographies | **excluded** | Public-park window/light-air rule (discretionary Parks determination); governs window-to-lot-line distance, NOT yard depth or lot coverage → not evaluated. |
| 23-71 | Predominantly Built-up Areas | **excluded** | Alternative bulk modifies FAR/height, not the captured footprint dimensions; a site electing §23-71 is not modeled → `professional_review_required` if flagged. |
| 23-72 | Portions of Community District 12 in the Borough of Brooklyn | **excluded** | Geographic alternative-bulk override not evaluated → CD12-Brooklyn lots carry `professional_review_required`; citywide yard values may be superseded there. |
| 23-723 | Yard modifications (CD12 Brooklyn, under §23-72) | **excluded** | CD12-Brooklyn yard modifications not evaluated → `professional_review_required` for CD12-Brooklyn lots. |
| 11-25 | District Designations Appended with Suffixes | **captured-controlling** (per-variant applicability rule; rules must cite it — see the §11-25 applicability decision) | — |
| 11-122 | Districts established | **captured-context-only** (informs building-type applicability) | — |
| 12-10 | Definitions (yard-relevant subset) | **captured-controlling** (see the definition sub-table) | — |

## §12-10 definitions (snapshot each individually — distinct `last_amended` provenance)

| Defined term | Drives | Last Amended |
|---|---|---|
| corner lot | lot-type routing; corner coverage/front-yard/rear-yard rules | 5/20/1965 |
| interior lot | lot-type routing (rear yard §23-342) | 12/15/1961 |
| through lot | lot-type routing (RYE §23-343) | 12/15/1961 |
| lot width | §23-11 / §23-334 / §23-321-QRS / §23-342 thresholds | 12/15/1961 |
| zoning lot | tax-lot vs zoning-lot area/width (readiness matrix row 3/5) | 2/2/2011 |
| qualifying residential site | §23-333 / §23-321 / coverage QRS gates | 12/5/2024 |

*(The lot-type/lot-width definitions predate City of Yes and are stable; only the QRS definition was
amended 2024-12-05. `wide street`/`narrow street` were already captured in M4-T006's `zr-12-10`
snapshot — reuse/extend, do not re-fork.)*

## Sections cited WITHIN the yard/coverage section text

| § | Exact title | Classification | Note / limitation |
|---|---|---|---|
| 23-34 | Rear Yard and Rear Yard Equivalent Requirements (heading) | captured-context-only | Members 341/342/343/344 classified individually. |
| 23-41 | Permitted Obstructions (heading) | captured-context-only | Obstruction cross-ref; no dimension. |
| 23-62 | Balconies | captured-context-only | Conditions a permitted obstruction; no dimension. |
| 23-362 | Maximum lot coverage in R6 through R12 Districts | **excluded** | R6–R12, not R5 → not evaluated in the R5 packet. |
| 25-621 | Location of parking spaces in certain districts | **excluded** | Parking-location (front-yard occupancy), not yard depth/coverage → not evaluated. |
| 25-622 | Location of parking spaces in lower density growth management areas | **excluded** | As above → not evaluated. |
| 25-85 | Floor Area Exemption | **excluded** | Floor-area exemption; out of footprint scope → not evaluated. |
| 26-50 | Special Screening and Enclosure Provisions | **excluded** | Screening rule; out of scope → not evaluated. |
| 24-04 / 24-05 | Applicability of Art II Ch 3 / Buildings containing certain community facility uses | **excluded** | Community-facility bulk → Art II Ch 4, not evaluated; a CF building/portion → `professional_review_required`. |

## Per-task snapshot sets (captured-controlling + captured-context-only for that task)

- **M4-T007 (coverage):** §23-361, §23-363 (controlling) · §23-01, §11-25, §12-10 {corner lot,
  interior lot, through lot, lot width, zoning lot, qualifying residential site} (gate/defs) ·
  §11-122 (context). Excluded→PRR: §23-425, §23-362, §24-04/05.
- **M4-T008 (rear + RYE):** §23-342, §23-343, §23-344 (controlling) · §23-313, §23-341, §23-34
  (context) · §23-01, §11-25, §12-10 {interior lot, through lot, corner lot, lot width, zoning lot}
  (gate/defs). Excluded→PRR: §23-425, §23-434, §23-435, §23-72/§23-723, §24-04/05.
- **M4-T009 (front):** §23-321 (controlling) · §23-313, §23-312 (context) · §23-01, §11-25, §12-10
  {corner lot, lot width, zoning lot, qualifying residential site} (gate/defs). Excluded→PRR:
  §23-72/§23-723, §24-04/05. Off-lot adjacency (§23-321 line-up) → PRR (no canonical source).
- **M4-T010 (side):** §23-332, §23-333, §23-334 (controlling) · §23-11 (controlling — width threshold)
  · §23-331, §23-313 (context) · §23-01, §11-25, §11-122, §12-10 {lot width, zoning lot, qualifying
  residential site} (gate/defs). Excluded→PRR: §23-72/§23-723, §24-04/05. §23-332 paragraph-scope →
  professional-review note (see §11-25 applicability decision).
