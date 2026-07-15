# @nyc-buildability/contracts

Versioned JSON Schema contracts shared by all modules (web, API, workers,
rules, reports). Individual modules may not invent competing schemas
(PRD section 32.3).

## Status: v1 DRAFTS

The schemas in `schemas/v1/` are **v1 draft stubs** created in task M0-T004 to
establish the monorepo skeleton and CI. They are **pending finalization in
task M0-T009** (canonical contract definition). Do not treat field lists as
frozen until M0-T009 is gated.

| Schema | Purpose | PRD reference |
| --- | --- | --- |
| `schemas/v1/property_profile.schema.json` | One canonical property profile: identity/address, BBL/BIN, geometry, lot facts, existing-building facts, zoning, project intent, per-fact provenance, missing inputs, conflicts, user confirmations, profile version | 9, 32.3 |
| `schemas/v1/coverage_status.schema.json` | Single coverage status per result, plus data-completeness status in `$defs` | 12 |
| `schemas/v1/analysis_state.schema.json` | Deterministic analysis-run workflow states | 32.1 |

## Versioning rules

- Schemas are immutable per version directory (`v1`, `v2`, ...).
- Breaking changes require a new version directory and a migration note.
- CI validates that every schema parses and declares `$schema` and `$id`.
