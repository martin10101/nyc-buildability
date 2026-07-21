# M2-T012 — Producer report

Task: **M2-T012 Profile integration of wave connectors + spatial results (single contract 1.4.0 update).**
Producer: orchestrator (lead-only, owner directive 2026-07-21). Status: `claimed`, G0 PASS, **implementation not started**.

## Session resume checkpoint (2026-07-21)

- **Branch:** `task/M2-T012-profile`.
- **HEAD:** this checkpoint commit; its parent is merge commit `cabe419d94bc6b2ac43b0cccadc8db75e9cc20e2`
  (resolve live with `git -C .claude/worktrees/M2-T012-profile rev-parse HEAD`).
- **origin/main integrated:** `047d31cda0f76c07ca62339ae42dd9f19f0afac0` (PR #73 lean context architecture),
  merged into this branch at `cabe419…` — clean merge, no conflicts. The branch now carries the slim
  CLAUDE.md, path-scoped `.claude/rules/`, and `docs/archive/`.
- **Implementation code exists yet:** **NO.** Zero code under `services/api/app/**`, `packages/contracts/**`,
  or `apps/web/**` on this branch.
- **Files changed vs base (`6f9d603`):** only the G0 control files —
  `project-control/gates/M2-T012-G0.json` (A), `project-control/reports/M2-T012-G0-readiness.md` (A),
  `project-control/state.json` (M), `project-control/tasks/M2-T012.json` (M) — plus this report and the
  origin/main merge. Worktree clean.
- **Baseline (pre-implementation):** `python -m pytest tests/api/test_property_contract.py tests/profile/
  tests/spatial/ tests/api/test_contract_schema_packaging.py` → **103 passed** on the local API env
  (Python 3.11.9, jsonschema 4.26.0, shapely 2.0.7).

### Completed architectural inspection (first-hand, no guessing)
- `services/api/app/profile/contract.py` — `SUPPORTED_CONTRACT_VERSIONS` is read **live** from
  `property_profile.schema.json` `properties.profile_version.properties.contract_version.enum`;
  `VERSION_INTRODUCED` (dotted-path → introducing version) drives the declared-vs-emitted consistency
  check; `validate_profile()` does structural → unsupported-version → consistency → full JSON-Schema.
  Publishing 1.4.0 = append `"1.4.0"` to the enum + register any new keys here.
- `services/api/app/profile/builder.py` — `PROFILE_CONTRACT_VERSION = "1.3.0"`; additive
  `additional_provenance` / `additional_conflicts` / `additional_notes` hooks (M2-T008 pattern); fixed
  top-level profile shape; `_assert_provenance_integrity`.
- `packages/contracts/schemas/v1/property_profile.schema.json` — additive, open-object pattern
  (`mapped_features`, `conflicts` deliberately open; per-fact provenance_ref required; closed
  `contract_version` enum `["1.0.0"…"1.3.0"]`).
- `services/api/app/spatial/models.py` — `LotIntersectionRecord.as_dict()`: `pairs` (exact geometric
  facts + `share_min/point/max` ranges + `pair_class` uncertainty), `lot_overall_class`,
  `professional_review_required`/`review_reasons`, `crosscheck`, `unassigned_area`/`overlap_area`,
  `accuracy_records`, permanent `coverage_note` ("never a Verified determination"); `coverage_audits`
  is **INTERNAL — not a published contract field**; integrate a **selected subset** without collapsing
  uncertainty.
- `services/api/app/profile/zoning_crosscheck.py` — `crosscheck_lot_zoning(pluto, ztldb, external_observations)`
  + `external_observation(...)`; the `external_observations` hook is the seam for the **fourth (geometric)
  evidence stream**.
- `services/api/app/api/v1/properties.py` — API path (`STATUS_STATE_MATRIX`, `build_property_profile`
  call); the live endpoint fetches PLUTO only. M2-T012 endpoint scope is "typed error surface only if the
  new keys require it"; the integration lands in the builder+contract and is fixture/unit-tested (no live
  multi-connector orchestration; that would need credentials — out of scope here).
- `services/api/app/connectors/mappluto_geometry_arcgis.py` — `LotGeometryResult` / `GeometryAssessment`
  (bbl, status, `review_required`, `canonical_geometry`, `area_sq_ft`, digests, provenance).
- Not yet inspected (read first in the new session): the zoning-features connector result class
  (`app/connectors/zoning_features_arcgis.py`), the spatial engine entry (`app/spatial/__init__.py`,
  `engine.py`, `adapter.py`), the M2-T010 sync/typegen tooling (`services/api/scripts/sync_contract_schemas.py`
  + the `contracts-typegen` script), the six enumerated carried-defect sites, the existing test patterns
  (`tests/profile/test_data_semantics.py`, `tests/api/test_property_contract.py`), and
  `apps/web/src/lib/**` declarations.

### Owner decision (scope)
**ONE coordinated contract 1.4.0 PR** (owner, 2026-07-21). Do not split; implement the full packet in this PR.

### Required contents of the 1.4.0 PR (from the packet)
1. **Three integrations** into the canonical profile with full provenance: (a) zoning-features citywide
   facts (M2-T007 six layers), (b) per-BBL MapPLUTO geometry facts (M2-T009), (c) M2-T013 spatial-intersection
   records (exact geometry, boundary distances, uncertainty classes, split-share ranges, professional-review
   flags).
2. **Fourth geometric evidence stream** — extend the PLUTO/ZTLDB/zoning-features cross-check to include the
   geometric assignment; disagreements surface through the existing conflict shape.
3. **Uncertainty preservation** — never collapse M2-T013 uncertainty into a definitive assignment anywhere
   in the profile or payload (hard STOP condition).
4. **Contract 1.4.0** published through the M2-T010 derivation tooling (schema enum + bundled-copy sync +
   TS typegen + client-lib declaration derive automatically; drift red-path proven). Additive-only;
   1.0.0–1.3.0 payloads must still validate; unsupported-version fail-closed unchanged.
5. **PI-S1 … PI-S8** acceptance scenarios (primary, uncertainty-preservation, conflict, back-compat, drift
   tooling, carried defects, missing-data, regression).
6. **Generated declarations** — client + backend version declarations derived through M2-T010; bundled-schema
   sync + typegen drift checks green.
7. **Enumerated carried LOW-defect fixes** (each with its own test evidence): M2-T009 metadata-TTL-cache
   option; M2-T007 G3/G4 (untested drift signals, test-name mismatch, count==cap default-page test); M2-T008
   G3/G4 D1 (`check_columns_for_drift` TypeError on doubly-malformed metadata) + O2 (`SOCRATA_APP_TOKEN` test
   hermeticity); M2-T007 G1 D1 (`out_fields` footgun typing); M2-T009 G4 D1 (top-level metadata
   `spatialReference` assertion).

### Next exact implementation action
Read the not-yet-inspected shapes listed above (zoning-features result class, spatial engine entry, M2-T010
sync/typegen tooling, carried-defect sites, existing test patterns, web lib). Then design + write the
**additive contract 1.4.0 schema** in `packages/contracts/schemas/v1/property_profile.schema.json`: append
`"1.4.0"` to the `contract_version` enum and add OPTIONAL top-level keys for (a) zoning-features facts, (b)
lot-geometry facts, and (c) the spatial-intersection record with uncertainty preserved; update
`app.profile.contract.VERSION_INTRODUCED`. Prove back-compat (1.0.0–1.3.0 fixtures still validate) before
touching the builder.

### Blockers
**None.** All dependencies (M2-T010, M2-T011, M2-T013) are accepted; the local API test env works; the
fixture-based integration needs no credentials.

### Gate status
No reviewer has been dispatched. The submit SHA is **not frozen**. Task remains `claimed` — not submitted,
not accepted, no checkpoint advanced, no PR opened.
