# M5-T062 DCV — directive-compliance verification (verbatim verifier return)

Verifier: directive-compliance-verifier (claude-opus-4-8 per D-064), FRESH dispatch by the
orchestrator in seq 124 (the seq-123 DCV was killed mid-run by the opus session limit),
pinned to the frozen submit head 0366210c. Recorded by the orchestrator; the verifier is
read-only and records nothing itself. Verbatim return follows.

---

VERDICT: PASS

# M5-T062 Directive-Compliance Verification (DCV)

Independent verification at the frozen submit head. Producer ≠ verifier: every requirement judged on primary repository evidence (code / tests / CI conclusions / gate records / git objects), reproduced myself. The producer report and evidence map were treated as claims.

## Identity verification performed
- Frozen head `0366210c` = `0366210cc6161b27ff3771f1423616a139910ab6` (exists; commit). Composition confirmed: material `0539cc84` (8 files, all inside allowed_paths) + [ORCH-CORRECTED] `099c32a7` (touches only `services/api/tests/api/test_site_definition_api.py`, in-scope) + one docs-only commit at the head.
- Task surface byte-stable across the disjoint peers: `git diff 0366210c..HEAD (d92b1c0a) -- <each of the 8 allowed_paths>` = empty for all 8. So the G3/G4 reviews recorded at `95e9977a` (manifest `650a48c1…`) and the CI at `0366210c` both pin the same byte-identical task identity.
- Material scope clean: `git show --stat 0539cc84` = exactly the 8 allowed_paths; no forbidden path (condo_records / connectors / rules / scenario / spatial / profile / packages/contracts / apps/web) touched.
- CI at the frozen head (reproduced via gh, not from the map): CI run **35547702435 success** — all 18 jobs green including `api (ruff + pytest)`, `modularity`, `control-plane`, `web`, `web-e2e`; `secret-scan` 35547702453 success; `context-budget` 35547702474 success. (Material `0539cc84` CI was red on the mount-presence introspection only — run 35546337617 — root-caused as the fastapi-0.139 `_IncludedRouter` layout blind spot in the TEST; correction `099c32a7` fixed the introspection and the frozen head is fully green.)
- Directive registry integrity: `tools/validate_directive_compliance.py --check` EXIT=0 locally; also wired into CI at `.github/workflows/ci.yml:442` inside the green `control-plane` job. All source digests / locked requirement ids validate; the three D-078 requirements (requirement_count 3) all read and present.
- No open blocker references M5-T062 (scan of `project-control/blockers/` for `T062` = none), so `accept()`'s `_blocker_references` scan is clear.

## Up-front statements
1. **Disjoint-peer tolerance:** My verdict REMAINS VALID if further DISJOINT peer commits — touching none of M5-T062's 8 allowed_paths (e.g. an M5-T066 contract seam, an M5-T065 submit seam, loop-relaunch/handoff artifacts, gate-record commits) — land between this verdict and the acceptance record. The verdict is bound to the byte-stable task surface, which those peers do not alter.
2. **Conditional restamp pre-authorization:** The orchestrator MAY restamp this verdict at a later head `H` WITHOUT a new dispatch iff the predicate `git diff 0366210c..H -- <the 8 allowed_paths listed in M5-T062.json> is empty` holds (byte-identical task surface). Record `reviewed_sha = H`; the reviewed content identity is unchanged from `0366210c`. If any of the 8 allowed_paths differs at `H`, this pre-authorization is void and a fresh DCV is required.

## Per-requirement verdicts

| Req | Verdict | Primary evidence (reproduced) |
|---|---|---|
| D-066-R001 | **SATISFIED** | Packet `project-control/tasks/M5-T062.json` inputs[3] carries the graph-derived navigation block (regenerated at seam `fffbd002`: 783 files/16500 nodes/7221 edges) + the `query.py --no-regen impact` instruction — the orchestrator obligation. Material conclusion verified in source: `git show 0539cc84 -- app/main.py` = only the flag-gated `if site_definition_write_enabled(): application.include_router(site_definition_v1_router)` block + its two import lines (main.py:203-218); condo_records.py and connectors are not in the 8-file diff (consumed read-only). |
| D-077-R002 | **SATISFIED** | Full contract drill on this lane: G0 PASS `project-control/gates/M5-T062-G0.json` (reviewer orchestrator, `reviewed_sha fffbd002b3ef…`, PASS); claim with the FULL worktree path `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m5t062` (M5-T062.json `worktree`); progress_log 20→85; lane cycled to submit at the green head `0366210c`. One of the three concurrent lanes; does not raise the D-072 max of 3. |
| D-077-R003 | **SATISFIED** | Scope stayed inside the released DB-040 / D-078 site-definition queue; no held work selected. Material touched only the 8 allowed_paths — no `apps/web/**` (the held M5-T060 proposal-editor and M5-T063 condo web lanes), no `connectors/rules/scenario/spatial/profile`. Mount ships DEFAULT OFF (no new production surface). No new scope granted or taken. |
| D-078-R001 | **SATISFIED** (task-scoped slice 2a) | Flag-gated mount default OFF: `site_definition_write_enabled()` returns False on absent/empty/unknown env (`app/api/v1/site_definition.py:121-135`); `main.py` registers the router only when true; `test_router_is_not_mounted_in_main_app_by_default` + `test_flag_off_is_generic_404_with_no_correlation_leak` prove it. Record substrate hardened (caps/index/matrix/typed refusals) and the multi-lot flow exercised end-to-end: `test_…298-Wallabout` (billing 3022647515), `test_created_confirmation_surfaces_on_the_condo_records_document` (write→read coherence). All green in CI run 35547702435. |
| D-078-R002 | **SATISFIED** | No auto-selection: create requires an explicit human confirmer + parcels from the request body (`app/api/v1/site_definition.py:492-533`, `confirmer_map.get("name"/"role")`, `proposed_parcels=block.get("parcels")`); handler is double-gated (`internal_rule_eval_enabled()` → generic 404 when off) on top of the registration flag. Revoke binds on the STORED record's condo_key/BBLs and never re-selects: `store.py` `revoke()` + `_matches_addressed_property()` (lines 350-431) — scope-before-status, `condo_key=None` never skips scoping. Tests: `test_attestation_is_server_set…` (server-set identity), `test_degraded_revoke_still_rejects_a_foreign_property_probe`, `test_revoke_binds_scope_before_status…`. `__init__.py` docstring states the boundary explicitly (D-078-R002). |
| D-078-R003 | **SATISFIED** | Sequencing honored: M5-T056 ACCEPTED (239th, commit `8705be52`/`5f52d153`) BEFORE T062's G0 at `2026-09-20T21:45` (fffbd002); the pair tasks M5-T058 + M5-T059 both ACCEPTED (state.json accepted_tasks); T062 is the recorded DB-040 successor slice; G0 disjointness record present. No phase-B order / hold / Tier-D stop altered. |

## Security-critical spot-reproduced (AS-1 / AS-2)
`store.py revoke()` (0366210c:services/api/app/site_definition/store.py:373-431) evaluates the property-scope match BEFORE the ACTIVE-status check: a foreign-property record returns `ConfirmationNotFoundError` (404) whatever its status — no 409-vs-404 cross-property status oracle (AS-1). A degraded resolver (`condo_key=None`) falls back to `addressed_bbl in (record.billing_bbl, record.entered_bbl)` so withdrawal at the record's own property still succeeds while a foreign probe stays 404 (AS-2, D-051 fail-direction). Directly covered by `test_revoke_binds_scope_before_status_so_a_foreign_non_active_record_is_404` and `test_revoke_survives_a_degraded_resolver_via_the_addressed_bbl_fallback`, both green in CI.

## Result
All 6 applicable requirements SATISFIED. No VIOLATED / UNVERIFIABLE / BLOCKED. Identity byte-stable, CI green (18/18 + secret-scan + context-budget), registry validator EXIT=0, no blocking blocker. **VERDICT: PASS.**

(G5 security gate was noted as running in parallel with this DCV and is outside my scope; acceptance still requires the recorded G5 result. My PASS covers the directive-requirement evidence only.)
