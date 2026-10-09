# Condo substrate-substitution recon (2026-09-20, seq 121; read-only Explore return, saved VERBATIM)

Trigger: owner's live 298 Wallabout St question (billing BBL 3022647515 →
`spatial_intersection_absent`, calculations withheld). Purpose: scope the future
substitution-stamp packet. NOT a contract; the packet contracts at a seam after
M5-T056 accepts (several proposed paths are T056-held today).

Orchestrator reading of the live evidence (added context, not part of the return):
the deployed head includes the accepted M5-T045 condo pre-lookup, and the control
parcel returns a REAL spatial answer (`geometry_uncertain`), so live spatial IS on —
the Wallabout outcome is most consistent with a MULTI-lot condo fail-safe
(`resolved_base_bbl` set only on OUTCOME_RESOLVED_SINGLE; the records view showed
multiple tax lots). The refusal is by design; the gap is the discarded resolution
record + the generic refusal name. R004/Q6 verification still applies at packet time.

---

## Recon return (verbatim)

### Headline

The substitution **already happens**, one layer too deep to be visible.
`build_live_substrate` resolves a billing BBL to its base lot and runs the whole
spatial pipeline on the base lot today — but the `CondoResolution` is discarded at the
seam boundary and survives only as a log line. The ready-made *record* producer
(`condo_resolution_report`) has **zero production callers**. So the packet is not
"find the base lot"; it is "carry the resolution across the substrate seam and stamp it."

### 1. Seam map — spatial_intersection producer → consumer

- Substrate produced (live, flag-gated): `services/api/app/spatial/live_provider.py:237`
  `build_live_substrate`; default seam `:313` `default_live_substrate`.
- BBL whose geometry is fetched is decided at `live_provider.py:258-290` —
  `substrate_bbl` = `condo.resolved_base_bbl` on `substitutes_base_lot`, else the input;
  `fetch_ztldb(substrate_bbl…)` `:280`, `fetch_lot(substrate_bbl…)` `:290`.
- Substitution recorded (log only, never in payload): `live_provider.py:221-234`
  `_record_condo_substitution`. Condo fail-safe → `None` substrate `:263-267`.
- Provider seam type + DI: `services/api/app/api/v1/rule_evaluation.py:110`
  `SpatialSubstrateProvider = Callable[[str, str], object | None]`; `:117`
  `get_spatial_substrate_provider`.
- Profile assembles the section: `services/api/app/profile/wave_integration.py:292`
  `_spatial_intersection_section`, mounted `:408-412`; entry
  `services/api/app/profile/builder.py:622/:822`.
- Four route consumers: `rule_evaluation.py:301-302`, `evidence.py:502`,
  `scenario.py:255`, `scenario_analysis.py:520`.
- Consumer that emits the failure: `services/api/app/rules/integration.py:617-633` —
  non-dict spatial → `_fail_safe(FAILSAFE_SPATIAL_ABSENT)` (constant `:87`; the exact
  live reasons[0] string `:625-629`).
- Caveat: live `3022647515` evidence is not by itself proof the condo step failed —
  flag-off returns `None` with an identical symptom (R004 protocol,
  docs/WORKING_KNOWLEDGE.md:115-119, :389-391). Root-cause first.

### 2. Condo resolver chain and its reach

- Transport leaf: `services/api/app/connectors/dtm_condo_soda.py`.
- Policy seam (accepted, M5-T045): `services/api/app/connectors/condo_base_lot.py` —
  `resolve_condo_billing` `:148`; typed `CondoResolution` `:88-140` with
  `resolved_base_bbl` (set ONLY on `OUTCOME_RESOLVED_SINGLE`), full `base_bbls`,
  `condo_key`, `resolution_path`, `source_id`, `dataset_ids`, `retrieved_at`,
  `provenance`, `divergent_zoning_notice`, and `is_pass_through` /
  `substitutes_base_lot` / `is_fail_safe`.
- Output is a base-lot BBL PLUS records — exactly what a substitution stamp needs.
- Reachable from the spatial path (`live_provider.py:42/:157-163`,
  `_ACTIVE_CONDO_RESOLVER`) and the condo-records route (`api/v1/condo_records.py:181`).
  NOT reachable from the profile path — `services/api/app/profile/zoning_crosscheck.py`
  (`condo_resolution_report` `:524`, `CONDO_RESOLUTION_FIELD` `:491`, machine token
  `:511-521`) has no production caller (tests only). The profile's
  `additional_conflicts`/`additional_notes` channel (`builder.py:618-619`, `:767`,
  `:784`) is the ready landing pad and is unused by every route.

### 3. AnalysisIdentityNotice feed + existing typed substitution shape

- Fed from `document.evaluated_input.bbl` vs the entered BBL:
  `apps/web/src/components/architect/AnalysisIdentityNotice.tsx:29-31`; mounted at
  `ArchitectEntry.tsx:169-170` and `ReportView.tsx:84-85`.
- Backend origin: `services/api/app/rules/response.py:154-161` builds
  `evaluated_input` from `profile.identity.bbl` (the ENTERED BBL today). Scenario
  mirrors: `app/scenario/builder.py:274/:341`, disagreement guard `:436/:724`.
- A typed entered-vs-analyzed record ALREADY EXISTS:
  `services/api/app/api/v1/condo_records.py:442-460` `_substitution_record` →
  `{entered_bbl, analyzed_bbl, note}`, surfaced as `document["substitution"]` `:519`;
  web reads it via `apps/web/src/lib/condo-records.ts`. Reuse this shape — never a second one.
- DB-036(d) collision, concretely: stamping `evaluated_input.bbl` with the base lot
  makes `AnalysisIdentityNotice` fire "identity mismatch — results withheld" beside the
  substitution record's shown allowances. Recorded at
  `project-control/reports/M5-T052-HJ.md:13` and `docs/DISCOVERY_BACKLOG.md:143` (d).

### 4. Minimal disjoint packet surface

Contract shape blocks the cheap route: `rule_evaluation.schema.json` is
`additionalProperties:false` with a closed `contract_version` enum ["1.0.0","1.1.0"]
and a closed `fail_safe_reason` enum; `evaluated_input` is also closed. A new
`substrate_substitution` block (or a `condo_substrate_unresolved` fail-safe reason)
needs an additive 1.2.0 bump — follow the M5-T037 `wide_street` precedent exactly.

Proposed allowed_paths (disjoint from T054/T055/T056 EXCEPT where flagged):
`packages/contracts/schemas/v1/rule_evaluation.schema.json`,
`packages/contracts/generated/rule_evaluation.ts`,
`services/api/app/_contract_schemas/v1/rule_evaluation.schema.json`,
`services/api/app/spatial/live_provider.py`,
`services/api/app/api/v1/rule_evaluation.py`,
`services/api/app/rules/integration.py`,
`services/api/app/rules/response.py`,
(`services/api/app/profile/builder.py` only if the stamp lands on the profile),
`services/api/tests/spatial/test_live_provider.py`,
`services/api/tests/api/test_rule_evaluation_api.py`,
`services/api/tests/rules/test_rules_integration.py`,
`services/api/tests/contracts/test_rule_evaluation_contract.py`,
`apps/web/src/lib/rule-evaluation-contract.ts`,
`apps/web/src/lib/__tests__/contract-versions.test.ts`,
`apps/web/src/components/architect/AnalysisIdentityNotice.tsx`,
a NEW `__tests__/analysis-identity-substitution.test.tsx` (NOT the T056-held
`condo-resolution-display.test.tsx`), producer report.
Deliberately excluded: `condo_base_lot.py`/`dtm_condo_soda.py` (complete),
`zoning_crosscheck.py` (wire only if profile-landing), `evidence.py`/`scenario.py`/
`scenario_analysis.py` (keep the old provider contract if the seam widens compatibly).

### 5. Overlap verdict vs live lanes

Disjoint from T055 entirely. Conflicts with T056 ONLY via the condo test/lib/route
files — all excluded above; the DB-036(d) coupling test goes in a NEW spec file. Net:
contractable disjointly, but sequence AFTER T056 accepts for safety.

### 6. Existing tests/fixtures for the billing-lot spatial-absent case

- `services/api/tests/spatial/test_live_provider.py:585-680` — M5-T045 condo
  pre-lookup block; `_BILLING_BBL = "3022647515"` `:592`; asserts base-lot fetches
  `:614-619`, the substitution log `:626`, fail-safe→None zero-lookup for
  multi-lot/unresolved/error `:640-658`; doubles `:200-225`.
- `services/api/tests/api/test_rule_evaluation_api.py:971-1097` — deployed
  `spatial_intersection_absent` reproduction (D-059 parcels); `:1097` positive control.
- `services/api/tests/rules/test_rules_integration.py:374-385` — uniform
  absent-substrate → exactly `spatial_intersection_absent`.
- `services/api/tests/profile/test_ztldb_crosscheck.py:474-580` — full
  `condo_resolution_report` coverage; profile round-trip `:551`.
- Web: `apps/web/src/test-support/rule-evaluation-fixtures.ts:35`,
  `development-limits.test.tsx:449`, label map `lib/architect/development-limits.ts:156`.
- NO fixture exists for end-to-end "billing BBL → base lot → real substrate → stamped
  result" — the packet's headline new fixture.

### Open design questions (decide at contract time)

1. Where the stamp lives: `evaluated_input` (closed; 1.2.0) vs new top-level
   `substrate_substitution` block vs the profile note channel (zero-bump but only
   `properties.py`/`rule_evaluation.py` build profiles; `properties.py:393` passes no
   substrate).
2. Seam signature: widen `SpatialSubstrateProvider` to `(record, resolution)` (touches
   four routes) vs a parallel provider (doubles the SODA call unless memoized per
   `(bbl, correlation_id)`).
3. Does `evaluated_input.bbl` change? If yes → DB-036(d) fires and the notice must
   learn substitution (mismatch WITH a substitution record is legitimate). If no → the
   stamp alone carries it, but `evaluated_input.bbl` names a BBL whose geometry was
   never used. The packet's central decision.
4. Honest refusal vocabulary: multi-lot/unresolved/typed-error condo outcomes all
   collapse into generic `spatial_intersection_absent` today; adding
   `condo_base_lot_unresolved` is the honest refusal (same contract bump + web enum
   update at `rule-evaluation-contract.ts:88-95`).
5. Lot-area provenance: on the substituted path `lot_area_source` is the BASE lot's
   area while lot_geometry/PLUTO facts describe the billing lot — mixed-substrate area
   is a real correctness risk the stamp should make visible.
6. R004 prerequisite: confirm from the deployed commit + `LIVE_SPATIAL_PROVIDER_ENABLED`
   whether the live 3022647515 failure is flag-off or a genuine condo fail-safe before
   scoping — the fix differs entirely.
