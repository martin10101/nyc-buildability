# M5-T033 input evidence — live spatial-failure capture (orchestrator, 2026-09-17T07:21:18Z)

Captured by the orchestrator from this workstation with curl (30 s deadline) against the
deployed internal API (`nycdf-api` on Render, health `/api/v1/health` → 200 `{"status":"ok",
"version":"0.1.0"}` at 0.44 s; deployed backend commit per handoff: f0e7d82f, autoDeploy off).
This file is INPUT evidence for the M5-T033 root-cause task (D-059-R004). It records observed
responses only; it draws no final root-cause conclusion.

## Probes — `GET /api/v1/properties/{bbl}/rule-evaluation`

| BBL | Borough | HTTP | time | fail_safe_reason | coverage_status |
|---|---|---|---|---|---|
| 3052960043 (D-059 start parcel) | Brooklyn | 200 | 0.70 s | `spatial_intersection_absent` | `professional_review_required` |
| 3022647515 (D-059-R004 named parcel) | Brooklyn | 200 | 0.71 s | `spatial_intersection_absent` | `professional_review_required` |
| 1008350041 (control — 350 Fifth Ave, Manhattan; resolves cleanly in GeoSearch) | Manhattan | 200 | 0.58 s | `spatial_intersection_absent` | `professional_review_required` |

Shared response shape on all three: `fail_safe: true`, `needs_review: true`,
`professional_review_required: true`, `rule_lifecycle_statuses: []`, empty
`zoning_district` / `lot_area_sq_ft` provenance arrays, DRAFT not-verified disclaimer.

## Observed signal (for the producer to weigh, not a conclusion)

- The failure is UNIFORM across boroughs and across known-good vs. previously-failing
  parcels, and every response returns in ~0.6–0.7 s — far too fast for the live path's three
  sequential ArcGIS/SODA connector calls. This is the exact signature the code contract
  predicts for `LIVE_SPATIAL_PROVIDER_ENABLED` unset/false on the deployed service
  (`services/api/app/spatial/live_provider.py`: flag "unset by default on every deployed
  service"; `rule_evaluation.py` default provider yields None → evaluator fail-safe
  `spatial_intersection_absent`), as opposed to a per-parcel connector/data failure, which
  would differ by parcel and carry connector latency.
- Per D-059-R004 the runtime cause stays UNCONFIRMED until the deployed settings are read:
  the Render dashboard env listing for `nycdf-api` is OWNER-visible only. The producer must
  (a) reproduce both branches deterministically (flag unset → uniform absent; flag on +
  connector failure → typed per-parcel fail-safe), (b) bound what each observable signature
  distinguishes, and (c) hand the single owner dashboard check (env var present/absent) as
  the one remaining confirmation step with exact expected readings for both outcomes.
- `docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md` names `INTERNAL_RULE_EVAL_ENABLED` but
  NEITHER `LIVE_SPATIAL_PROVIDER_ENABLED` NOR `INTERNAL_SCENARIO_ENABLED` — the D-059-R004
  checklist requirement is currently unmet and is part of this task's scope.
