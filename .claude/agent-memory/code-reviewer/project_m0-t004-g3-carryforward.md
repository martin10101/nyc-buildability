---
name: m0-t004-g3-carryforward
description: G3 findings from M0-T004 (monorepo+CI) that must be re-checked when M0-T009 finalizes the contracts
metadata:
  type: project
---

M0-T004 G3 (2026-07-14) passed with deferred defects that M0-T009 (canonical contract finalization) must close:

1. `packages/contracts/schemas/v1/property_profile.schema.json` provenance_record `required` omits `dataset_version`, `confidence`, `user_confirmed_or_overridden`, `conflict_status` — PRD section 9 mandates all four unconditionally (only `effective_date` is "where available"). `fact_value.provenance_ref` is also optional despite the schema's own prose requiring a provenance record per fact.
2. Invented enums not sourced from PRD (borough spellings, `conflicts[].resolution`, `conflict_status`) need validation against real connector outputs (e.g., Geoclient borough naming).
3. `.github/scripts/validate_contracts.py` only checks JSON parse + 4 top-level keys; no meta-schema or instance validation. M0-T009 should add real jsonschema validation + API contract tests.

**Why:** schemas were explicitly labeled v1 DRAFT pending M0-T009, so these were medium/low, not gate-blocking; they become high-severity if M0-T009 ships without fixing them.
**How to apply:** when reviewing M0-T009 (or anything binding to packages/contracts), verify these three items first.

Process facts confirmed this gate: ADR-005 workflow — sandboxed producers cannot run git/gh/python; the orchestrator executes commit/push/CI and appends an integration appendix to the producer report; reviewer is read-only and returns the report in-message. Remote is github.com/martin10101/nyc-buildability; CI evidence is verifiable read-only via `gh run view <id> --repo martin10101/nyc-buildability`.
