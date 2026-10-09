# PLUTO FEMA flood-map flags — publisher field descriptions (B-09 flood item)

B-09 flood-meaning follow-up (Lane B; plan `docs/PRODUCT_PLAN_CURRENT_2026-09-28.md` section
8a "Map-based rules"; directive D-090). Dataset: **Primary Land Use Tax Lot Output (PLUTO)**
(NYC Open Data `64uk-42ks`, publisher **Department of City Planning (DCP)**). Research note
with the official metadata URL, sha256 and the verbatim field descriptions relied on:
`docs/research/pluto-firm-flags-2026-10-02.md`.

This pack carries the publisher's own field descriptions for the two PLUTO FEMA flood-map
flag columns, `firm07_flag` and `pfirm15_flag`, which give the §8a flood hidden-issue item an
accurate, sourced meaning. The named 26v1 PLUTO data-dictionary **PDF is permissions-encrypted
and was not read or bypassed**; this machine-readable `api/views` metadata is DCP's official
substitute.

- **Capture:** 1 response on **2026-10-02 UTC**. `curl` GET, keyless, metadata endpoint.
- **Excerpt, not the whole body:** the full 202,683-byte `api/views` body is not small, so it
  is not committed; its sha256 (`full_body_sha256` in `MANIFEST.json`) is recorded instead.
  The committed file is a verbatim excerpt — the two column objects copied byte-faithfully
  from the live `columns[]` array, wrapped with dataset-level provenance.
- **Provenance:** `MANIFEST.json` records the dataset id, source id, the exact URL,
  `retrieved_at` (from the HTTP `Date` header), the HTTP status, byte count and the excerpt's
  sha256, plus the full body's sha256.
- **Integrity:** `services/api/tests/profile/test_map_based_rules.py` re-hashes the excerpt
  and pins the verbatim descriptions, so a metadata change is visible. `.gitattributes`
  (`-text`) keeps the bytes exact.

## What is here

| File | Finding |
|---|---|
| `pluto_firm_flags_metadata_excerpt.json` | The `firm07_flag` and `pfirm15_flag` columns: both `dataTypeName` **number**, each with DCP's verbatim description. A value of 1 means **some portion of the tax lot** falls within the 1% annual chance floodplain on FEMA's **2007 FIRM** (`firm07_flag`) / **2015 Preliminary FIRM** (`pfirm15_flag`); buildings on the lot **may or may not** be in that portion. Only the value 1 is defined (the `cachedContents` largest and smallest are both `1`). |

## Boundaries (recorded, never crossed here)

- **Lot-level, not building-level.** The description itself says a flagged lot's buildings may
  or may not sit in the floodplain portion of the lot; the flood item says no more.
- **No zone letter, no Appendix G.** The metadata names the 1% annual chance floodplain and
  the FEMA map vintage; it does not assign a flood-zone letter or any flood-resilience height
  rule. Those stay a FEMA-map lookup and a rule-engine / G6 determination, not decided here.
- **Version gap disclosed.** The live dataset self-reports `current_version` 26v2, one release
  past the named 26v1 PDF; the field definitions are stable across these releases.
