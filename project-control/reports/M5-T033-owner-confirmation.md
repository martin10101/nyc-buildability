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
4. Secondary observations, honestly bounded: `ztldb_soda source freshness: dataset rows last
   updated 2026-04-05 (age 164.6 days > 45-day threshold)` on every request — the CITY's
   ZTLDB dataset is stale at the source (the known "observed live stall" in the connector
   comments); logged, non-blocking today, a data-quality watch item for the G6 era. And BBL
   3022647515 logged `event=no_candidate_districts error_type=none` — its ZTLDB record
   carries an empty zoning assignment, an honest data-sufficiency absence distinct from the
   pin failure (candidate future work: condo/billing-lot assignment coverage).
