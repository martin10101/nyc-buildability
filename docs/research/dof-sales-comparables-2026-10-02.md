# DOF sales — comparable-sales source (B-11, plan section 11b)

Queue item **B-11** (Lane B; plan `docs/PRODUCT_PLAN_CURRENT_2026-09-28.md` section 11b
"Comparable sales"; directive D-090). This note records the official source for the
comparable-sales slice, so no field name, type, unit or meaning is guessed (platform
principle 3; PRD sections 2, 9, 23.2).

## 1. Dataset

- **Name (verbatim):** NYC Citywide Annualized Calendar Sales Update
- **Publisher (`attribution`):** Department of Finance
- **NYC Open Data id:** `w2pb-icbu`
- **Description (verbatim):** "Annualized sales file displays yearly sales information of
  properties sold in New York City."
- **Resource endpoint:** `https://data.cityofnewyork.us/resource/w2pb-icbu.json`

## 2. Metadata capture (provenance)

- **Metadata URL:** `https://data.cityofnewyork.us/api/views/w2pb-icbu.json`
- **Retrieved:** 2026-10-02 (HTTP `Date`: Fri, 02 Oct 2026 11:02:48 GMT; keyless `curl` GET)
- **HTTP status:** 200; **bytes:** 52900
- **sha256 of the response body:**
  `8ee80fd8bdd4edd5122f2f3edffe86fbf4cb81cdaf8cb1e513e87a1de39e00a9`
- **Stored fixture:**
  `services/api/tests/fixtures/dof_sales_bayside/dof_sales_api_views_w2pb-icbu.json`
- **Data vintage** (from the two resource-query responses, header
  `X-SODA2-Truth-Last-Modified`): **Tue, 09 Jun 2026 18:31:52 GMT**.

The server also returns the authoritative column list and types in the `X-SODA2-Fields` and
`X-SODA2-Types` response headers; they match the metadata `columns` used below (29 columns).

## 3. Columns relied on (field name, type, verbatim description)

Types are the publisher's SODA types. "text" square-footage fields carry thousands
separators (e.g. `"10,075"`); the connector strips commas and parses to an int, and treats a
blank or `0` as "size not recorded" (never a real zero). `sale_price` is kept verbatim,
`0` included.

| Field (`fieldName`) | Type | Verbatim description |
|---|---|---|
| `bbl` | text | "The BBL (Borough, Block, and Lot) is a unique identifier for each tax lot in the City." |
| `borough` | text | "The name of the borough in which the property is located" |
| `neighborhood` | text | "DOF assessors determine the neighborhood name in the course of valuing properties." |
| `block` | text | "A Tax Block is a sub-division of the borough on which real properties are located" |
| `lot` | text | "A tax Lot is a subdivision of a tax Block and represents the property unique location" |
| `address` | text | "The street  address of the property as listed on the Sales File. Coop sales include the apartment in the address field" |
| `zip_code` | text | "The property's postal code" |
| `building_class_category` | text | "This identifies properties broad usage (e.g. One Family Home)." |
| `building_class_at_time_of` | text | "The building classification at the time of sale" |
| `residential_units` | number | "The number of residential units at the listed property" |
| `commercial_units` | number | "The number of commercial units at the listed property" |
| `total_units` | number | "The total number of units at the listed property" |
| `year_built` | number | "Year the structure on the property was built." |
| `land_square_feet` | text | "The land are of the property listed in square feet" |
| `gross_square_feet` | text | "The total area of all e floors of a building as measured from the exterior surfaces of the outside walls of the building , including the land area and space within any building structure on the property" |
| `sale_price` | number | "Price paid for the property" |
| `sale_date` | floating_timestamp | "A $0 sale price indicates that there was a transfer of ownership without a cash consideration." |
| `bin` | text | "The BIN (Building Identification Number) is a unique identifier for each building in the City." |

(Typos — "are" for "area", "all e floors" — are transcribed verbatim from the publisher's
metadata.)

**Load-bearing meaning:** the `sale_date` description is the official basis for treating a
`$0` `sale_price` as a transfer without cash consideration (a non-arms-length transfer), so
the selection filter excludes `$0` rows from market comparables by default.

## 4. Subject lot and the recorded sale

Subject: **215-16 Northern Boulevard**, Bayside, Queens, BBL **4073340070** (the B-01
benchmark lot). The dataset holds **one** sale row for it: a **$0 transfer** dated
**2018-01-18** of the pre-redevelopment store building (`building_class_at_time_of` K1,
`building_class_category` "22 STORE BUILDINGS", `gross_square_feet` "5,091"). PLUTO's current
record for the lot is a D6 elevator-apartment building with 38 residential units — so the
DOF-recorded sale is **stale relative to the current building**. Recorded faithfully; not
reconciled or interpreted. (See the fixture pack README.)

- Subject fixture (`build_by_bbl_url('4073340070', row_limit=50)`), sha256
  `a89c09293f975fd435a5180d56d9d075eff234489ea2dc898ab54547907d2fef`.
- Candidate fixture (`build_candidates_url('BAYSIDE', '22 STORE BUILDINGS', row_limit=12)`),
  sha256 `8ab62bba6b7b1eeec3c49edcd034060090e25726b20a5c9329afb33e10ad6aa0`.

## 5. The disclosed selection filter ("similar type and size") — a product choice

How comparables are chosen is a **product choice**, not a fact. The default filter
(`app.profile.parity.comparable_sales`) is simple and surfaced verbatim to the architect:

- **Similar type:** the same DOF `building_class_category` as the subject.
- **Similar size:** recorded `gross_square_feet` within **+/-50%** of the subject's.
- **Market sales only:** `$0` sales (transfers without cash consideration, per the official
  `sale_date` description) are excluded.
- **Not the subject:** the subject's own lot is excluded.
- Candidates with no recorded gross floor area are listed separately, never size-matched.

The comparables are presented as recorded sales with a disclosed filter, **never a
valuation**: no average, no price-per-square-foot and no estimate is computed.

**Open owner question (Q-B11-1):** confirm or change the selection filter — in particular
(a) the +/-50% size tolerance, (b) whether "type" should match the subject's *recorded* DOF
category or its *current* PLUTO use (they differ for this lot), and (c) whether to widen the
candidate query beyond one neighborhood + category.

## 6. 485-x — source pointers only (eligibility is a legal interpretation)

485-x is a **New York State tax-incentive program** (Real Property Tax Law §485-x,
"Affordable Neighborhoods for New Yorkers"). Eligibility, its affordability requirements and
any geographic zones are **legal determinations** set by State law and administered through
the City. Per the lane rules and platform principle 1, **no eligibility rule or zone
boundary is encoded here or anywhere in Lane B**, and none was taken from memory.

What Lane B records now: the program exists and is relevant to §11b parity. Official source
pointers to **register and verify under a future task** (not fetched or encoded here): the
RPTL §485-x statute text (NYS), and the administering City agency's official program page
(HPD / DOF). Until a qualified reviewer confirms them, any 485-x surface reads **"Check
needed."**

**Open owner question (Q-B11-2):** which official 485-x source(s) should Lane B register and
capture as research (statute vs City program page), and who confirms eligibility and any zone
boundaries (this stays a legal/G6 determination, never a data default)?

## 7. What this slice covers, and what remains

- **Covered:** the connector (`app.connectors.dof_sales_soda`), this research note with the
  official metadata/sha256/verbatim descriptions, recorded fixtures with provenance, typed
  and dated `SaleRecord`s, and the disclosed non-valuation selection filter; plus the
  unused-floor-area data stub (`app.profile.parity.unused_floor_area`) carrying the B-05
  input and "Not confirmed" (subject and neighbours).
- **Remains:** wiring comparables into the study/contract (a Lane C request, as B-06/B-10
  did); 485-x source capture + an eligibility owner decision (section 6); neighbours' actual
  existing-floor-area capture (the stub takes them as input; capturing neighbour filings is a
  later increment); confirming the selection filter (section 5). Lane B never computes a
  remaining or unused development capacity.
