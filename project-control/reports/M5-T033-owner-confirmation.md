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

## Post-change probe (appended when captured)

- PENDING at first write: rule-evaluation re-probe of 3052960043 / 3022647515 / 1008350041
  after the Render restart.
