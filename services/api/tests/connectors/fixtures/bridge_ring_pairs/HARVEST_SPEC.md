# [ORCH-CORRECTED per M5-T073 data-contract review F2, 2026-09-24]: EXECUTED on
# 2026-09-23 (commit 06e3e72d) - pairs P05-P08 registered in pairs_manifest.json with
# kind raw_esri_body / raw_geojson_body; the _auth_response_body branch this spec asks
# for exists in the harness (kind == "raw_esri_body" returns the body verbatim). This
# file remains the re-run recipe; the stored layout is <pair_id>/<label>.json (the
# registration section's naming note covers the difference).

# HARVEST_SPEC — net-new real bridge-ring pairs (M5-T073, DB-045(a))

The offline worker measured the 4 real pairs available from the accepted fixture
packs (see [`PROVENANCE.md`](PROVENANCE.md)). To satisfy the packet's **≥8 real
pairs / ≥3 boroughs / regular-small-lot** coverage, the orchestrator harvests
**≥4 more pairs** through the two live connectors (network egress the worker
lacks). Fixtures are captured VERBATIM; nothing here is fabricated. Once dropped
in, the harness picks them up through `pairs_manifest.json` with no code change.

## What to add (fills the gaps in the current sample)

Add pairs in the boroughs and classes NOT yet covered — at minimum one each in
**Bronx (2), Brooklyn (3), Staten Island (5)** (to reach ≥3 boroughs), plus at
least one **small regular residential lot** (row-house-scale, single exterior
ring), to reach ≥8 pairs total. Candidate query targets below are STARTING
POINTS; the capture verifies each returns `single_lot` (display) and
`single_feature` (authoritative) with a usable exterior ring, and SUBSTITUTES
another BBL in the same borough+class if not (record the substitution).

| target class | borough | note |
|---|---|---|
| small regular residential lot | Bronx (2) | single exterior ring, ~standard lot |
| small regular residential lot | Brooklyn (3) | single exterior ring, ~standard lot |
| irregular / corner lot | Staten Island (5) | non-rectangular exterior |
| curved-edge / waterfront lot | any of 2/3/5 | curved boundary densification stress |

## Capture procedure (re-runnable; keyless official ArcGIS)

For each canonical BBL, GET BOTH connector URLs and store each body VERBATIM. The
URLs are built by the accepted connectors (BBL only from `normalize_bbl`):

```
# run from services/api
python - <<'PY'
import urllib.request
from app.connectors.mappluto_lot_outline import build_outline_query_url      # f=geojson&outSR=4326
from app.connectors.mappluto_geometry_arcgis import build_lot_query_url      # f=json (EPSG:2263)
bbl = "2........."  # each harvested canonical 10-digit BBL
for label, url in (("display_4326", build_outline_query_url(bbl)),
                   ("authoritative_2263", build_lot_query_url(bbl))):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    body = urllib.request.urlopen(req, timeout=40).read()
    open(f"{bbl}_{label}.json", "wb").write(body)
PY
```

Digest each stored body: `sha256:` + lowercase-hex SHA-256 over the exact UTF-8
bytes of the body (for the authoritative body this is the same basis the harness
re-checks: `response_body_sha256`).

## How to register a harvested pair

Either (a) store the two verbatim bodies under
`services/api/tests/connectors/fixtures/bridge_ring_pairs/<pair_id>/` and point
the manifest at them, or (b) if the capture is added to the M2-T009 / M5-T020
packs, reference those paths (as the existing 4 pairs do). Append an entry to
[`pairs_manifest.json`](pairs_manifest.json) mirroring the existing shape:

```json
{
  "pair_id": "P05_regular_small_bronx_2XXXXXXXXX",
  "bbl": "2XXXXXXXXX",
  "borough": "Bronx",
  "borough_code": 2,
  "geometry_class": "regular_small_residential_lot",
  "notes": "…",
  "display": {
    "source_fixture": "bridge_ring_pairs/P05_.../display_4326.json",
    "kind": "raw_geojson_body",
    "endpoint": "<build_outline_query_url output>",
    "retrieved_at": "<UTC RFC3339>",
    "source_file_sha256": "sha256:<hex over stored body bytes>"
  },
  "authoritative": {
    "source_fixture": "bridge_ring_pairs/P05_.../authoritative_2263.json",
    "kind": "raw_esri_body",
    "endpoint": "<build_lot_query_url output>",
    "retrieved_at": "<UTC RFC3339>",
    "response_body_sha256": "sha256:<hex over stored body bytes>"
  }
}
```

Note: `kind` for a directly-stored esri body is `raw_esri_body`; the harness's
`_auth_response_body` currently unwraps `response_body_raw` from a
provenance-envelope fixture (`provenance_envelope.response_body_raw`). If a pair
stores the raw esri body directly instead, extend `_auth_response_body` to return
the body verbatim for `kind == "raw_esri_body"` (a one-branch change routed to
the orchestrator, since the test file is the producer's scope this wave).

## Verify

Run from `services/api`:

```
python -m pytest tests/connectors/test_bridge_ring_preconditions.py -q -s
```

`-s` surfaces the emitted verdict table (per-pair vertex counts, RMS residual,
alignment separation, pass/refuse + refusal class) for the producer report's AS-3
table. A precondition-violating pair is a FINDING, never a test failure.
