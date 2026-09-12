<!-- Researcher return preserved VERBATIM by the orchestrator (report-preservation rule;
transport entity-decoding applied: &lt; -> <, &gt; -> >, &amp; -> &). Author: independent
official-source-researcher subagent, returned 2026-09-12 (UTC). This resolves the
address-entry design spec's flagged assumption (a) — the exact ZoLa URL shape — and is a
named input to the M5-T016 (address Packet 2) task packet. -->

# ZoLa lot deep-link — CONFIRMED

The design spec's assumed template is **correct**, including the `/l/` prefix. Verified against NYCPlanning/labs-zola Ember source (develop branch) plus live HTTP checks, retrieval date **2026-09-12**.

## 1. Verified path template

```
https://zola.planning.nyc.gov/l/lot/<boro>/<block>/<lot>
```

Segment meaning and format:
- `<boro>` — borough **digit 1-5** (1=Manhattan, 2=Bronx, 3=Brooklyn, 4=Queens, 5=Staten Island).
- `<block>` — tax block as a **plain integer, leading zeros stripped** (NOT zero-padded).
- `<lot>` — tax lot as a **plain integer, leading zeros stripped** (NOT zero-padded).

Source of truth — `app/router.js`:
- Parent: `this.route('map-feature', { path: '/l' }, function () { ... })`
- Child: `this.route('lot', { path: 'lot/:boro/:block/:lot' })`
- So the full route path is `/l/lot/:boro/:block/:lot`.

**Zero-padding is authoritatively resolved by `app/utils/bbl-demux.js`:** it splits a 10-digit BBL with `parseInt(substring, 10)` (which strips leading zeros) for block and lot, and only re-pads (`numeral(...).format('00000')` / `'0000'`) when reconstructing a 10-digit BBL string — never in the route params.

Example: BBL `1000477501` -> boro `1`, block `00047`->`47`, lot `7501`->`7501` -> **`https://zola.planning.nyc.gov/l/lot/1/47/7501`**.

## 2. Is it a stable, citable pattern? Yes — and there's a better option for you

ZoLa exposes an explicit **BBL convenience route** intended for exactly this outbound-link use case. From the repo README: *"For convenience to other apps that work with NYC BBLs (10-digit Borough, Block, and Lot identifiers), a `/bbl` route is available for incoming links. Incoming connections on this route will be redirected to the corresponding lot view."*

```
https://zola.planning.nyc.gov/bbl/<10-digit-bbl>      e.g.  /bbl/1000477501
```

`app/routes/bbl.js` calls `bblDemux(params.bbl)` then `transitionTo('map-feature.lot', boro, block, lot)`, i.e. it redirects (client-side) to the `/l/lot/...` view. **Recommendation: use the `/bbl/<bbl>` form.** You already hold the canonical 10-digit BBL, so you avoid doing the split/zero-strip yourself and delegate that to ZoLa's own parser. Both forms are equally documented/stable.

## 3. Empirical verification (curl, 2026-09-12)

All three forms return the SPA app shell — expected for an Ember SPA:

| URL | Status | Notes |
|---|---|---|
| `/l/lot/1/47/7501` | `200 OK` | HTML shell, Content-Length 24926 |
| `/bbl/1000477501` | `200 OK` | identical shell (same Etag) |
| `/lot/1/47/7501` (legacy) | `200 OK` | identical shell |

All three return byte-identical shells (same `Etag: "31ba7877...ssl"`, same Content-Length). The site is now served via **Netlify** (`Cache-Status: "Netlify Edge"`; `Link: <https://zola.planninglabs.nyc/index.html>; rel="canonical"`). **No server-side redirect is observable** — the server returns the SPA shell for every path and all redirecting (`/bbl` -> `/l/lot`, legacy `/lot` -> `/l/lot`) happens **client-side in the Ember router**. Path acceptance was therefore confirmed from source rather than from an HTTP 3xx.

## 4. Alternative / legacy forms

- **`/bbl/:bbl`** — recommended convenience route (above).
- **Legacy `/lot/:boro/:block/:lot`** (no `/l` prefix) — still present as a `legacy-redirects` route that client-side-redirects to `/l/lot/...`. The README example text showing `/bbl/1000477501` -> `/lot/1/47/7501` is slightly stale; the actual live target is the `/l/lot/...` form. Avoid emitting the bare `/lot/...` form for new links.
- **`/bbox/:west/:south/:east/:north`** — WGS84 bounding-box route (not lot-specific).
- No query-string lot form is defined in the router. When you view a lot on ZoLa today, the address bar shows the `/l/lot/<boro>/<block>/<lot>` form.

## 5. Provenance to record

- `github.com/NYCPlanning/labs-zola`, branch `develop`, files: `app/router.js` (route paths incl. `map-feature` path `/l` and `lot` path `lot/:boro/:block/:lot`), `app/routes/bbl.js`, `app/utils/bbl-demux.js` (parseInt strip / numeral re-pad), `README.md` (`/bbl` and `/bbox` documentation). Retrieved 2026-09-12.
- Live HTTP check of the three URLs above, 2026-09-12 (200 OK, SPA shell, Netlify-hosted).

## Caveats

- **Client-side routing:** a wrong/nonexistent BBL still returns HTTP 200 (SPA shell); "not found" is a client-side state, so you cannot use HTTP status to validate a lot before linking. Validate the BBL against your own PLUTO data first.
- **Condo/billing lots:** unit/billing lots (high lot numbers) and lots absent from PLUTO may render a client-side error/empty state in ZoLa even though the URL is well-formed.
- **Host migration:** the app is now served through Netlify with a canonical link to `zola.planninglabs.nyc`; `zola.planning.nyc.gov` remains the DCP-branded public host and is the one to use for outbound links.

**Bottom line:** template CONFIRMED as `https://zola.planning.nyc.gov/l/lot/<boro>/<block>/<lot>` with unpadded integer segments; prefer `https://zola.planning.nyc.gov/bbl/<10-digit-bbl>` for outbound links since you hold the canonical BBL.

Sources:
- [NYCPlanning/labs-zola (repo)](https://github.com/NYCPlanning/labs-zola)
- [labs-zola app/router.js (develop)](https://raw.githubusercontent.com/NYCPlanning/labs-zola/develop/app/router.js)
- [labs-zola app/routes/bbl.js (develop)](https://raw.githubusercontent.com/NYCPlanning/labs-zola/develop/app/routes/bbl.js)
- [labs-zola app/utils/bbl-demux.js (develop)](https://raw.githubusercontent.com/NYCPlanning/labs-zola/develop/app/utils/bbl-demux.js)
- [labs-zola README.md (develop)](https://github.com/NYCPlanning/labs-zola/blob/develop/README.md)
