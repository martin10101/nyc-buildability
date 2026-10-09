# PLUTO FEMA flood-map flags — `firm07_flag` / `pfirm15_flag` official meaning

**Lane B · queue item B-09 (flood-meaning follow-up) · plan section 8a map-based rules ·
directive D-090 · 2026-10-02.**

Purpose: give the §8a flood hidden-issue item
(`services/api/app/profile/hidden_issue_flags/map_based_rules.py` `_flood`) an accurate,
sourced meaning for the two PLUTO FEMA flood-map flag columns, replacing the deliberately
weak "the flag's exact meaning is not verified" wording left by B-09 slice 3.

## Why a substitute source

The named PLUTO data dictionary **26v1 PDF**
(`https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_datadictionary.pdf`)
is **permissions-encrypted**; it returned raw compressed streams and could not be read, and
nothing was decrypted or bypassed (CLAUDE.md principle: never guess, never bypass). PDF
sha256 recorded by B-09 slice 3:
`d587cbe90bafad128c88f7dfab0ec6741d2735b20695e99b931fa0607aeaf3fe`.

The authoritative substitute is the publisher's own machine-readable per-column metadata in
the official **NYC Open Data** catalog entry for PLUTO — DCP publishes the field descriptions
there verbatim.

## Live retrieval (fetched for this note)

| Field | Value |
|---|---|
| URL | `https://data.cityofnewyork.us/api/views/64uk-42ks.json` |
| Method | `curl` GET, keyless, single request |
| Retrieval date | **2026-10-02** |
| HTTP status | `200` |
| HTTP `Date` header | `Fri, 02 Oct 2026 11:51:43 GMT` |
| Body sha256 | `e2898060ad159147f2c8c4a333c9689b5e9234cb86239106c5ca48941680d4c2` |
| Body bytes | `202683` |
| Dataset `name` | **Primary Land Use Tax Lot Output (PLUTO)** |
| `attribution` | **Department of City Planning (DCP)** |
| `attributionLink` | `https://www.nyc.gov/content/planning/pages/resources/datasets/mappluto-pluto-change` |
| "Current version" | **26v2** (verbatim from the dataset `description`: "Current version: 26v2") |
| `rowsUpdatedAt` | `2026-08-24T20:48:51Z` |

Committed excerpt fixture (the two column objects copied verbatim, plus this provenance):
`services/api/tests/fixtures/pluto_firm_flags/pluto_firm_flags_metadata_excerpt.json`
(sha256 `11b36fd3982444e79a0585775c3bd0757c24f52ccc4c48fc380b42d0a64f039f`), manifested in
`services/api/tests/fixtures/pluto_firm_flags/MANIFEST.json`.

## Verbatim field descriptions (from the live metadata `columns[]`)

**`firm07_flag`** — `fieldName` `firm07_flag`, `dataTypeName` **number**, position 89:

> A value of 1 means that some portion of the tax lot falls within the 1% annual chance
> floodplain as determined by FEMA's 2007 Flood Insurance Rate Map.
>
> Note that buildings on the tax lot may or may not be in the portion of the tax lot that is
> within the 1% annual chance floodplain.

**`pfirm15_flag`** — `fieldName` `pfirm15_flag`, `dataTypeName` **number**, position 90:

> A value of 1 means that some portion of the tax lot falls within the 1% annual chance
> floodplain as determined by FEMA's 2015 Preliminary Flood Insurance Rate Map.
>
> Note that buildings on the tax lot may or may not be in the portion of the tax lot that is
> within the 1% annual chance floodplain.

## Confirmation and what the wording may say

The live metadata **CONFIRMS** the descriptions (they also match, byte-for-byte, the earlier
`api/views` capture committed as `services/api/tests/fixtures/pluto/F08_api_views_columns_snapshot.json`,
retrieved 2026-07-16 by M1-T002). Supported, and now sourced:

- A value of 1 = **some portion of the tax lot** falls within the **1% annual chance
  floodplain** on the named FEMA map (2007 FIRM for `firm07_flag`; 2015 Preliminary FIRM for
  `pfirm15_flag`).
- Buildings on the lot **may or may not** be in that portion (lot-level, not building-level).
- Both columns are `dataTypeName` **number**; only the value 1 is defined (the metadata's
  `cachedContents` report largest = smallest = `1`). The description states no blank/0 meaning.

Not supported, so the wording claims none of it: no flood-**zone letter** (AE/VE/X…), no
**Appendix G** or flood-resilience height rule, no building-level certainty. The flood zone
stays a FEMA Flood Insurance Rate Map lookup; what it requires stays a rule-engine / G6
determination.

**Version gap (disclosed):** the named 26v1 PDF could not be opened, and the live dataset
self-reports `current_version` **26v2**, one release later. The flag field definitions are
stable across these releases; the gap is recorded here and in the fixture, not hidden. No
page citation from the 26v1 PDF is available because it could not be read.

## Sources

- `https://data.cityofnewyork.us/api/views/64uk-42ks.json` (DCP PLUTO metadata, NYC Open Data) — fetched 2026-10-02, sha256 above.
- `https://data.cityofnewyork.us/City-Government/Primary-Land-Use-Tax-Lot-Output-PLUTO-/64uk-42ks` (dataset landing page).
- `https://s-media.nyc.gov/agencies/dcp/assets/files/pdf/data-tools/bytes/pluto_datadictionary.pdf` (26v1 PDF — encrypted, unread).
