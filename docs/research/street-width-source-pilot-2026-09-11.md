# Street-width source pilot — confirm/kill, 2026-09-11

**Question:** can Geoclient's per-address `streetWidth` field answer the ZR wide-street test
(ZR 12-10: a wide street is 75 ft or more; captured at
`docs/research/zr-snapshots/v1/zr-12-10.snapshot.json`), and if not, what official source can?
Raised by MVP_AGENDA §B2 ("street-width source not chosen"), triggered by the G01 Geoclient
fixture carrying `streetWidth`.

**Verdict: Geoclient's field is KILLED for direct legal use; the Digital City Map (DCM)
Street Center Line dataset is CONFIRMED as the candidate legal-width source.** Pilot grade —
a full truth-set validation and an independent review are still owed before any rule consumes it.

## Evidence

1. **Same street, two numbers.** West 100 Street, Manhattan (the G01 fixture address):
   Geoclient `/v2/address` returns `streetWidth: 30` / `streetWidthMaximum: 30`
   (fixture `services/api/tests/fixtures/geoclient/G01_address_documented_example.json`,
   retrieved 2026-09-11). The DCM Street Center Line dataset returns **mapped width 60**
   for that street's segments. 60 ft is the standard Manhattan side-street mapped width;
   30 ft matches its paved roadbed. The two fields measure different things.
2. **Field definition (cited with a caveat).** Search-indexed text of the official LION
   metadata (https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/lion_metadata.pdf)
   defines StreetWidth as "the narrowest width, in feet, of the paved area of the street."
   The PDF's text layer would not extract locally (image-based), so this wording is
   search-derived, not byte-verified — verify verbatim during the full validation. The
   empirical 30-vs-60 result stands independently of the quote.
3. **The legal test measures the mapped street, not the pavement.** ZR 12-10's 75-ft
   threshold is about the street as mapped (property line to property line). A pavement
   width systematically under-reports it (W 100 St: 30 vs 60), which would flip legal
   answers near the 75-ft boundary in BOTH directions across the city.
4. **DCM Street Center Line pilot queries** (SODA dataset `g6zj-tzgn`,
   https://data.cityofnewyork.us/City-Government/DCM_StreetCenterLine/g6zj-tzgn, retrieved
   2026-09-11, tokenless, five KB-scale requests; the dataset self-describes as "official
   street names and widths shown on the Official City Map"):
   - West 100 Street, Manhattan → segments 60 (one segment 100 — segment variation is real)
   - 5 Avenue, Manhattan → predominantly 100 (one 29 segment; one **"Width Irregular"**)
   - Queens Boulevard → 200–240
   - Ocean Parkway, Brooklyn → 210 (including a `Paper_St` / `Unimproved` segment)
   All four match well-documented mapped widths. The dataset also carries per-segment
   MultiLineString geometry — the ingredient the eventual within-100-ft computation needs.

## Caveats the eventual connector MUST handle (found in a 5-query pilot)

- `streetwidt` is a STRING and can be non-numeric (`"Width Irregular"`) → fail closed to
  the conservative value, never parse-and-guess.
- Width varies per segment of one named street → the determination is per-segment/per-lot
  geometry, never per street name.
- Paper streets (`feat_statu: Paper_St`, `build_stat: Unimproved`) exist in the data →
  decide their legal treatment from the ZR text, not from assumption.
- The wide-street rule is "any portion of the zoning lot within 100 feet of a wide street"
  (ZR 23-22 footnote 1) — an around-the-corner, partial-lot geometry test. A fronting-street
  width alone cannot answer it; DCM geometry + lot geometry can.

## Next steps (in order, none started)

1. Full truth-set validation: 30–50 streets, all five boroughs, borderline-75-ft cases
   weighted, hand-checked against the Official City Map; byte-verify the LION definition.
2. Contract the DCM Street Center Line connector like every other connector (source_registry
   record, recorded fixtures including the irregular/paper cases, contract tests).
3. The wide-street determination task itself (lot geometry × street geometry × 100-ft
   buffer), consuming the connector; conservative lower-value behavior stays until it lands.
4. Geoclient `streetWidth` may serve as a free advisory cross-check flag only — never the
   legal answer.
