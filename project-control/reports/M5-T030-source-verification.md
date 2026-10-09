# Independent source verification

Verbatim return from source_verifier; no implementation verdict.

Verified the fixed PLUTO JSON link approach for both lots.

| Check | Result |
|---|---|
| [Brooklyn lot record](https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=3021720001) | HTTP 200; exactly one row; BBL `3021720001`; `83 TAYLOR STREET`; `lotarea=116000`; `bldgarea=341300`; `version=26v2`. Retrieved September 15, 2026, 00:28:17 UTC. |
| [Empire State Building lot record](https://data.cityofnewyork.us/resource/64uk-42ks.json?bbl=1008350041) | HTTP 200; exactly one row; BBL `1008350041`; `338 5 AVENUE`; `version=26v2`. Retrieved September 15, 2026, 00:29:14 UTC. |

The Empire State Building’s BBL was independently derived from the [official LPC designation report](https://s-media.nyc.gov/agencies/lpc/lp/2000.pdf), whose first page identifies **350 Fifth Avenue, Manhattan, block 835, lot 41**. The PDF returned HTTP 200. Combining those components using the [official PLUTO BBL definition](https://data.cityofnewyork.us/api/views/64uk-42ks.json) produces `1008350041`.

The current Empire State Building row contains these raw source values:

| Fields | Values |
|---|---|
| `lotarea` / `bldgarea` | `91351` / `2812739` |
| `comarea` / `officearea` / `retailarea` | `2812739` / `2685483` / `127256` |
| `resarea` / `numfloors` / `yearbuilt` | `0` / `102.0000000` / `1931` |
| `zonedist1` / `zonedist2` | `C5-3` / `C6-4.5` |
| `spdist1` / `splitzone` | `MiD` / `true` |
| `landmark` | `INDIVIDUAL AND INTERIOR LANDMARK` |
| `builtfar` / `commfar` | `30.79000000000` / `15.00000000000` |

These are source fields, not evaluated development permissions.

The address-only request for `350 5 AVENUE` returned zero rows. PLUTO documents that its address can be the lowest address in a range; therefore the differing `338 5 AVENUE` label does not establish a lot mismatch. Use the verified BBL relationship.

Recommend:

- Label the link **“Current PLUTO record (JSON)”**, with “About this dataset” separately.
- Construct it from a fixed official prefix and canonical BBL matching `^[1-5][0-9]{9}$`.
- Require a known PLUTO source, dataset `64uk-42ks`, and matching `record.bbl` and `profile.identity.bbl`.
- Allow missing per-record dataset fallback only when reproducibility metadata belongs to the same proven source.
- For non-PLUTO, missing, malformed, or mismatched identities, omit the exact-lot link. Preserve source text and any independently valid dataset link.
- Never build the URL from reflected `request_url`.
- Preserve captured values, version, retrieval time, and digest metadata. The public link queries today’s dataset; it does not recover an immutable captured report snapshot.

The [Socrata endpoint documentation](https://dev.socrata.com/docs/endpoints.html) now emphasizes SODA3 and identifies `/resource/IDENTIFIER.json` as its predecessor. The two tokenless requests above verified that predecessor endpoint’s behavior directly. I did **not** establish an officially documented, stable filtered-table deeplink in this bounded check.

For architects, this supports checking lot identity, comparing captured facts with current city records, and spotting source flags requiring further review. It does not establish legal conclusions or measured time savings.

No files, repository state, or external records were changed. This verifies sources and linking assumptions; it does not verify the new frontend implementation or full application workflow.
