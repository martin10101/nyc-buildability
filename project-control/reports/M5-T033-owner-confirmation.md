# M5-T033 follow-up — owner dashboard reading CONFIRMS the runtime cause (2026-09-17)

Recorded by the orchestrator. The accepted M5-T033 record is immutable; this is the
post-acceptance confirmation the task's §2 handed to the owner.

## The reading (owner, verbatim)

> "LIVE_SPATIAL_PROVIDER_ENABLED it didn't have this so I added it under environmental
> variables under the nycdf api"

## What it settles

- The decisive discriminator from the accepted diagnosis (producer report §2, checklist
  §6b): `LIVE_SPATIAL_PROVIDER_ENABLED` was **ABSENT** on `nycdf-api` → the code-contract
  fail-safe default DISABLED → the provider returned no substrate for every BBL → the
  uniform, fast `spatial_intersection_absent` captured on 2026-09-17T07:21:18Z.
- This matches reproduced Branch A exactly (uniform across boroughs and the known-good
  control, ~0.6–0.7 s, zero connector latency) — the runtime cause of the deployed
  `spatial_intersection_absent`, previously held UNCONFIRMED, is now **CONFIRMED as the
  absent flag** for that captured deployment. D-059-R004's remaining confirmation step is
  complete.
- The owner has now ADDED the variable (value as typed by the owner in the dashboard;
  active only if it is one of the true tokens `1|true|yes|on` — checklist §6a). Post-change
  verification probes per checklist §6b run at the seam and are appended below when the
  service restart settles.

## Post-change probe (captured 2026-09-17 ~10:1x UTC)

- All three BBLs still return `spatial_intersection_absent` BUT the latency signature
  changed decisively: uniform 0.58–0.71 s before the owner's change → **1.55–2.80 s,
  variable, across six repeated probes** after it (health endpoint steady at 0.16 s).
  Per the accepted diagnosis this is the ENABLED-path signature (real connector calls now
  run per request); the disabled-flag branch is excluded for the observed runtime.
- Per checklist §6b the remaining cause is established only from correlated typed
  evidence: the owner reads the `nycdf-api` service logs for
  `live_spatial_substrate fail_safe event=<connector_error|no_candidate_districts|district_page_partial> …`
  lines (the ~9 probe requests just generated fresh ones). The typed `event=`/`error_type=`
  values name the exact remaining fix. Requested from the owner in-chat.

## Typed-log evidence (owner-pasted Render logs, 2026-09-17 10:01–10:05 UTC) — CONFIRMED CAUSE #2

The owner pasted the full deploy + runtime log. Correlated findings:

1. **The env-var save triggered a fresh deploy of candidate head fd9c644c** ("Checking out
   commit fd9c644c…"). The build line shows **"Using Python version 3.14.3 (default)"** —
   the service does not pin a Python version, and Render's default moved to 3.14. pip then
   installed `shapely==2.0.7` as a **locally-built `cp314` wheel** ("shapely-2.0.7-cp314-
   cp314-linux_x86_64.whl" — no manylinux wheel exists for 3.14, so it compiled from source
   against the build image's system GEOS).
2. Nearly every probe then logged `live_spatial_substrate fail_safe event=connector_error
   error_type=RuntimeError` with matching correlation ids. The only bare-`RuntimeError`
   raiser on the live spatial path is **`assert_geometry_pins`**
   (`services/api/app/spatial/geometry.py:62`): it fails closed unless the runtime carries
   the proven build `shapely==2.0.7` + `GEOS 3.11.4` (`mappluto_geometry_arcgis.py:207-208`;
   the requirements lock is compiled for Python 3.12 and CI proves the stack on 3.12).
   **Confirmed cause #2: unpinned Python → source-built shapely against a non-pinned GEOS →
   the geometry-pin guard refuses to compute legal geometry on an unproven build.** The
   guard behaved exactly as designed; this mismatch was latent on every prior deploy and
   invisible until the flag went live — precisely the "enabled path can expose an additional
   problem" scenario the accepted diagnosis bounded.
3. **Fix (owner one-liner):** on `nycdf-api → Environment`, add `PYTHON_VERSION` = `3.12.11`
   (any current 3.12.x; the lock and CI are proven on 3.12, where pip installs the prebuilt
   manylinux shapely 2.0.7 wheel bundling GEOS 3.11.4). Save → redeploy → re-probe.
   Follow-up: the deploy checklist should gain this pin (bounded doc follow-up task; the
   checklist file is not in any active packet's scope right now).
### Post-pin probe (2026-09-17T10:12:06Z) — the live spatial path RUNS end-to-end

Owner set `PYTHON_VERSION=3.12.11`; the rebuild (owner-pasted log, deploy of 216378e5)
installed shapely 2.0.7 as the prebuilt cp312 manylinux wheel. Probes now DIVERGE per
parcel — the uniform signature is gone:

| BBL | fail_safe_reason | time |
|---|---|---|
| 3052960043 | `geometry_uncertain` | 3.53 s |
| 3022647515 | `spatial_intersection_absent` (empty ZTLDB assignment → no_candidate_districts) | 1.43 s |
| 1008350041 | `geometry_uncertain` | 3.06 s |

Reading: the geometry-pin guard passes, all three connectors fetch, and the M2-T013
engine composes and CLASSIFIES in production for the first time. D-059-R004's runtime
chain: cause #1 flag absent (CONFIRMED, fixed) → cause #2 unpinned Python vs geometry
pins (CONFIRMED, fixed) → per-parcel honest outcomes.

### Both residual outcomes verified CORRECT against the city's own records (2026-09-17)

- **1008350041 (350 Fifth Ave) `geometry_uncertain` is RIGHT, not over-caution.** The
  city's ZTLDB row for the lot lists **TWO zoning districts — `zoning_district_1: C5-3`
  AND `zoning_district_2: C6-4.5` — plus `special_district_1: MiD`** (Special Midtown),
  zoning map 8D. The lot is genuinely SPLIT-ZONED; a confident single-district claim would
  be false. The engine's refusal is the correct conservative outcome; supporting split-lot
  apportionment (ZR 77-series class) is future scope, and this supersedes the earlier
  "candidate next defect" framing.
- **3022647515 (298 Wallabout St, Brooklyn) `spatial_intersection_absent` is RIGHT.**
  ZTLDB returns **0 rows** for the BBL, while PLUTO shows it is a **condominium record**
  (`condono: 1313`, building class R4, lot 7515 in the 7501+ condo-billing range,
  zonedist1 R7-1). The zoning-lot database tracks the underlying LAND lot, not condo
  billing/unit BBLs — so "no zoning-lot record" is true for the queried BBL. The product
  gap is a condo→base-lot resolution step before the ZTLDB lookup (exactly the
  D-059-R007 benchmark's "condo/billing lots" hard class); honest absence today is the
  designed behavior.

4. Secondary observations, honestly bounded: `ztldb_soda source freshness: dataset rows last
   updated 2026-04-05 (age 164.6 days > 45-day threshold)` on every request — the CITY's
   ZTLDB dataset is stale at the source (the known "observed live stall" in the connector
   comments); logged, non-blocking today, a data-quality watch item for the G6 era. And BBL
   3022647515 logged `event=no_candidate_districts error_type=none` — its ZTLDB record
   carries an empty zoning assignment, an honest data-sufficiency absence distinct from the
   pin failure (candidate future work: condo/billing-lot assignment coverage).
