# M5-T004 — G0 readiness (orchestrator administrative gate)

**Task:** M5-T004 — Compare (Step 3) UI (apps/web) consuming the accepted M5-T003 scenario endpoint; offline/fixtures, no credentials.
**Reviewed content SHA:** 3879d4c4 (candidate/D-024-mrl-option-b — the commit that contracted the packet).
**Gate class:** G0 administrative readiness (recorded by the orchestrator; not an independent review gate).

## Readiness checklist (packet is dispatchable)

- [x] `objective` + `business_reason` present and scoped to a single user-facing product increment (Step 3 Compare).
- [x] `allowed_paths` (5) bound to the new apps/web Compare surface + the narrow ConfirmScreen rewire; `forbidden_paths` protect the accepted backend, the built contract, the read-only client templates, supabase, .claude, tools.
- [x] `acceptance_scenarios` — 8 executable AS (AS-1..AS-8): verbatim-cap render, no_scenario/professional-review, coverage labels, contract-safety-before-render, flag-off/upstream states, navigation, offline/no-creds, accessibility.
- [x] `documented_test_commands` present (vitest / typecheck / Playwright vs the committed-fixture API) with the thin-client evidence-capture note.
- [x] `required_gates` G0,G1,G3,G4,G5 + reviewer roster (code, qa, security, visual-quality, human-journey) appropriate for a frontend task.
- [x] `directive_refs` D-038:ALL; task is in-regime; D-038-R003 (product deliverable) + R004 (no-creds) resolve as applicable (validator EXIT=0).
- [x] No credential dependency: consumes the flag-gated endpoint / committed fixtures only (proves D-038-R004). No Supabase, no Geoclient, no backend change.
- [x] Dependency present: the M5-T003 scenario endpoint is ACCEPTED and on the candidate line (services/api/app/api/v1/scenario.py at 3879d4c4).

**Verdict: PASS (ready for claim + supervised dispatch).**
