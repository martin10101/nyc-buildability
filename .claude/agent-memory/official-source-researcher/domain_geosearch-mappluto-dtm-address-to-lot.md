---
name: domain-geosearch-mappluto-dtm-address-to-lot
description: Verified wire behavior of GeoSearch v2, MapPLUTO (64uk-42ks) and DTM (i38t-6if2) for address→lot resolution — success-discrimination pitfalls, bbl typing, null-omission
metadata:
  type: reference
---

Verified 2026-09-19 UTC against live endpoints (keyless GET; no auth exists for any of these). Supports the future DB-026 address→lot connector.

## GeoSearch v2 (geosearch.planninglabs.nyc/v2/{search,autocomplete})
- Keyless; served by Pelias behind nginx. Response is a GeoJSON FeatureCollection; per-feature NYC data lives in `properties.addendum.pad` = `{bbl, bin, version}`. `version` observed `26c` (PAD release stamp).
- **`confidence` and `match_type` do NOT discriminate success.** Both a true hit and pure-garbage queries return `confidence:0.8, match_type:"fallback"`. A nonexistent street ("1279 zzqqxx street") returns a *different real lot* (fell back to "1279 53 STREET") at 0.8/fallback; an out-of-range house number ("99999 37 street") returns "207 37 STREET" (house number silently dropped) at 0.8/fallback. **All still HTTP 200 with a non-empty `features` array** — never trust presence-of-feature or these two scores as a match gate. Must validate returned `housenumber`/`street` against the query, or cross-check bbl against PLUTO.
- `/autocomplete` feature `properties` **omit `confidence` and `match_type` entirely** (present in `/search`); default `size:10`, query object nests `parser`/`parsed_text` inline. Otherwise same addendum.pad shape.
- Multiple frontages of ONE lot are distinct features with the SAME bbl: "1279 37 STREET" (bin 3340270) and "1279 GARAGE 37 STREET" (bin 3123204) both → bbl 3052960043. Reverse query "3622 13 avenue" → same bbl 3052960043, bin 3340270, identical coords. PLUTO address-of-record for that bbl is "3622 13 AVENUE", NOT the "1279 37 STREET" the user may type.
- Cache/version headers: only a weak `etag` (`W/"…"`) and `cache-control: public,private`; NO Last-Modified/dataset-version header. Version signal lives in the BODY (`addendum.pad.version`, `geocoding.engine.version` "1.0", `geocoding.version` "0.2"). `set-cookie: DO-LB=…` is an ephemeral DigitalOcean LB routing cookie (Max-Age 300), not a credential — changes per request.

## bbl typing differs by dataset (equality-gate trap)
- MapPLUTO `64uk-42ks`: `bbl` is Socrata type **number**; value serializes as `"3052960043.00000000"` (8-decimal tail). `$where=bbl='3052960043'` (string literal) still matched. address field = the address-of-record.
- DTM `i38t-6if2`: `bbl` is Socrata type **text**; value `"3052960043"` (no tail). Do NOT assume the same literal form across the two — normalize to 10-digit int before joining.

## SODA null omission (confirmed again)
- SODA JSON omits null columns even when named in `$select`. DTM `$select=…,condo_flag,…,effective_tax_year` returned a row WITHOUT those keys for a base tax lot → key ABSENCE means null/not-a-condo, not "field missing from schema". Full field roster is in the `X-SODA2-Fields` header regardless. `bill_bbl_flag:"0"` = lot bills to itself.
- Freshness cross-check available free: `X-SODA2-Truth-Last-Modified` / `X-SODA2-Data-Out-Of-Date` on every SODA response.

See also [[project-nyc-source-fetch-channels]].
