# M0-T002 — Official-Source Research: NYC Address/BBL/BIN Resolution

- **Task:** M0-T002 — Official-source discovery: NYC address/BBL/BIN resolution (Geoclient/Geosupport/GeoSearch)
- **Producer agent:** official-source-researcher
- **Retrieval date for all sources:** 2026-07-14 (unless noted)
- **Scope:** How the platform should resolve a NYC street address or BBL to canonical address + BBL + BIN + coordinates using OFFICIAL sources only. No endpoints, parameters, fields, or units are guessed; anything unverifiable is marked `UNKNOWN — requires verification`.

---

## 1. Executive summary

| Service | Operator | Official? | Key required | Input types | BBL/BIN in output | Recommended role |
|---|---|---|---|---|---|---|
| **Geoclient v2** | NYC Office of Technology and Innovation (OTI), backed by DCP Geosupport | Yes | Yes — free subscription key from NYC API Developers Portal | address, address point, bbl, bin, blockface, intersection, place, single-field search, street code, normalize | Yes (full attribute set) | **Primary** |
| **GeoSearch v2** | NYC Dept. of City Planning (Planning Labs) | Yes | No | free-text search / autocomplete only | Yes (`addendum.pad.bbl` / `addendum.pad.bin`) | **Fallback** + autocomplete |
| **Geoservice** | NYC DCP | Yes | Yes — registration on geoservice.planning.nyc.gov | 16 raw Geosupport functions (1A, 1B, 1E, AP, 2, 3, 3S, BBL, BIN, 1N, D, BF, N, HR, ...) | Yes | Secondary fallback / cross-check |
| **Geosupport Desktop Edition (GDE)** | NYC DCP | Yes | No (free download) | all Geosupport functions, offline | Yes | Self-hosted option (Linux supported); underlying engine of record |

All four are front-ends to (or distributions of) **Geosupport**, "NYC's official geocoder of record," maintained by the Department of City Planning (DCP). PAD (Property Address Directory) is the address/tax-lot/BIN reference data inside Geosupport and is released **quarterly**, with biweekly UPAD/TPAD interim updates.

---

## 2. Geoclient API (recommended primary)

### 2.1 Official status and version

- Geoclient is "an API for geocoding locations in New York City ... a proxy API for calling Geosupport," which is "NYC's official geocoder of record ... written and maintained by the Department of City Planning."
  Source: https://github.com/mlipper/geoclient (README; retrieved 2026-07-14)
- The former canonical repo `https://github.com/CityOfNewYork/geoclient` displays: "This project has moved to mlipper/geoclient" (the actively maintained project). Retrieved 2026-07-14.
- The public endpoint is "Sponsored by NYC's Office of Technology and Innovation" and "freely available to the public on the NYC API Developers Portal."
  Source: Geoclient User Guide v2.0.4, section 7 "Public Endpoint": https://mlipper.github.io/geoclient/ (retrieved 2026-07-14)
- **Current version: v2** (user-guide documents v2.0.4). The portal sign-up instructions state: subscribe to **"Geoclient - v2" as "v1 is deprecated and scheduled for deactivation."**
  Source: Geoclient User Guide section 7 (retrieved 2026-07-14). Exact v1 deactivation date: `UNKNOWN — requires verification` (not published on any page consulted).
- Evidence v1 still exists behind auth: unauthenticated GET to `https://api.nyc.gov/geoclient/v1/doc/` returned **HTTP 401** on 2026-07-14.

### 2.2 Base URL and endpoints

- **Production base URL (v2):** `https://api.nyc.gov/geoclient/v2`
  Source: official geoclient-examples repo by the Geoclient maintainer: "examples check for a variable named `GEOCLIENT_URL` allowing you to override the default for the Geoclient v2 base endpoint URL: `https://api.nyc.gov/geoclient/v2`" — https://github.com/mlipper/geoclient-examples (README, retrieved 2026-07-14).
- Endpoints (User Guide, Table 1 "Endpoints" + section 3, retrieved 2026-07-14). Geosupport function proxied in parentheses:
  - `/v2/address` (1B) — "Given a valid address, provides blockface-level, property-level, and political information." Params: `houseNumber` (required), `street` (required; name or 7-digit street code), `borough` (required if `zip` not given), `zip` (required if `borough` not given).
  - `/v2/addresspoint` (AP) — address point ~5 ft inside building along street frontage ("Path: /v2/addresspoint" per guide section 3.2).
  - `/v2/bbl` (BL) — "Given a valid borough, block, and lot provides property-level information." Params: `borough`, `block` ("Zero padding is not required"), `lot` (required; zero padding not required).
  - `/v2/bin` (BN) — "Given a valid building identification number provides property-level information." Param: `bin` (required).
  - `/v2/blockface` (3, 3X), `/v2/place` (1B), `/v2/normalize` (N), `/v2/streetcode` (D/DG/DN), `/v2/version` (HR — Geoclient software + Geosupport release info).
  - Intersection (2, 2W): **exact path `UNKNOWN — requires verification`.** The guide's section 3.6 "Intersection" prints "Path: /v2/blockface" while its parameter table is titled "/intersection arguments" — an internal inconsistency in the official guide (retrieved 2026-07-14). Confirm the real path with a live keyed call before implementing (parameters documented: `crossStreetOne`, `crossStreetTwo`, `borough`).
  - `/v2/search` — single-field search; parses unstructured text and dispatches to address/BBL/BIN/blockface/intersection/place. Params: `input` (required), optional `exactMatchForSingleSuccess` (default false), `exactMatchMaxLevel` (default 3, max 6), `returnPolicy` (default false), `returnPossiblesWithExact` (default false), `returnRejections` (default false), `returnTokens` (default false), `similarNamesDistance` (max Levenshtein distance for street-name guesses; default 8).
- **Case sensitivity:** "The Geoclient base URI and query parameter names are case-sensitive!" Parameter *values* are not. (User Guide section 2.2.)
- **Borough values:** name or number — Manhattan/MN/1, Bronx/BX/2, Brooklyn/BK/BKLYN/3, Queens/QN/4, Staten Island/SI/5. `/search` additionally maps aliases (NYC/NY/New York → Manhattan; ~40 Queens neighborhood names → Queens). (User Guide section 2.2.1.)

### 2.3 Authentication (subscription key model)

Source: Geoclient User Guide sections 7 and 7.1 (retrieved 2026-07-14).

- "Geoclient does not perform any kind of authentication or authorization. However, the endpoint that is available to the public ... does sit behind an API gateway. This endpoint requires that an API key be included with every HTTP request."
- Recommended method: HTTP header **`Ocp-Apim-Subscription-Key: <key>`**.
- Alternate (works "at this time" but "isn't officially documented by the NYC API Developers Portal"): query-string parameter `key=<key>`. Prefer the header.
- The portal (`https://api-portal.nyc.gov/`) is a Microsoft Azure API Management developer portal ("Microsoft Azure API Management - developer portal", "© City of New York" — page title/footer retrieved 2026-07-14).

**Exact human steps to obtain a key** (User Guide section 7, quoted/paraphrased):
1. Go to the NYC API Developers Portal: `https://api-portal.nyc.gov/`.
2. Sign up for an account (green "Sign up" button); confirm via email; sign in.
3. Go to the **Products** page; click the **Geoclient User** link (`https://api-portal.nyc.gov/product#product=geoclient-user`). "Make sure to choose the subscription to 'Geoclient - v2' as v1 is deprecated and scheduled for deactivation."
4. In "Your Subscriptions," enter a name for the product/subscription and click **Subscribe**. (Multiple named subscriptions/keys per account are allowed.)
5. Confirmation email arrives; then open **Profile → Subscriptions → Show** to reveal the subscription key.

### 2.4 Rate limits

- **Official rate limits: `UNKNOWN — requires verification`.** No rate limit is stated in the Geoclient User Guide or on any publicly accessible (unauthenticated) portal page consulted on 2026-07-14. Quotas, if any, are expected to be displayed inside the portal after sign-in (Azure APIM products typically carry quotas).
- A third-party (non-official) repository states "2,500 requests per minute / 500,000 requests per day" (https://github.com/edgaralfonseca/python-nyc-oti-geoclient-api-v1, retrieved 2026-07-14). Treat as **unverified**; confirm from the portal product page once an account exists.

### 2.5 Request/response format

Source: Geoclient User Guide sections 2.1.1–2.1.2 (retrieved 2026-07-14).

- All requests are HTTP **GET** with query-string arguments.
- Default response media type: **JSON** (`application/json`); XML available (`.xml` extension is deprecated; a `Content-Type` header/parameter mechanism is the stated future direction).
- Responses are "composed almost entirely from the results of the proxied Geosupport function call."
- **Contract-relevant behaviors:**
  - Fields with NULL values are **not serialized** (omitted) by default.
  - "Even for successfully recognized input, certain data attributes may not be available for some locations."
  - Element order is unspecified; do not rely on ordering or whitespace formatting.
  - Some Geosupport field values intentionally retain significant whitespace (e.g., censusTract values like `" 187 "` in the official example).

### 2.6 Key response fields (verified from official example responses in the User Guide)

From the documented `/geoclient/v2/address` example (`houseNumber=314&street=w 100 st&borough=manhattan`), response is wrapped in an `"address"` object; fields observed include (all quoted from the official example, retrieved 2026-07-14):

- **Identifiers:** `bbl` ("1018890001"), `bblBoroughCode`, `bblTaxBlock`, `bblTaxLot`, `buildingIdentificationNumber` ("1057127" — the BIN), `condominiumBillingBbl`, `lowBblOfThisBuildingsCondominiumUnits`, `highBblOfThisBuildingsCondominiumUnits`.
- **Canonical address:** `houseNumber`, `firstStreetNameNormalized`, `boePreferredStreetName`, `firstBoroughName`, `zipCode`, `uspsPreferredCityName`. Note the example demonstrates **vanity-address normalization**: input "314 W 100 St" resolves to house number "280" on "RIVERSIDE DRIVE" with `message`: "280 RIVERSIDE DRIVE IS ON RIGHT SIDE OF WEST 100 STREET".
- **Coordinates:** `latitude` (e.g., 40.798502) / `longitude` (e.g., -73.972709) as JSON numbers; `xCoordinate` / `yCoordinate` (e.g., "0991806"/"0230194") as strings; also `internalLabelXCoordinate`/`internalLabelYCoordinate` and `latitudeInternalLabel`/`longitudeInternalLabel` (tax-lot internal label point, present on `/bbl` and `/bin` responses).
- **Status:** `geosupportReturnCode`, `geosupportReturnCode2`, `reasonCode`, `message`, `returnCode1a`, `returnCode1e`, `geosupportFunctionCode`.
- **Zoning-related:** the example contains `dcpZoningMap` ("5D" — the DCP zoning *map sheet number*). **No zoning district designation field appears in any documented example response.** Whether any Geoclient endpoint returns zoning district designations: `UNKNOWN — requires verification` (nothing on the pages consulted claims it does; zoning district data should come from other official sources, out of scope here).
- **Districts (selection):** `communityDistrict`, `cityCouncilDistrict`, `censusTract2020`, `censusBlock2020`, `nta2020`, `cdta2020`, `assemblyDistrict`, `congressionalDistrict`, plus sanitation/fire/police/health fields.

`/v2/bbl` example (`borough=manhattan&block=67&lot=1`) — wrapped in `"bbl"` object — demonstrates **BBL validation/expansion**: inputs echoed as `bblTaxBlockIn: "67"`, `bblTaxLotIn: "1"` and normalized to `bblTaxBlock: "00067"`, `bblTaxLot: "0001"`, full `bbl: "1000670001"`, and returns the lot's `buildingIdentificationNumber` ("1079043"), `numberOfExistingStructuresOnLot`, condo billing BBL fields, and internal-label coordinates.

`/v2/bin` example (`bin=1079043`) — wrapped in `"bin"` object — returns the BIN's `bbl` ("1000670001") and the same property-level attribute family.

**Coordinate system (verified from DCP's official Geosupport UPG, Appendix 3 "Data Item Dictionary", https://nycplanning.github.io/Geosupport-UPG/appendices/appendix03/, retrieved 2026-07-14):**
- "The coordinate system that Geosupport uses is known as the State Plane Coordinate (SPC) system ... The SPC zone that New York City is in, and which Geosupport uses, is called the **New York-Long Island zone, NAD 83**. In the SPC system, **one unit of X or Y represents one foot** of distance on the ground."
- Latitude/longitude "are calculated based on the spatial coordinates (x,y) returned for that location," so lat/long from address functions (1/1E) "will be somewhat different from the values returned by Tax Lot and Building processing functions (e.g. 1A/BL/BN)." For NYC, "Latitude is always positive and Longitude is always negative."
- Precision caveat: "For Functions 1, 1B (blockface information) and 1E, the spatial coordinates that Geosupport returns are imprecise approximations of real-world locations, and are not appropriate for use in applications that require a high level of spatial accuracy." (Function AP / address points exist for higher-precision entrance locations.)
- The explicit EPSG code is not stated in the UPG text consulted; "NAD83 / New York Long Island (ftUS)" is commonly EPSG:2263, but the EPSG mapping is `UNKNOWN — requires verification` from an official NYC page.

### 2.7 Status codes and ambiguity/multiple-match reporting

Source: Geoclient User Guide sections 2.3.1–2.3.2 and 3.9; Geosupport UPG Appendix 4 (https://nycplanning.github.io/Geosupport-UPG/appendices/appendix04/), both retrieved 2026-07-14.

- **Two layers of status:** HTTP status codes for the Geoclient service itself (200 = request reached Geoclient regardless of geocoding outcome; 400 = missing required query parameter; 401/403 = key problems; 404 = bad URL; 500 = internal error), and **Geosupport return codes (GRC)** inside the 200 response for the geocoding outcome.
- GRC semantics (User Guide Table 4): `00` = success (blank `reasonCode`/`message`); `01` = success with warnings (`geosupportReturnCode`, `reasonCode`, `message` populated); GRC > `01` = reject/error.
- `/address` (Function 1B) is composed of two sub-calls; **check both**: 1EX status in `geosupportReturnCode`/`reasonCode`/`message` (aliases `returnCode1e`/`reasonCode1e`) and 1AX status in `geosupportReturnCode2`/`reasonCode2`/`message2` (aliases `returnCode1a`/`reasonCode1a`). "There are a significant number of locations where data is valid and/or available for only one of these two sub-function calls."
- **Ambiguity signals (official GRC meanings, UPG Appendix 4):**
  - GRC `11`: "NOT RECOGNIZED. THERE ARE NO SIMILAR NAMES".
  - GRC `EE`: street not recognized with suggestions — reason code `1`: "<street> NOT RECOGNIZED. IS IT <similar street name>?"; reason codes `2`–`A`: "<street> NOT RECOGNIZED. THERE ARE <number> SIMILAR NAMES" (similar names returned in the "List of Street Names" in Work Area 1).
  - GRC `50` (reason codes 1–4): "<input street name> IS AN INVALID STREET NAME FOR THIS LOCATION", reason code indicating how many valid alternatives exist.
  - GRC `75`: "DUPLICATE ADDRESS-USE <pseudo-streetname1> OR <pseudo-streetname2>".
  - GRC `63` (Function 2): "INPUT STREET NAMES DO NOT FORM A UNIQUE INTERSECTION".
- **`/v2/search` multiple-match model** (User Guide section 3.9): response envelope has `id`, `status` (e.g., "OK"), `input`, and a `results` array; each result has `level` (0 = as-given borough; 1 = automatic 5-borough fan-out when borough can't be derived; higher levels = sub-searches on Geosupport suggestions), `status` (e.g., `EXACT_MATCH`), `request` (the parsed structured request), and `response` (the full geocode attribute set). Options `returnPossiblesWithExact`, `returnRejections`, `similarNamesDistance`, `exactMatchMaxLevel` control how possibles/rejections/suggestion-driven sub-searches are returned.
- `/v2/search` **directly accepts BBL and BIN strings**: "A ten-digit number where the first digit is 1–5 is recognized as a BBL request"; "A seven-digit number where the first digit is 1–5 is recognized as a BIN request."

### 2.8 Known limitations (Geoclient)

- Attribute availability varies by location; null fields omitted (section 2.5 above).
- Blockface-level coordinates are approximations (UPG precision caveat, section 2.6 above).
- v1 deprecated; deactivation date unpublished.
- Official rate limits unpublished (section 2.4).
- Data currency is bounded by the Geosupport release loaded on the server; `/v2/version` reports "Geosupport version/release info directly from the Geosupport instance this endpoint is currently using" (User Guide Table 1) — use it in health checks.

---

## 3. NYC Planning Labs GeoSearch API (recommended fallback)

Sources: https://geosearch.planninglabs.nyc/docs/ (retrieved 2026-07-14); https://github.com/NYCPlanning/labs-geosearch-docs README (retrieved 2026-07-14); live unauthenticated response retrieved 2026-07-14.

- **Official status:** Operated by NYC Planning (Planning Labs). "NYC GeoSearch is an API that transforms input text — such as an address, or the name of a place — to a location in New York City using authoritative NYC address data from the Property Address Directory (PAD) via Pelias (a modular, open-source geocoder)." It "powers the autocomplete/typeahead search results in web apps such as ZoLa and Population Fact Finder."
- **Base URL:** `https://geosearch.planninglabs.nyc/v2/` with endpoints `/search` and `/autocomplete`. No reverse-geocoding endpoint is documented. (Docs, retrieved 2026-07-14.)
- **Key:** none required — docs mention no key, and a live call without credentials succeeded (below).
- **Rate limits:** `UNKNOWN — requires verification` (not documented).
- **Data basis:** PAD. Live responses carry the PAD release in `addendum.pad.version` (observed `"26a"` on 2026-07-14, i.e., one quarterly release behind the then-current Geosupport/PAD 26B — evidence that GeoSearch data refresh can lag the PAD release).
- **Response format:** GeoJSON `FeatureCollection`; coordinates are GeoJSON `[longitude, latitude]`. `/search` returns 10 features by default; `size` parameter controls count. "Spelling matters, but not capitalization."
- **Representative raw response (live GET `https://geosearch.planninglabs.nyc/v2/search?text=120%20broadway&size=2`, retrieved 2026-07-14; trimmed to one feature):**

```json
{
  "geocoding": {
    "version": "0.2",
    "attribution": "http://geosearch.planninglabs.nyc/attribution",
    "query": {
      "text": "120 broadway", "size": 2, "parser": "pelias",
      "parsed_text": {"subject": "120 broadway", "housenumber": "120", "street": "broadway"}
    },
    "engine": {"name": "Pelias", "author": "Mapzen", "version": "1.0"}
  },
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [-74.010542, 40.708233]},
      "properties": {
        "id": "4178", "gid": "nycpad:venue:4178", "layer": "venue", "source": "nycpad",
        "name": "120 BROADWAY", "housenumber": "120", "street": "BROADWAY", "postalcode": "10271",
        "confidence": 0.8, "match_type": "fallback", "accuracy": "point",
        "borough": "Manhattan", "region_a": "NY", "locality": "New York",
        "label": "120 BROADWAY, New York, NY, USA",
        "addendum": {"pad": {"bbl": "1000477501", "bin": "1001026", "version": "26a"}}
      }
    }
  ]
}
```

- **BBL/BIN:** returned in `properties.addendum.pad.bbl` / `.bin`. **No BBL/BIN input lookup is documented** — GeoSearch is text-search only; it cannot validate/expand a BBL directly.
- **Multiple matches:** returned as ranked `features` with `confidence` and `match_type`; no Geosupport GRC semantics.

### GeoSearch vs Geoclient (S2: conflicting/alternative sources)

| Dimension | Geoclient v2 | GeoSearch v2 |
|---|---|---|
| Engine | Geosupport (geocoder of record) via JNI proxy | Pelias/Elasticsearch over normalized PAD extract |
| Key | Required (free) | None |
| Inputs | Structured address, BBL, BIN, blockface, intersection, place + single-field search | Free text only |
| BBL validation/expansion | Yes (`/v2/bbl`, `/v2/bin`, `/search` pattern recognition) | No (not documented) |
| Attribute richness | Very high (districts, condo BBL ranges, street codes, GRCs, x/y NAD83 ft + lat/long) | Address + point + `addendum.pad` {bbl, bin, version} |
| Ambiguity semantics | Geosupport GRC/reason codes + search levels/possibles | Ranked results + `confidence` |
| Data currency | Geosupport release on server (verify via `/v2/version`) | PAD release in `addendum.pad.version` (observed lagging: 26a vs 26B) |
| Vanity-address normalization, DUPLICATE ADDRESS handling | Yes (Geosupport logic) | `UNKNOWN — requires verification` |

**Recommendation:** Geoclient v2 primary (authoritative semantics, BBL/BIN lookups, richer canonical output); GeoSearch as keyless fallback and for UI autocomplete. Cross-check `addendum.pad.version` vs Geoclient `/v2/version` when reconciling disagreements.

---

## 4. Geosupport, Geosupport Desktop Edition, and Geoservice

### 4.1 Geosupport (the engine)

- Geosupport is DCP's geographic data retrieval/validation system; functions relevant here: **1B** (address → blockface+property+political data; used by Geoclient `/address`), **1A/1E/AP**, **BL** (BBL → property data; Geoclient `/bbl`), **BN** (BIN → property data; Geoclient `/bin`), 2/3 families (intersections/blockfaces). Authoritative programming reference: **Geosupport System User Programming Guide (UPG)** — https://nycplanning.github.io/Geosupport-UPG/ (DCP-published; retrieved 2026-07-14).
- Return codes reference: https://nycplanning.github.io/Geosupport-UPG/appendices/appendix04/ (retrieved 2026-07-14).

### 4.2 Geosupport Desktop Edition (GDE) — server-side viability

Source: official DCP page "Geosupport Desktop Edition", https://www.nyc.gov/content/planning/pages/resources/geocoding/geosupport-desktop-edition (content retrieved 2026-07-14 via nyc.gov's own content API at `https://apps.nyc.gov/content-api/v1/content/planning/resources/geocoding/geosupport-desktop-edition`, because the page is client-rendered).

- "Geosupport Desktop Edition is a highly customized geocoding package that allows users to process geographic information for New York City." Free download; documentation manuals included with install.
- **Platforms:** downloads offered for "Windows - Standard 32-bit", "Windows - Standard 64-bit", and **"Linux"** (both for GDE and for UPAD/TPAD updates). The UPG overview likewise lists "Geosupport Desktop Edition (Windows 32-bit and 64-bit; LINUX)" (https://nycplanning.github.io/Geosupport-UPG/overview/, retrieved 2026-07-14).
- **Current release (as of 2026-07-14):** "Latest Release: 26B; Release Frequency: Quarterly; Date of Data: May 2026; Software: 26.2". TPAD/UPAD "Latest Release: 26B4; Release Frequency: As Needed; Release Date: July 13, 2026" (page also states "The UPAD and TPAD files are released biweekly").
- **UPAD/TPAD:** "UPAD (Updated Property Address Directory) ... contains property level address, tax parcel, and building identification number updates made to ... PAD ... since its last quarterly release." "TPAD (Transitional Property Address Directory) provides users with up-to-date property related information received from the Department of Buildings, such as job filings for new buildings (NB) as well as status updates of new construction and/or demolition." (Directly relevant to development-feasibility use: TPAD carries provisional BIN/status data for buildings under construction/demolition. UPG overview: TPAD provides "BIN and status information for Functions 1A, 1B, BL and BN.")
- **Why it matters / server-side viability:** GDE is the same engine Geoclient wraps; the Geoclient project itself runs Geosupport's C shared libraries via JNI and publishes a `geosupport-docker` image and Linux deployment docs (User Guide sections 5.5–5.6, retrieved 2026-07-14). Self-hosting Geosupport on Linux is therefore an officially supported pattern — viable if the platform later needs unmetered/offline resolution — at the cost of quarterly + biweekly data-refresh operations.
- **Use limitation (both GDE and PAD pages):** BYTES of the BIG APPLE products are "provided ... for informational purposes only"; DCP disclaims warranties of completeness/accuracy/fitness.

### 4.3 Geoservice (DCP REST interface)

Source: https://geoservice.planning.nyc.gov/ (retrieved 2026-07-14).

- "A RESTful web service interface to the NYC Department of City Planning's core Geosupport system." Exposes 16 Geosupport functions (address: 1A, 1B, 1E, AP; intersection/street: 2, 3, 3S; property: BBL, BIN; name/code: 1N, D, BF, N; HR version info).
- Endpoint pattern: `https://geoservice.planning.nyc.gov/geoservice/geoservice.svc/Function_[NAME]`; JSON and XML output; examples show a `Key=` parameter and the site has a `/Register` link → **registration/API key required**. Exact registration/approval workflow: `UNKNOWN — requires verification` (requires signing up).
- Site reported running **"Geosupport Version 26B"** on 2026-07-14 — consistent with the GDE/PAD 26B release.

---

## 5. PAD update cadence

- Official DCP PAD page: "The Property Address Directory (PAD) file contains additional NYC geographic information at the tax lot level not found in the PLUTO files. ... **Update Frequency: Quarterly**. Latest Release: 26B; Date of Data: May 2026."
  Source: https://www.nyc.gov/content/planning/pages/resources/datasets/pad (content retrieved 2026-07-14 via `https://apps.nyc.gov/content-api/v1/content/planning/resources/datasets/pad`).
- Interim updates between quarterly releases: UPAD/TPAD, "released biweekly" (GDE page, section 4.2 above).
- PAD is also mirrored on NYC Open Data (`https://data.cityofnewyork.us/City-Government/Property-Address-Directory/bc8t-ecyu`); mirror-specific update metadata not independently fetched — `UNKNOWN — requires verification` if the connector ever consumes the Open Data mirror instead of DCP's release.

---

## 6. Answers to the task's specific questions

1. **Can these services validate/expand a BBL directly?**
   - Geoclient v2: **Yes** — `/v2/bbl?borough=&block=&lot=` (Function BL) accepts unpadded block/lot, returns normalized 10-digit `bbl`, the lot's BIN(s), condo billing BBL, structure counts, and internal-label coordinates. `/v2/bin` does the inverse (BIN → BBL). `/v2/search` recognizes bare 10-digit BBL / 7-digit BIN strings.
   - Geoservice: **Yes** — Function_BBL and Function_BIN endpoints (raw Geosupport).
   - GeoSearch: **No** (text search only; BBL/BIN appear only in output `addendum.pad`).
2. **How are ambiguous addresses / multiple matches reported?** Geoclient: HTTP 200 + Geosupport GRC/reason/message (GRC EE similar-name suggestions, 11 no-similar-names, 50 invalid-street-for-location, 75 duplicate address, 63 non-unique intersection), dual sub-function codes on `/address`, and `/search` result arrays with `level`/`status`/possibles/rejections. GeoSearch: ranked GeoJSON features with `confidence`/`match_type`. (Details and sources in section 2.7 and 3.)
3. **Update cadence:** PAD/Geosupport quarterly (releases named `<YY><A-D>`, e.g., 26B, "Date of Data: May 2026"); UPAD/TPAD biweekly/as-needed (26B4 released 2026-07-13). Hosted-API refresh timing after each release: `UNKNOWN — requires verification` for Geoclient (check `/v2/version`) and observed lagging for GeoSearch (`addendum.pad.version` = 26a on 2026-07-14).

---

## 7. Recommendation for the resolve-address connector

1. **Primary:** Geoclient v2 (`https://api.nyc.gov/geoclient/v2`), header auth `Ocp-Apim-Subscription-Key`.
   - Structured input → `/v2/address` (with `borough` or `zip`); check BOTH `returnCode1e` and `returnCode1a` families; treat GRC 00/01 as success, surface `message` on 01; map `bbl`, `buildingIdentificationNumber`, normalized street/house number, `latitude`/`longitude` (derived, WGS-degrees-style decimal values computed from NAD83 NY-LI state-plane x/y; exact output datum statement beyond "calculated from SPC NAD83 x,y" is `UNKNOWN — requires verification`), `xCoordinate`/`yCoordinate` (NAD83 NY–Long Island state plane, feet).
   - Free-text input → `/v2/search` with `returnPossiblesWithExact=true` to drive a disambiguation UI; bare BBL/BIN strings also route here or to `/v2/bbl` / `/v2/bin`.
   - Health/currency check → `/v2/version` (records Geosupport release, compare to DCP's published latest release).
2. **Fallback:** GeoSearch v2 (`https://geosearch.planninglabs.nyc/v2/search`, `/v2/autocomplete`) — keyless; use for autocomplete and as a degraded-mode resolver (address + point + BBL/BIN via `addendum.pad`); always record `addendum.pad.version` for provenance.
3. **Cross-check / secondary fallback:** DCP Geoservice (registration required) for raw Geosupport function access; self-hosted GDE/geosupport-docker only if volume or offline requirements demand it.
4. **Credentials a human must obtain (exact action):** create an account at `https://api-portal.nyc.gov/`, subscribe to the **Geoclient User** product choosing **"Geoclient - v2"**, and retrieve the subscription key from Profile → Subscriptions → Show (full steps in section 2.3). Optionally also register at `https://geoservice.planning.nyc.gov/Register` for the Geoservice fallback. While in the portal, record the official rate limits/quotas shown for the Geoclient product (currently UNKNOWN).

---

## 8. Contract-test fixture plan (to capture once credentials exist)

Save raw, unmodified JSON responses (plus request URL, headers minus key, timestamp, and `/v2/version` output captured the same day) as fixtures:

| # | Fixture | Request | Asserts |
|---|---|---|---|
| F1 | address exact match, vanity address | `/v2/address?houseNumber=314&street=w%20100%20st&borough=manhattan` | GRC 01/00 pair; normalized to 280 Riverside Dr; `bbl`, `buildingIdentificationNumber`, lat/long, x/y present |
| F2 | address via zip (no borough) | `/v2/address?houseNumber=120&street=broadway&zip=10271` | borough resolved; zip echo |
| F3 | address, similar-name suggestion | `/v2/address` with misspelled street | GRC `EE` + reason code + message with suggestions |
| F4 | address, not recognized | `/v2/address` with nonsense street | GRC `11` |
| F5 | duplicate address case | known GRC `75` input (identify via DCP examples) | GRC `75` + pseudo-street message |
| F6 | bbl valid + normalization | `/v2/bbl?borough=manhattan&block=67&lot=1` | `bblTaxBlockIn` vs padded `bblTaxBlock`; `bbl=1000670001`; BIN present |
| F7 | bbl invalid lot | `/v2/bbl` with nonexistent lot | GRC > 01 shape |
| F8 | bin valid | `/v2/bin?bin=1079043` | `bbl` back-reference |
| F9 | bin invalid | `/v2/bin?bin=1999999` (or similar invalid) | error shape |
| F10 | search: address w/o borough | `/v2/search?input=280%20riverside%20drive&returnPossiblesWithExact=true` | 5-borough fan-out `level=1`, possibles array |
| F11 | search: bare BBL | `/v2/search?input=1000670001` | recognized as BBL request |
| F12 | search: bare BIN | `/v2/search?input=1079043` | recognized as BIN request |
| F13 | version | `/v2/version` | Geosupport release id; used for provenance pinning |
| F14 | auth failure | any endpoint without key | gateway 401 body shape (Azure APIM error format — capture, currently UNKNOWN) |
| F15 | GeoSearch search (no key needed — capturable now) | `https://geosearch.planninglabs.nyc/v2/search?text=120%20broadway&size=2` | GeoJSON shape; `addendum.pad.{bbl,bin,version}` (raw copy captured 2026-07-14, section 3) |
| F16 | GeoSearch autocomplete | `/v2/autocomplete?text=120%20bro` | feature shape parity with `/search` |

Fixture hygiene: never edit captured bodies; store PAD/Geosupport release identifiers alongside; refresh fixtures after each quarterly release only when contract changes are suspected.

---

## 9. UNKNOWNs (S3 — explicit, with reason)

1. **Geoclient official rate limits/quotas** — not published on unauthenticated pages; visible (if at all) only inside api-portal.nyc.gov after sign-in. Third-party figure (2,500/min, 500k/day) unverified.
2. **Geoclient v1 deactivation date** — guide says "deprecated and scheduled for deactivation" with no date.
3. **Azure APIM gateway error body shape for 401/403/429** — requires live calls with/without key.
4. **Whether any Geoclient endpoint returns zoning district designations** — not shown in documented examples; only `dcpZoningMap` (map sheet) observed.
5. **EPSG code equivalence for Geosupport x/y** — UPG states "New York-Long Island zone, NAD 83, feet" but no EPSG number on official pages consulted.
6. **GeoSearch rate limits/SLA and data-refresh schedule** — undocumented; observed PAD 26a while DCP's latest is 26B.
7. **GeoSearch handling of vanity/duplicate addresses** — undocumented.
8. **Geoservice registration/approval workflow and terms** — requires registering an account.
9. **Geoclient hosted endpoint's refresh lag after each Geosupport release** — must be observed via `/v2/version` over time.
10. **NYC Open Data PAD mirror update metadata** — mirror page not independently fetched; verify before relying on it.
11. **Geoclient intersection endpoint path** — official guide is internally inconsistent ("Path: /v2/blockface" under the Intersection section vs "Table 11. /intersection arguments"); confirm with a live keyed call.

---

## 10. Source register (all retrieved 2026-07-14)

| Source | URL | Used for |
|---|---|---|
| Geoclient User Guide v2.0.4 (official project docs) | https://mlipper.github.io/geoclient/ | endpoints, params, auth steps, examples, GRC handling, search semantics, v1 deprecation |
| mlipper/geoclient README | https://github.com/mlipper/geoclient | official status, Geosupport relationship |
| CityOfNewYork/geoclient (moved notice) | https://github.com/CityOfNewYork/geoclient | provenance of the maintained repo |
| geoclient-examples README | https://github.com/mlipper/geoclient-examples | production base URL `https://api.nyc.gov/geoclient/v2`, key header + `key` query param |
| NYC API Developers Portal | https://api-portal.nyc.gov/ (product: https://api-portal.nyc.gov/product#product=geoclient-user) | portal existence, Azure APIM, sign-up surface |
| Geoclient v1 doc URL (401 evidence) | https://api.nyc.gov/geoclient/v1/doc/ | v1 exists behind auth |
| GeoSearch docs | https://geosearch.planninglabs.nyc/docs/ | v2 base URL, endpoints, GeoJSON, size param, caveats |
| GeoSearch docs repo README | https://github.com/NYCPlanning/labs-geosearch-docs | official status, PAD basis, Pelias |
| GeoSearch live response | https://geosearch.planninglabs.nyc/v2/search?text=120%20broadway&size=2 | representative raw response, `addendum.pad` fields, PAD version 26a |
| DCP Geosupport Desktop Edition page | https://www.nyc.gov/content/planning/pages/resources/geocoding/geosupport-desktop-edition (via https://apps.nyc.gov/content-api/v1/content/planning/resources/geocoding/geosupport-desktop-edition) | GDE description, platforms, release 26B/software 26.2, UPAD/TPAD biweekly, use limitations |
| DCP PAD page | https://www.nyc.gov/content/planning/pages/resources/datasets/pad (via https://apps.nyc.gov/content-api/v1/content/planning/resources/datasets/pad) | PAD description, quarterly cadence, release 26B May 2026 |
| Geosupport UPG overview | https://nycplanning.github.io/Geosupport-UPG/overview/ | functions, platforms, TPAD role |
| Geosupport UPG Appendix 3 (Data Item Dictionary) | https://nycplanning.github.io/Geosupport-UPG/appendices/appendix03/ | SPC NAD83 NY–Long Island, feet; lat/long derivation; precision caveats |
| Geosupport UPG Appendix 4 (Return Codes) | https://nycplanning.github.io/Geosupport-UPG/appendices/appendix04/ | GRC 00/01/11/50/63/75/EE meanings |
| DCP Geoservice | https://geoservice.planning.nyc.gov/ | fallback REST interface, 16 functions, key requirement, Geosupport 26B |
