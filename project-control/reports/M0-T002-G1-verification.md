# Gate Report

- Gate ID: G1
- Task ID: M0-T002
- Reviewer: data-contract-verifier
- Producer: official-source-researcher
- Result: PASS
- Clean environment/worktree used: Read-only review of `docs/research/M0-T002-geoclient-address-resolution.md` at the current checkout; no repository files modified other than this report. All verification performed against live official sources on 2026-07-14, independently of the producer's citations.

## Acceptance criteria reviewed

- S1 (normal): current endpoint(s), auth model, rate limits, pagination/N-A, update cadence, field definitions for BBL/BIN resolution, with source URLs and retrieval date.
- S2 (conflicting-source): Geoclient vs GeoSearch both documented with official status, differences, and a recommendation.
- S3 (missing-data): unpublished details explicitly marked UNKNOWN; no guessed endpoints, fields, or units.

## Steps independently executed

All steps performed 2026-07-14 by this reviewer (not reusing the producer's fetches). Tooling note: shell network access and several domains (raw.githubusercontent.com, apps.nyc.gov content API, s-media.nyc.gov PDFs, medium.com) were blocked by sandbox policy; where a primary URL was unreachable, the same official artifact was verified via the official GitHub source repository or an official DCP web property.

1. Independently located the current official Geoclient documentation via web search (not the doc's links). Result: Geoclient User Guide v2.0.4 at `https://mlipper.github.io/geoclient/` — same source the producer used; no newer/other official doc found. Search also surfaced `https://api-portal.nyc.gov/` with title "Home - Microsoft Azure API Management - developer portal" (confirms Azure APIM portal claim).
2. Fetched `https://mlipper.github.io/geoclient/` (three targeted passes, page is large and fetch-truncated per pass):
   - Endpoints table / per-section `Path:` lines: `/v2/address`, `/v2/addresspoint`, `/v2/bbl`, `/v2/bin`, `/v2/blockface`, `/v2/normalize`, `/v2/place`, `/v2/search`, `/v2/streetcode`, `/v2/version` — all verified verbatim. Intersection section verified to print "Path: `/v2/blockface`" while its parameter table is titled "Table 11. `/intersection` arguments" — the internal inconsistency the doc flags is real.
   - Required params verified: `/address` houseNumber + street + (borough | zip); `/bbl` borough/block/lot; `/bin` bin; `/search` `input` plus defaults `exactMatchForSingleSuccess=false`, `exactMatchMaxLevel=3`, `returnPolicy=false`, `returnPossiblesWithExact=false`, `returnRejections=false`, `returnTokens=false`, `similarNamesDistance=8`.
   - Case-sensitivity sentence verified: "The Geoclient base URI and query parameter names are case-sensitive!" (values are not).
   - Address example verified: request `houseNumber=314&street=w%20100%20st&borough=manhattan`; response wrapped in `"address"`; `bbl` "1018890001", `buildingIdentificationNumber` "1057127", `houseNumber` "280", `firstStreetNameNormalized`/`boePreferredStreetName` "RIVERSIDE DRIVE", `latitude` 40.798502, `longitude` -73.972709, `xCoordinate` "0991806", `yCoordinate` "0230194", `dcpZoningMap` "5D", `message` "280 RIVERSIDE DRIVE IS ON RIGHT SIDE OF WEST 100 STREET" — vanity-address normalization claim confirmed exactly.
   - `/bbl` example verified: `bblTaxBlockIn` "67", `bblTaxLotIn` "1", `bblTaxBlock` "00067", `bblTaxLot` "0001", `bbl` "1000670001", BIN "1079043". `/bin` example verified: `bbl` "1000670001".
3. Auth section verified from the official repo source (guide page truncated before section 7): `https://github.com/mlipper/geoclient/blob/main/documentation/src/docs/asciidoc/parts/public-endpoint.adoc` — "Sponsored by NYC's Office of Technology and Innovation, the Geoclient REST service is freely available to the public on the NYC API Developers Portal"; header `Ocp-Apim-Subscription-Key` (primary), `key` query-string parameter (unofficial alternate); sign-up steps including "Make sure to choose the subscription to 'Geoclient - v2' as v1 is deprecated and scheduled for deactivation"; no rate-limit/quota statement present.
4. Base URL verified from `https://github.com/mlipper/geoclient-examples` README: "the default for the Geoclient v2 base endpoint URL: `https://api.nyc.gov/geoclient/v2`", with examples using the `Ocp-Apim-Subscription-Key` header and `-qs` variants using the `key` parameter.
5. Provenance chain verified: `https://github.com/CityOfNewYork/geoclient` displays "This project has moved to mlipper/geoclient"; `https://github.com/mlipper/geoclient` README states Geoclient "relies on Geosupport, NYC's official geocoder of record ... a separate application written and maintained by the Department of City Planning".
6. GeoSearch official docs fetched: `https://geosearch.planninglabs.nyc/docs/` — base `https://geosearch.planninglabs.nyc/v2/`, endpoints `/search` and `/autocomplete` only (no reverse documented), no API key, no rate-limit statement, GeoJSON output, default 10 results with `size` parameter, "Spelling matters, but not capitalization." Operator/PAD basis verified from `https://github.com/NYCPlanning/labs-geosearch-docs` (NYCPlanning org): "NYC GeoSearch is an API that transforms input text ... using authoritative NYC address data from the [Property Address Directory (PAD)]"; "powers the autocomplete/typeahead search results in web apps such as ZoLa and Population Fact Finder".
7. Live keyless request executed (one small GET, no credentials): `https://geosearch.planninglabs.nyc/v2/search?text=120%20broadway&size=1`. Excerpt of returned JSON:
   - `"engine":{"name":"Pelias","author":"Mapzen","version":"1.0"}`
   - first feature `geometry.coordinates`: `[-74.010542, 40.708233]`
   - `properties.borough` "Manhattan", `properties.postalcode` "10271"
   - `properties.addendum.pad`: `bbl` "1000477501", `bin` "1001026", `version` "26a"
   This matches the producer's captured fixture (same BBL/BIN/PAD version for 120 Broadway) and proves: keyless access works, BBL/BIN are returned in `addendum.pad`, and the PAD version exposed ("26a") lags the current 26B release exactly as the doc reports.
8. Release/cadence checks: `https://geoservice.planning.nyc.gov/` (official DCP site, fetched directly) self-describes as "a RESTful web service interface to the NYC Department of City Planning's core Geosupport system", reports running "Geosupport Version 26B", requires registration/`Key=` — confirms current release naming 26B and the Geoservice claims. Official DCP PAD user guide (`padgui.pdf` on s-media.nyc.gov, surfaced via site:nyc.gov search; direct PDF fetch blocked by sandbox) states PAD is released under BYTES of the BIG APPLE four times a year, with UPAD updates deployed approximately every two weeks between quarterly Geosupport releases — confirms quarterly cadence + biweekly interim updates. `https://nycplanning.github.io/Geosupport-UPG/overview/` verified: "Geosupport Desktop Edition (Windows 32-bit and 64-bit; LINUX)" and TPAD provides "BIN and status information for Functions 1A, 1B, BL and BN".
9. Field-semantics cross-check against the official Geosupport UPG: `https://nycplanning.github.io/Geosupport-UPG/appendices/appendix03/` verified verbatim: "The latitude and longitude of a location are calculated based on the spatial coordinates (x,y) returned for that location. As a result, the latitude and longitude returned by the Address Processing functions (e.g. 1/1E Extended) will be somewhat different from the values returned by Tax Lot and Building processing functions (e.g. 1A/BL/BN)." and "For NYC, Latitude is always positive and Longitude is always negative." The SPC-zone sentence ("New York-Long Island zone, NAD 83", one unit = one foot) sits beyond the fetch tool's page-size truncation and could not be re-quoted directly; it is corroborated by (a) the EPSG registry (EPSG:2263 "NAD83 / New York Long Island (ftUS)" covering Bronx/Kings/New York/Queens/Richmond counties), and (b) search-indexed copies of the DCP text containing the exact phrase. No contradiction found; the doc's attribution is credible and it correctly marks the EPSG mapping itself as UNKNOWN (no official NYC page states an EPSG code).
10. UNKNOWN spot-checks (two, as required, plus one incidental):
    - Official rate limits (doc UNKNOWN #1): confirmed no rate limit/quota stated in the User Guide, in `public-endpoint.adoc`, or in GeoSearch docs; portal quotas sit behind sign-in. UNKNOWN is genuine for v2. Incidental finding: the 2,500 req/min / 500,000 req/day figure the doc labels third-party/unverified matches guidance historically published in official *v1*-era documentation ("guidelines and not hard limits") that search engines still surface; the currently reachable legacy doc page (`http://mlipper.github.io/geoclient-api-doc/`, "Geoclient API v1 (BETA)") no longer shows it. The doc's handling (treat as unverified, confirm inside the portal) is sound.
    - v1 deactivation date (doc UNKNOWN #2): current guide/changes sources (`parts/changes.adoc`: "Geoclient v1 has reached end-of-life status and will be deactivated"; "Geoclient is moving all its OTI datacenter-hosted service endpoints to the Azure cloud and deactivating all legacy, unsupported API versions") publish no date. A superseded official changes page (still in search indexes at the now-404 `docs/current/user-guide/changes.html`) announced an October 1st, 2025 shutdown for hosted /geoclient/v1 endpoints; that date has passed while v1 still answers (see next item), so no currently valid published date exists. UNKNOWN is defensible; see Defects note D2.
    - Reproduced the doc's 401 evidence: unauthenticated GET `https://api.nyc.gov/geoclient/v1/doc/` returned HTTP 401 on 2026-07-14 for this reviewer as well.

## Expected versus actual

| Claim in doc | Independent result | Match |
|---|---|---|
| Base URL `https://api.nyc.gov/geoclient/v2` | geoclient-examples README (official maintainer repo) | Yes |
| Auth header `Ocp-Apim-Subscription-Key`; alternate `key` param | public-endpoint.adoc in official repo | Yes (verbatim) |
| `/v2/address`, `/v2/bbl`, `/v2/bin`, `/v2/search` paths + params + defaults | User Guide v2.0.4 | Yes (verbatim) |
| Intersection path inconsistency ("Path: /v2/blockface" vs "Table 11. /intersection arguments") | User Guide v2.0.4 | Yes — inconsistency is real; doc correctly refuses to guess |
| Example values (bbl 1018890001, BIN 1057127, 314 W 100 St → 280 Riverside Dr, x/y, dcpZoningMap 5D) | User Guide examples | Yes (exact) |
| GeoSearch official (Planning Labs), keyless, `/v2/search` + `/v2/autocomplete`, GeoJSON, BBL/BIN in `addendum.pad` | Docs + labs-geosearch-docs README + live keyless GET | Yes (live response: bbl 1000477501, bin 1001026, version "26a") |
| PAD/Geosupport quarterly; naming `<YY><A-D>`; current 26B; UPAD/TPAD biweekly | DCP padgui.pdf (via official search surface), geoservice.planning.nyc.gov "Geosupport Version 26B", UPG overview | Yes |
| x/y = SPC NAD83 New York–Long Island, one unit = one foot; lat/long derived from x/y; precision caveats | UPG Appendix 3 (partially verbatim; SPC sentence corroborated, not re-quoted — see step 9) | Yes, with tooling caveat |
| v1 exists behind auth (401) | Reproduced HTTP 401 | Yes |
| UNKNOWNs genuinely unpublished (rate limits, v1 date spot-checked) | No official current publication found | Yes, with notes D2/D3 |

## Evidence paths

- Subject: `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\docs\research\M0-T002-geoclient-address-resolution.md`
- Task packet: `C:\Users\MLFLL\Downloads\nyc zoning\nyc-development-feasibility-claude-pack\project-control\tasks\M0-T002.json`
- URLs fetched (2026-07-14): https://mlipper.github.io/geoclient/ ; https://github.com/mlipper/geoclient ; https://github.com/mlipper/geoclient-examples ; https://github.com/mlipper/geoclient/blob/main/documentation/src/docs/asciidoc/parts/public-endpoint.adoc ; https://github.com/mlipper/geoclient/blob/main/documentation/src/docs/asciidoc/parts/changes.adoc ; https://github.com/CityOfNewYork/geoclient ; https://geosearch.planninglabs.nyc/docs/ ; https://geosearch.planninglabs.nyc/v2/search?text=120%20broadway&size=1 (live keyless) ; https://github.com/NYCPlanning/labs-geosearch-docs ; https://geoservice.planning.nyc.gov/ ; https://nycplanning.github.io/Geosupport-UPG/appendices/appendix03/ ; https://nycplanning.github.io/Geosupport-UPG/overview/ ; https://nycplanning.github.io/Geosupport-UPG/appendices/glossary/ ; https://api.nyc.gov/geoclient/v1/doc/ (401) ; http://mlipper.github.io/geoclient-api-doc/ ; plus web searches (incl. site:nyc.gov for padgui.pdf and api-portal.nyc.gov title).

## Human-style walkthrough findings

Following the doc as a connector implementer: the base URL + header name + endpoint paths + required parameters are sufficient to write the Geoclient client without guessing; the doc's instruction to resolve the intersection path via a live keyed call before implementing is the correct conservative behavior given the official guide's own inconsistency. The GeoSearch fallback is immediately reproducible without credentials (this reviewer reproduced it in one request). The human key-acquisition steps match the official public-endpoint.adoc word-for-word.

## Regression/security/provenance findings

- No secrets, keys, or authenticated calls in the doc; fixture plan explicitly excludes keys from stored headers.
- Every material claim carries a source URL and a retrieval date (source register, section 10); spot-checked claims traced back to those sources accurately; quotes verified verbatim where reachable.
- No endpoint, field, or unit was guessed; all 11 UNKNOWNs are genuine gaps or correctly flagged ambiguities (two spot-checked in depth, one incidentally reproduced).

## Defects

None gating. Notes (non-blocking):

1. D1 (minor, cosmetic): Doc says Geoservice exposes "16 raw Geosupport functions"; the live Geoservice site enumerates additional function variants (e.g., 1L, 2 with node IDs) beyond the 14 named in the doc's list. Count/enumeration should be re-checked when/if the Geoservice fallback is implemented. No impact on the recommended Geoclient/GeoSearch path.
2. D2 (minor, informational): A superseded official Geoclient changes page announced an October 1st, 2025 shutdown for hosted /geoclient/v1 endpoints; current official pages publish no date and v1 still answers 401 behind the gateway. The doc's "UNKNOWN — requires verification" for the v1 deactivation date is accurate for current sources, but a sentence noting the stale previously-published date would add context. No implementation impact (doc already mandates v2).
3. D3 (minor, informational): The 2,500/min & 500k/day figure the doc attributes to a third-party repo also matches historically published official v1-era guidance ("guidelines and not hard limits"). For v2 the limits remain unpublished, so the doc's UNKNOWN stands; recording the v1-era provenance would strengthen the note.
4. D4 (cosmetic): The PAD-basis quote for GeoSearch lives in the labs-geosearch-docs README, not on the /docs page itself; the doc cites both jointly. Attribution could be split more precisely. The `addendum.pad` behavior is independently proven by the live response regardless.

## Required rework

None required for gate passage. Optional editorial improvements per D1–D4 may be folded into any future revision.

## Reviewer conclusion

PASS. Every contract-critical claim was independently re-verified against official sources located by this reviewer: Geoclient v2 base URL, `Ocp-Apim-Subscription-Key` header, `/address`, `/bbl`, `/bin`, `/search` paths/parameters/defaults, example field values (including vanity-address normalization and BBL padding semantics), GeoSearch v2's official Planning Labs operation, keyless access, and BBL/BIN in `addendum.pad` (confirmed by a live request), quarterly PAD/Geosupport cadence with 26B naming (confirmed on DCP's own Geoservice site and PAD guide), and the NAD83 New York–Long Island state-plane-feet coordinate semantics (verbatim in part, corroborated in whole). The doc's UNKNOWN discipline is genuine — spot-checked items are indeed unpublished in current official sources — and the one place the official guide contradicts itself (intersection path) is flagged rather than guessed. The four notes above are minor/cosmetic and cannot mislead connector implementation.
