<!-- Orchestrator capture header: official-source-researcher fixture-capture return saved
     VERBATIM (transport entity-decoding only: &amp; decoded in URLs/headers). Dispatched and
     delivered 2026-09-19 (session seq 119) for the DB-026 packet. The agent's preamble line
     and closing notes are preserved as part of the verbatim return. -->

All eight captures are complete, byte-faithful, and clean (no errors, no rate-limits, no auth demanded). Below is the full corpus for the orchestrator to save verbatim.

---

# DB-026 address→lot source fixture corpus — byte-faithful capture

Captured 2026-09-19 UTC by `official-source-researcher`. Tool: `curl 8.11.0` (Schannel), keyless GET. No endpoint demanded a key. No errors or rate-limits occurred; no retries were needed. All bodies are reproduced exactly as the server returned them (minified single-line JSON; no reindent/reorder). Request URLs were issued with `curl -G --data-urlencode`, so on the wire spaces are `%20` and each param is separate (e.g. `?text=1279%2037%20street%20brooklyn&size=3`); the human-readable form is shown per section.

---

## 1. GeoSearch success — `search`, size=3 (true hit + GARAGE sibling + EAST 37 mismatch)
- **URL:** `https://geosearch.planninglabs.nyc/v2/search?text=1279 37 street brooklyn&size=3`
- **Retrieved:** 2026-09-19T03:59:02Z — HTTP 200, content-length 3545
- **Freshness/version headers:** `x-powered-by: pelias`; `cache-control: public,private`; `etag: W/"dd9-kvpcSdOGRRDbKuTcb8IOD3pguqg"`; no Last-Modified / dataset-version header. (`set-cookie: DO-LB=...` is an ephemeral 300s LB routing cookie, not a credential.)
- **Body (verbatim):**

```json
{"geocoding":{"version":"0.2","attribution":"http://geosearch.planninglabs.nyc/attribution","query":{"text":"1279 37 street brooklyn","size":3,"private":false,"lang":{"name":"English","iso6391":"en","iso6393":"eng","via":"default","defaulted":true},"querySize":20,"parser":"pelias","parsed_text":{"subject":"1279 37 street","housenumber":"1279","street":"37 street","locality":"brooklyn","admin":"brooklyn"}},"engine":{"name":"Pelias","author":"Mapzen","version":"1.0"},"timestamp":1789790343142},"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.98522,40.641968]},"properties":{"id":"1309911","gid":"nycpad:venue:1309911","layer":"venue","source":"nycpad","source_id":"1309911","country_code":"US","name":"1279 37 STREET","housenumber":"1279","street":"37 STREET","postalcode":"11218","confidence":0.8,"match_type":"fallback","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Kensington","neighbourhood_gid":"whosonfirst:neighbourhood:85828101","label":"1279 37 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3052960043","bin":"3340270","version":"26c"}}}},{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.985331,40.642037]},"properties":{"id":"1309902","gid":"nycpad:venue:1309902","layer":"venue","source":"nycpad","source_id":"1309902","country_code":"US","name":"1279 GARAGE 37 STREET","housenumber":"1279 GARAGE","street":"37 STREET","postalcode":"11218","confidence":0.8,"match_type":"fallback","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Kensington","neighbourhood_gid":"whosonfirst:neighbourhood:85828101","label":"1279 GARAGE 37 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3052960043","bin":"3123204","version":"26c"}}}},{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.93952,40.624792]},"properties":{"id":"1632496","gid":"nycpad:venue:1632496","layer":"venue","source":"nycpad","source_id":"1632496","country_code":"US","name":"1279 EAST 37 STREET","housenumber":"1279","street":"EAST 37 STREET","postalcode":"11210","confidence":0.8,"match_type":"fallback","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Flatlands","neighbourhood_gid":"whosonfirst:neighbourhood:85819585","label":"1279 EAST 37 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3076370038","bin":"3209116","version":"26c"}}}}],"bbox":[-73.985331,40.624792,-73.93952,40.642037]}
```

All three features carry identical `confidence:0.8, match_type:"fallback"`. The true hit and GARAGE sibling share `bbl 3052960043` (differ only by `bin`: 3340270 vs 3123204); the EAST 37 feature is a distinct lot (`bbl 3076370038`).

---

## 2. GeoSearch "th" variant — `search`, size=1
- **URL:** `https://geosearch.planninglabs.nyc/v2/search?text=1279 37th street brooklyn&size=1`
- **Retrieved:** 2026-09-19T03:59:17Z — HTTP 200, 1566 bytes
- **Body (verbatim):**

```json
{"geocoding":{"version":"0.2","attribution":"http://geosearch.planninglabs.nyc/attribution","query":{"text":"1279 37th street brooklyn","size":1,"private":false,"lang":{"name":"English","iso6391":"en","iso6393":"eng","via":"default","defaulted":true},"querySize":20,"parser":"pelias","parsed_text":{"subject":"1279 37th street","housenumber":"1279","street":"37th street","locality":"brooklyn","admin":"brooklyn"}},"engine":{"name":"Pelias","author":"Mapzen","version":"1.0"},"timestamp":1789790357661},"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.98522,40.641968]},"properties":{"id":"1309911","gid":"nycpad:venue:1309911","layer":"venue","source":"nycpad","source_id":"1309911","country_code":"US","name":"1279 37 STREET","housenumber":"1279","street":"37 STREET","postalcode":"11218","confidence":0.8,"match_type":"fallback","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Kensington","neighbourhood_gid":"whosonfirst:neighbourhood:85828101","label":"1279 37 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3052960043","bin":"3340270","version":"26c"}}}}],"bbox":[-73.98522,40.641968,-73.98522,40.641968]}
```

"37th" (query `parsed_text.street` = "37th street") resolves to the same canonical `1279 37 STREET`, bbl 3052960043, bin 3340270 — identical to the C1 top hit.

---

## 3. GeoSearch reverse frontage — `search`, size=1
- **URL:** `https://geosearch.planninglabs.nyc/v2/search?text=3622 13 avenue brooklyn&size=1`
- **Retrieved:** 2026-09-19T03:59:17Z — HTTP 200, 1560 bytes
- **Body (verbatim):**

```json
{"geocoding":{"version":"0.2","attribution":"http://geosearch.planninglabs.nyc/attribution","query":{"text":"3622 13 avenue brooklyn","size":1,"private":false,"lang":{"name":"English","iso6391":"en","iso6393":"eng","via":"default","defaulted":true},"querySize":20,"parser":"pelias","parsed_text":{"subject":"3622 13 avenue","housenumber":"3622","street":"13 avenue","locality":"brooklyn","admin":"brooklyn"}},"engine":{"name":"Pelias","author":"Mapzen","version":"1.0"},"timestamp":1789790357962},"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.98522,40.641968]},"properties":{"id":"1309903","gid":"nycpad:venue:1309903","layer":"venue","source":"nycpad","source_id":"1309903","country_code":"US","name":"3622 13 AVENUE","housenumber":"3622","street":"13 AVENUE","postalcode":"11218","confidence":0.8,"match_type":"fallback","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Kensington","neighbourhood_gid":"whosonfirst:neighbourhood:85828101","label":"3622 13 AVENUE, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3052960043","bin":"3340270","version":"26c"}}}}],"bbox":[-73.98522,40.641968,-73.98522,40.641968]}
```

The reverse (address-of-record) frontage returns **same bbl 3052960043, same bin 3340270, same coordinates** as the C1 top hit — but a different feature `id` (1309903) and the PLUTO-canonical `name`/`label` "3622 13 AVENUE".

---

## 4. GeoSearch failure probes — `search`, size=1 (both still HTTP 200 with a bogus fallback feature)

### 4a. Nonexistent street `1279 zzqqxx street brooklyn`
- **URL:** `https://geosearch.planninglabs.nyc/v2/search?text=1279 zzqqxx street brooklyn&size=1`
- **Retrieved:** 2026-09-19T03:59:34Z — HTTP 200, 1578 bytes
- **Body (verbatim):**

```json
{"geocoding":{"version":"0.2","attribution":"http://geosearch.planninglabs.nyc/attribution","query":{"text":"1279 zzqqxx street brooklyn","size":1,"private":false,"lang":{"name":"English","iso6391":"en","iso6393":"eng","via":"default","defaulted":true},"querySize":20,"parser":"pelias","parsed_text":{"subject":"1279 zzqqxx street","housenumber":"1279","street":"zzqqxx street","locality":"brooklyn","admin":"brooklyn"}},"engine":{"name":"Pelias","author":"Mapzen","version":"1.0"},"timestamp":1789790374793},"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.994554,40.633088]},"properties":{"id":"1359602","gid":"nycpad:venue:1359602","layer":"venue","source":"nycpad","source_id":"1359602","country_code":"US","name":"1279 53 STREET","housenumber":"1279","street":"53 STREET","postalcode":"11219","confidence":0.8,"match_type":"fallback","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Borough Park","neighbourhood_gid":"whosonfirst:neighbourhood:420782907","label":"1279 53 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3056627501","bin":"3138712","version":"26c"}}}}],"bbox":[-73.994554,40.633088,-73.994554,40.633088]}
```

Garbage street name "zzqqxx" was dropped; returned a **wrong real lot** "1279 53 STREET" (bbl 3056627501) at `confidence:0.8, match_type:"fallback"`.

### 4b. Out-of-range house number `99999 37 street brooklyn`
- **URL:** `https://geosearch.planninglabs.nyc/v2/search?text=99999 37 street brooklyn&size=1`
- **Retrieved:** 2026-09-19T03:59:34Z — HTTP 200, 1561 bytes
- **Body (verbatim):**

```json
{"geocoding":{"version":"0.2","attribution":"http://geosearch.planninglabs.nyc/attribution","query":{"text":"99999 37 street brooklyn","size":1,"private":false,"lang":{"name":"English","iso6391":"en","iso6393":"eng","via":"default","defaulted":true},"querySize":20,"parser":"pelias","parsed_text":{"subject":"99999 37 street","housenumber":"99999","street":"37 street","locality":"brooklyn","admin":"brooklyn"}},"engine":{"name":"Pelias","author":"Mapzen","version":"1.0"},"timestamp":1789790375009},"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-74.008191,40.655949]},"properties":{"id":"758253","gid":"nycpad:venue:758253","layer":"venue","source":"nycpad","source_id":"758253","country_code":"US","name":"207 37 STREET","housenumber":"207","street":"37 STREET","postalcode":"11232","confidence":0.8,"match_type":"fallback","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Sunset Park","neighbourhood_gid":"whosonfirst:neighbourhood:85851575","label":"207 37 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3006950001","bin":"3336906","version":"26c"}}}}],"bbox":[-74.008191,40.655949,-74.008191,40.655949]}
```

Out-of-range "99999" was silently replaced; returned "207 37 STREET" (`housenumber:"207"` ≠ query 99999), bbl 3006950001, again `confidence:0.8, match_type:"fallback"`.

---

## 5. GeoSearch autocomplete shape — `autocomplete`
- **URL:** `https://geosearch.planninglabs.nyc/v2/autocomplete?text=1279 37 st`
- **Retrieved:** 2026-09-19T03:59:34Z — HTTP 200, 3361 bytes, 3 features
- **Body (verbatim):**

```json
{"geocoding":{"version":"0.2","attribution":"http://geosearch.planninglabs.nyc/attribution","query":{"text":"1279 37 st","parser":"pelias","parsed_text":{"subject":"1279 37 st","housenumber":"1279","street":"37 st"},"size":10,"private":false,"lang":{"name":"English","iso6391":"en","iso6393":"eng","via":"default","defaulted":true},"querySize":20},"engine":{"name":"Pelias","author":"Mapzen","version":"1.0"},"timestamp":1789790375218},"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.98522,40.641968]},"properties":{"id":"1309911","gid":"nycpad:venue:1309911","layer":"venue","source":"nycpad","source_id":"1309911","country_code":"US","name":"1279 37 STREET","housenumber":"1279","street":"37 STREET","postalcode":"11218","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Kensington","neighbourhood_gid":"whosonfirst:neighbourhood:85828101","label":"1279 37 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3052960043","bin":"3340270","version":"26c"}}}},{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.985331,40.642037]},"properties":{"id":"1309902","gid":"nycpad:venue:1309902","layer":"venue","source":"nycpad","source_id":"1309902","country_code":"US","name":"1279 GARAGE 37 STREET","housenumber":"1279 GARAGE","street":"37 STREET","postalcode":"11218","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Kensington","neighbourhood_gid":"whosonfirst:neighbourhood:85828101","label":"1279 GARAGE 37 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3052960043","bin":"3123204","version":"26c"}}}},{"type":"Feature","geometry":{"type":"Point","coordinates":[-73.93952,40.624792]},"properties":{"id":"1632496","gid":"nycpad:venue:1632496","layer":"venue","source":"nycpad","source_id":"1632496","country_code":"US","name":"1279 EAST 37 STREET","housenumber":"1279","street":"EAST 37 STREET","postalcode":"11210","accuracy":"point","country":"United States","country_gid":"whosonfirst:country:85633793","country_a":"USA","region":"New York","region_gid":"whosonfirst:region:85688543","region_a":"NY","county":"Kings County","county_gid":"whosonfirst:county:102082361","county_a":"BK","locality":"New York","locality_gid":"whosonfirst:locality:85977539","locality_a":"NYC","borough":"Brooklyn","borough_gid":"whosonfirst:borough:421205765","neighbourhood":"Flatlands","neighbourhood_gid":"whosonfirst:neighbourhood:85819585","label":"1279 EAST 37 STREET, Brooklyn, NY, USA","addendum":{"pad":{"bbl":"3076370038","bin":"3209116","version":"26c"}}}}],"bbox":[-73.985331,40.624792,-73.93952,40.642037]}
```

**Shape differences vs `/search`:** (a) each feature's `properties` **omit `confidence` and `match_type`** entirely (present in every `/search` feature); (b) `geocoding.query` nests `parser`/`parsed_text` before `size`, and `size` defaults to 10 (no explicit `size` was passed); `parsed_text` lacks `locality`/`admin` here (no borough token in the query). Feature `properties`/`geometry`/`addendum.pad` are otherwise identical in structure to `/search`. First feature = the same canonical `1279 37 STREET`, bbl 3052960043, bin 3340270.

---

## 6. MapPLUTO row — Socrata `64uk-42ks`
- **URL:** `https://data.cityofnewyork.us/resource/64uk-42ks.json?$where=bbl='3052960043'`
- **Retrieved:** 2026-09-19T04:00:03Z — HTTP 200, 1483 bytes, 1 row
- **X-SODA2 / freshness headers (verbatim):**

```
ETag: W/"aG90ZWwuMjUzNjdfM18xNTM4dV9OUTM1YkExOWNnYnlTTlZVdzNuYmFLZlk---gzipGT-Ctm3gZfhq48x4A8VwVo1elbg--gzip--gzip"
X-SODA2-Data-Out-Of-Date: false
X-SODA2-Truth-Last-Modified: Mon, 24 Aug 2026 20:20:51 GMT
X-SODA2-Secondary-Last-Modified: Mon, 24 Aug 2026 20:20:51 GMT
Last-Modified: Mon, 24 Aug 2026 20:20:51 GMT
X-Socrata-Region: aws-us-east-1-fedramp-prod
X-Socrata-RequestId: f280c580a03570ef4952b3c2f2248320
```
`X-SODA2-Fields` / `X-SODA2-Types` are also present and list the full 110-column schema; `bbl` appears in `X-SODA2-Types` as type **number**. (Full X-SODA2-Fields/Types header text elided here for length — it enumerates every column incl. those null-omitted from the row below; available on request.)

- **Body (verbatim):**

```json
[{"borough":"BK","block":"5296","lot":"43","cd":"312","ct2010":"226","cb2010":"1000","schooldist":"15","council":"39","zipcode":"11218","firecomp":"E240","policeprct":"66","healtharea":"6900","sanitboro":"3","sanitsub":"3D","address":"3622 13 AVENUE","zonedist1":"M1-2/R6A","spdist1":"MX-12","splitzone":false,"bldgclass":"K4","landuse":"4","easements":"0","ownername":"3622 THIRTEENTH LLC","lotarea":"2400","bldgarea":"6271","comarea":"4350","resarea":"1921","officearea":"1921","retailarea":"1979","garagearea":"0","strgearea":"450","factryarea":"0","otherarea":"0","areasource":"2","numbldgs":"2","numfloors":"3.0000000","unitsres":"2","unitstotal":"5","lotfront":"30.0000000","lotdepth":"80.0000000","bldgfront":"30.0000000","bldgdepth":"57.0000000","ext":"EG","proxcode":"0","irrlotcode":false,"lottype":"3","bsmtcode":"0","assessland":"43200.00000","assesstot":"331200.00000","exempttot":"0.00000","yearbuilt":"1931","yearalter1":"0","yearalter2":"0","builtfar":"2.61000000000","residfar":"3.00000000000","commfar":"2.00000000000","facilfar":"3.00000000000","affresfar":"3.90000000000","mnffar":"2.00000000000","borocode":"3","bbl":"3052960043.00000000","tract2010":"226","xcoord":"988343","ycoord":"173166","latitude":"40.6419763","longitude":"-73.9852516","zonemap":"22c","sanborn":"306A056","taxmap":"31606","plutomapid":"1","version":"26v2","sanitdistrict":"12","healthcenterdistrict":"39","bct2020":"3022600","bctcb2020":"30226001000","transitzone":"Outer Transit Zone"}]
```

Note `bbl:"3052960043.00000000"` (numeric, 8-decimal tail); `address:"3622 13 AVENUE"` (the address-of-record — NOT "1279 37 STREET"); `block:"5296"`, `lot:"43"`; PLUTO `version:"26v2"`, `zonemap:"22c"`. Many schema columns (e.g. `zonedist2`, `overlay1`, `condono`, `edesignum`, `geom`, `appbbl`) are **absent from the row** because they are null — SODA omits null fields.

---

## 7. DTM tax-lot polygon row — Socrata `i38t-6if2`

### 7a. With `$select` (geometry deliberately excluded via `$select` — no `the_geom` requested)
- **URL:** `https://data.cityofnewyork.us/resource/i38t-6if2.json?$select=bbl,boro,block,lot,condo_flag,bill_bbl_flag,effective_tax_year&$where=bbl='3052960043'`
- **Retrieved:** 2026-09-19T04:00:21Z — HTTP 200, 80 bytes, 1 row
- **X-SODA2 / freshness headers (verbatim):**

```
ETag: W/"anVsaWV0dC40MjU4NF8xXzc1MXFvT0VQYUZLc3I0YVBkN25aZDYzY3doNnE4---gzipgCFJ4F7-hihYPWXaRBzlY7CCU_M--gzip--gzip"
X-SODA2-Fields: ["bbl","boro","block","lot","condo_flag","bill_bbl_flag","effective_tax_year"]
X-SODA2-Types: ["text","text","number","number","text","number","text"]
X-SODA2-Data-Out-Of-Date: false
X-SODA2-Truth-Last-Modified: Wed, 02 Sep 2026 05:35:09 GMT
X-SODA2-Secondary-Last-Modified: Wed, 02 Sep 2026 05:35:09 GMT
Last-Modified: Wed, 02 Sep 2026 05:35:09 GMT
X-Socrata-Region: aws-us-east-1-fedramp-prod
X-Socrata-RequestId: bfa057d432bd93860bd1bb090ce86241
```

- **Body (verbatim):**

```json
[{"bbl":"3052960043","boro":"3","block":"5296","lot":"43","bill_bbl_flag":"0"}]
```

`bbl` here is Socrata type **text**, value `"3052960043"` (NO `.00000000` tail — differs from MapPLUTO). Although `condo_flag` and `effective_tax_year` were named in `$select`, both are **absent from the row** (null → SODA omits) — key absence = null/not-a-condo for this base tax lot. `bill_bbl_flag:"0"` = lot bills to itself.

### 7b. Without `$select` (full row incl. geometry)
- **URL:** `https://data.cityofnewyork.us/resource/i38t-6if2.json?$where=bbl='3052960043'`
- **Retrieved:** 2026-09-19T04:00:41Z — HTTP 200, 390 bytes, 1 row
- **Full field roster (from `X-SODA2-Fields` / `X-SODA2-Types` header, verbatim):**

```
X-SODA2-Fields: ["the_geom","boro","block","lot","bbl","condo_flag","reuc_flag","air_lot_flag","sub_lot_flag","easement_flag","lot_note","effective_tax_year","bill_bbl_flag","nycmap_bldg_flag","conversion_exception_flag","value_reflected_out_flag"]
X-SODA2-Types: ["multipolygon","text","number","number","text","text","text","text","text","text","text","text","number","number","number","number"]
```
Freshness headers identical to 7a (`X-SODA2-Truth-Last-Modified: Wed, 02 Sep 2026 05:35:09 GMT`, `X-SODA2-Data-Out-Of-Date: false`).

- **Body (verbatim — the whole row is only 390 bytes so `the_geom` is included rather than elided; the_geom is a MultiPolygon, 212 bytes minified, 5 coordinate pairs = a closed quadrilateral):**

```json
[{"the_geom":{"type":"MultiPolygon","coordinates":[[[[-73.9853973113,40.642024367772],[-73.98533248925,40.642085787218],[-73.985104300253,40.64194774461],[-73.985169121455,40.641886325994],[-73.9853973113,40.642024367772]]]]},"boro":"3","block":"5296","lot":"43","bbl":"3052960043","bill_bbl_flag":"0","nycmap_bldg_flag":"1","conversion_exception_flag":"0","value_reflected_out_flag":"0"}]
```

Keys present: `the_geom, boro, block, lot, bbl, bill_bbl_flag, nycmap_bldg_flag, conversion_exception_flag, value_reflected_out_flag`. **Null-omitted (in roster but absent from the row):** `condo_flag, reuc_flag, air_lot_flag, sub_lot_flag, easement_flag, lot_note, effective_tax_year`. `the_geom` is EPSG:4326 (lon/lat) — DTM WGS84 display geometry; not for measurement.

---

## 8. GeoSearch cache/version signal — headers + `addendum.pad.version`
- **URL:** `https://geosearch.planninglabs.nyc/v2/search?text=1279 37 street brooklyn&size=1`
- **Retrieved:** 2026-09-19T04:01:14Z — HTTP 200, 1560 bytes
- **Full response headers (verbatim):**

```
HTTP/1.1 200 OK
server: nginx/1.28.1
date: Sat, 19 Sep 2026 04:01:14 GMT
content-type: application/json; charset=utf-8
content-length: 1560
x-powered-by: pelias
charset: utf8
cache-control: public,private
access-control-allow-origin: *
access-control-allow-methods: GET, OPTIONS
access-control-allow-headers: X-Requested-With,content-type
x-robots-tag: none
etag: W/"618-LuIf1MFe7H8E6pJIBfjFhQQh2tE"
set-cookie: DO-LB="Cg4xMC4xMzIuMC4xMTo4MBCl94Eo"; Max-Age=300; Path=/; HttpOnly; SameSite=Lax
```

- **Version signals from the body:** `geocoding.version = "0.2"`; `geocoding.engine = {"name":"Pelias","author":"Mapzen","version":"1.0"}`; `geocoding.timestamp = 1789790474018` (epoch ms, per-request); `feature[0].properties.addendum.pad = {"bbl":"3052960043","bin":"3340270","version":"26c"}` → **`addendum.pad.version = "26c"`** (matches the expected 26c PAD release; observed identically on every GeoSearch feature in captures 1–5).

**Header-level cache/version findings:** GeoSearch exposes only a weak `etag` (`W/"..."`, changes with the response) and `cache-control: public,private`. There is **no `Last-Modified` and no dataset/PAD version HTTP header** — the only version stamp is the in-body `addendum.pad.version`. The `set-cookie: DO-LB=...` is an ephemeral DigitalOcean load-balancer routing cookie (`Max-Age=300`), regenerated per request; it is not a credential and carries no version signal.

---

## Assertions this corpus supports

1. **Success is NOT discriminable from `confidence`/`match_type` on `/search`.** True hit, GARAGE sibling, wrong-lot, garbage-street fallback, and out-of-range-housenumber fallback ALL return `confidence:0.8, match_type:"fallback"`. The connector MUST NOT gate a match on these fields.
2. **GeoSearch never returns an empty `features` array for these probes** — even a nonexistent street ("zzqqxx" → "1279 53 STREET") and an out-of-range number ("99999" → housenumber "207") return HTTP 200 with a bogus-but-real fallback lot. A no-match gate requires comparing returned `housenumber`/`street` against the parsed query, or cross-checking the returned `bbl` against PLUTO — presence-of-feature is not evidence of a correct match.
3. **Frontage aliasing:** "1279 37 STREET", "1279 GARAGE 37 STREET", and "3622 13 AVENUE" are distinct GeoSearch features that resolve to the **same bbl 3052960043**; the true building frontage and the reverse address-of-record share `bin 3340270` and identical coordinates, while the GARAGE has a different `bin` (3123204). Equality gate: match on `addendum.pad.bbl`, not on address string or `bin`.
4. **`/autocomplete` feature `properties` omit `confidence` and `match_type`** (present on `/search`); its `geocoding.query` uses `size:10` default and a reduced `parsed_text`. A connector reusing a `/search` parser on `/autocomplete` output must not require those two keys.
5. **PLUTO address-of-record ≠ user-typed address:** MapPLUTO `64uk-42ks` for bbl 3052960043 has `address:"3622 13 AVENUE"`, not "1279 37 STREET" — confirming the connector cannot assume the queried frontage equals PLUTO `address`.
6. **`bbl` is typed differently across the two Socrata datasets** — number in MapPLUTO (serializes `"3052960043.00000000"`) vs text in DTM (`"3052960043"`). Normalize to a 10-digit integer before joining; a naive string-equality join across the two will fail.
7. **SODA omits null columns** even when explicitly `$select`ed (DTM `condo_flag`/`effective_tax_year` absent for this base lot) and in default rows (MapPLUTO `zonedist2`, `condono`, etc.). Key ABSENCE = null; the authoritative full schema is in the `X-SODA2-Fields` header. Fixtures must assert key-absence tolerance, not explicit-null.
8. **This bbl is a plain base tax lot, not a condo:** DTM `condo_flag` null (omitted) and `bill_bbl_flag:"0"`; MapPLUTO `condono` null (omitted). Useful negative fixture for the condo path.
9. **Version stamps:** GeoSearch PAD `addendum.pad.version = "26c"` (matches expected 26c, uniform across all features); MapPLUTO `version = "26v2"`, `zonemap = "22c"`. Freshness is header-borne for SODA (`X-SODA2-Truth-Last-Modified`: MapPLUTO 2026-08-24, DTM 2026-09-02; `X-SODA2-Data-Out-Of-Date: false`) but body-only for GeoSearch (no Last-Modified/version HTTP header; only a weak etag).
10. **DTM `the_geom` is EPSG:4326 MultiPolygon (display only)** — a 5-vertex closed quad, 212 bytes here; do not use for measurement (measurement geometry is MapPLUTO/DTM in 2263 elsewhere per program rules).

---

### Notes / limitations
- No endpoint required or offered authentication; nothing was redacted except the disclosed elisions (MapPLUTO `X-SODA2-Fields`/`Types` full header text in §6; DTM `the_geom` was small enough to include verbatim in §7b). The ephemeral `DO-LB` LB cookie is shown as-returned and is not a secret.
- `geocoding.timestamp` is a per-request epoch-ms value and will differ on every call; it is not a dataset version.
- Files written during capture live only in the session scratchpad (`.../scratchpad/c1.json … c8.json`, `c6.hdr`, `c7a.hdr`, `c7b.hdr`, `c8.hdr`); no repository files were written except my agent-memory note.

**Requested status: awaiting_gate** (read-only research capture; suitable for a G1 verification pack for the DB-026 connector).
