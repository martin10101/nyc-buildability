# Location and zoning maps — data sources and licence record (task E-07, plan §5c-2)

The map builder `services/api/app/drawings/maps/` draws server-made vector SVG
location and zoning maps from NYC **city open data only**. This note records
each source and its licence, and why no raster base-map imagery is drawn. It is
evidence for the "licence-checked imagery only" requirement; it is not a legal
determination.

## What the maps draw

- **Location map** — the subject lot (emphasised, labelled by its BBL) among the
  surrounding **building footprints**, so the reader can see where the lot sits.
- **Zoning map** — the subject lot against the **zoning-district boundaries**,
  each district labelled by its verbatim `ZONEDIST` symbol read from the data,
  with the official use-limitation, horizontal-accuracy and attribution notes.

Every coordinate is **EPSG:2263 (NAD83 / New York Long Island, US survey feet)**
— the authoritative measurement CRS. The maps never reproject and refuse any
other CRS (`adapter.SUPPORTED_CRS`). Every printed label and note is read from
the data and keeps a JSON-pointer source (check C-4).

## Vector data sources and licences

All three vector sources are NYC city open data governed by the **NYC Open Data
Terms of Use** (`https://opendata.cityofnewyork.us/overview/#termsofuse`),
access rights **Public**, with no prohibition on automated API access. Facts
below are from the repository's recorded source research, not re-derived here.

| Layer | Dataset / field | Owner | Licence / terms (recorded source) |
|---|---|---|---|
| Lot outline | MapPLUTO / DOF Digital Tax Map outline | DCP / DOF | NYC Open Data terms; DCP informational-purposes disclaimer; **± 20 ft** horizontal accuracy; **not a legal boundary survey** (`docs/SOURCE_ACCESS_REGISTRY.md` §§ MapPLUTO / DTM) |
| Zoning districts | NYC GIS Zoning Features `nyzd`, field **`ZONEDIST`** | DCP | NYC Open Data terms; data "freely available … to the public"; **official use limitation (verbatim): "These features are not intended for determining zoning at the individual tax lot level"**; **± 20 ft** horizontal accuracy (`docs/SOURCE_ACCESS_REGISTRY.md`; `docs/research/zoning-features-ztldb-2026-07-16.md` Z11) |
| Building footprints | OTI Building Footprints, NYC Open Data `5zhs-2jue` | OTI | SODA `license` = none set → governing terms are the **NYC Open Data Terms of Use**; access rights Public; no prohibition on automated API access (`docs/research/building-footprints-source-2026-09.md` §6) |

### Zoning use-limitation is honoured in the drawing

Because `nyzd` "is not intended for determining zoning at the individual tax lot
level", the zoning map is deliberately **not** a lot-level zoning determination:

- all districts share one neutral wash — the map never colour-codes a district
  into a use class; the exact `ZONEDIST` symbol is the only classification and it
  is the label;
- the verbatim use-limitation note and the ± 20 ft accuracy note always appear
  on the map (sourced to the data);
- the subject lot is drawn from its own tax-map outline, independently of the
  district polygons.

## Base-map imagery (aerial / street): left out on purpose

§5c-2 allows aerial or street imagery **only** from sources whose licence allows
use in reports. This increment draws **no** raster base map or map tiles: no
imagery licence was confirmed from a publisher's own page for this task, so per
the Lane E instruction the base map is omitted and the maps are vector city data
only. The SVG contains no `<image>` element and no external `href` (asserted by
`tests/drawings/maps/test_maps.py::test_no_raster_base_map_imagery`). Adding a
base map later requires recording the tile/imagery licence from the publisher
first (e.g. an orthophoto layer's own terms).

## Tests

Tests use recorded-shape synthetic fixtures under
`services/api/tests/drawings/maps/fixtures/`; **no live service is called**. The
fixtures carry the official attribution, accuracy and use-limitation text so the
provenance notes are exercised. The whole kit (maps + E-01 drawings) is behind
`LANE_E_ENABLED` (off in production).
