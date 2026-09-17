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
