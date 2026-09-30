---
name: zola-deeplink-url
description: Confirmed NYC ZoLa deep-link URL template for a tax lot, zero-padding rules, and provenance (labs-zola Ember source)
metadata:
  type: reference
---

ZoLa (zola.planning.nyc.gov) lot deep-link — CONFIRMED from NYCPlanning/labs-zola Ember source (develop branch), verified 2026-09-12.

Canonical lot URL template: `https://zola.planning.nyc.gov/l/lot/<boro>/<block>/<lot>`
- Source: `app/router.js` — parent `this.route('map-feature', { path: '/l' }, ...)` wraps `this.route('lot', { path: 'lot/:boro/:block/:lot' })`.
- Segments are PLAIN INTEGERS with leading zeros stripped (NOT zero-padded): boro=1-5, block and lot as integers.
  - Proof: `app/utils/bbl-demux.js` decomposes BBL via `parseInt(substring, 10)` (strips zeros); reconstructs BBL from params via numeral format `'0'`/`'00000'`/`'0000'`. So `1000477501` -> boro 1, block 47, lot 7501 -> `/l/lot/1/47/7501`.

Convenience BBL route: `https://zola.planning.nyc.gov/bbl/<10-digit-bbl>` (`app/routes/bbl.js` calls `bblDemux` then `transitionTo('map-feature.lot', boro, block, lot)`). Client-side redirect to the `/l/lot/...` form. Best form for our UI since we hold the 10-digit BBL directly — no manual split needed.
- Legacy `/lot/:boro/:block/:lot` (no `/l`) exists as a `legacy-redirects` route (client-side redirects to `/l/lot/...`). README example is slightly stale (shows `/lot/1/47/7501` as the /bbl target).

Empirical (2026-09-12, curl): all of `/l/lot/1/47/7501`, `/bbl/1000477501`, `/lot/1/47/7501` return `HTTP/1.1 200`, identical SPA shell (Content-Length 24926, same Etag). Now hosted on Netlify (Cache-Status "Netlify Edge"; canonical Link -> zola.planninglabs.nyc/index.html). No server-side redirect observable — all routing (incl. /bbl and legacy redirects) resolves CLIENT-SIDE in Ember. Cannot HTTP-verify the redirect target; verified via source instead.

Caveats: condo billing lots (lot >= 1000 for some, unit lots) and lots not in PLUTO may render an error state client-side. Bbox route also exists: `/bbox/:west/:south/:east/:north` (WGS84).
