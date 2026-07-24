# First-Wave Integration Contract (D-002 §5–§7)

**This is a contract, not a second ledger.** The authoritative packets are
`project-control/tasks/{M3-T001,M4-T007,M2-T017}.json`; this document freezes their interface and
collision surface so three "blind island" producer tabs can build in parallel without seeing one
another. The project-control ledger, D-002 registry, gates, and blockers remain the sole authorities.

- **Frozen first-wave base SHA:** the `origin/main` commit immediately AFTER the consolidation PR
  (branch `control/D-002-consolidation-2026-07-24`, task M0-T024) is merged. Recorded at worktree
  creation (D-002 §8 step 3) and written into each producer capsule. Every first-wave producer starts
  from this same SHA.
- **Wave size:** 3 producers (ceiling is 4). Lane 4 (auth/RLS) is **intentionally idle** — see §Idle.
- **No first-wave producer depends on another first-wave producer's unmerged output** (proven below).
- **Parallel production, sequential merging** (D-002 §11): merge one PR at a time, provider-before-consumer.

---

## Lane 1 — M3-T001 (legal-source authority foundation)
| Field | Value |
|---|---|
| Task ID / title | **M3-T001** — Legal-source authority hierarchy, corpus scope, coverage matrix, internal legal-source manifest |
| Base SHA | frozen first-wave base (above) |
| Dependencies (accepted) | **M1-T001** (accepted) — no first-wave sibling dependency |
| Complete outputs | `docs/SOURCE_AUTHORITY_POLICY.md`, `docs/LEGAL_CORPUS_COVERAGE_MATRIX.md`, `docs/CONSTRUCTION_CODE_RELEASE_SCOPE.md` (owner-approval draft), `docs/DOCUMENT_EVIDENCE_POLICY.md`, additive rows in `docs/SOURCE_ACCESS_REGISTRY.md`, `packages/contracts/schemas/v1/legal_source_manifest.schema.json` (NEW additive) + `packages/contracts/schemas/v1/fixtures/legal_source_manifest/**`, report |
| Allowed paths | the 5 docs above + `packages/contracts/schemas/v1/legal_source_manifest.schema.json` + `packages/contracts/schemas/v1/fixtures/legal_source_manifest/**` + `project-control/reports/M3-T001-*.md` |
| Forbidden paths | any `services/api/app/**` runtime; canonical contracts (property_profile/rule_evaluation/coverage_status/scenario/source_fact/analysis_state_transition); `apps/web/**`; `.claude/**` except own agent-memory; `project-control/**` except own reports + B-011 reference |
| Owned interfaces / schema versions | `legal_source_manifest.schema.json@v1` ($id + version deterministic; internal manifest, NOT a canonical cross-tier contract) |
| Read-only from main | `docs/SOURCE_ACCESS_REGISTRY.md` (existing rows byte-unchanged; additive only), M1 registry |
| Generated artifacts + sole owner | none touch typegen/schema-bundle (legal_source_manifest is not in `SCHEMA_FILES` nor a typegen target) |
| DB / migration ownership | none |
| Env-var ownership | none |
| Service / port ownership | none |
| Test / harness | executable JSON-schema validation of positive + negative manifest fixtures |
| Producer-report path | `project-control/reports/M3-T001-producer-report.md` (+ `M3-T001-architect-benchmark-analysis.md`) |
| Acceptance evidence | G0/G1/G2/G3/G4/G5; benchmark discrepancy findings; fixture validation |
| Stop conditions | construction-code scope approval (owner/B-011); genuine legal ambiguity; any need to touch runtime/canonical contracts |
| Downstream integration | M3-T002 (needs accepted M3-T001) — a LATER wave, not parallel |

## Lane 2 — M4-T007 (exact Decimal/legal-units arithmetic, DF-2)
| Field | Value |
|---|---|
| Task ID / title | **M4-T007** — Exact Decimal/legal-units arithmetic and rounding foundation |
| Base SHA | frozen first-wave base |
| Dependencies (accepted) | none (builds on already-merged M4 engine code on main) — no first-wave sibling dependency |
| Complete outputs | `services/api/app/rules/operations.py` (Decimal/rational), `services/api/app/rules/evaluator.py` (exact threshold comparisons; geometry-float isolation preserved), `services/api/app/rules/units.py` (NEW), `services/api/tests/rules/**`, report |
| Allowed paths | `services/api/app/rules/operations.py`, `.../evaluator.py`, `.../units.py`, `services/api/tests/rules/`, `project-control/reports/M4-T007-producer-report.md` |
| Forbidden paths | `packages/contracts/**`; `services/api/app/rules/rulesets/**` (published rule CONTENT); `dsl.py`/`lifecycle.py`/`registry.py`/`integration.py`; `services/api/app/profile/**` and `.../api/**`; all shared hotspots |
| Owned interfaces / schema versions | `units.py` decimal/unit helpers (frozen interface); no schema |
| Read-only from main | rule DSL/model types, ZR snapshots |
| Generated artifacts + sole owner | none |
| DB / migration ownership | none |
| Env-var ownership | none |
| Service / port ownership | none |
| Test / harness | property-based, differential (native vs independent Decimal recompute), adversarial exact-threshold + rounding tests, existing rules-engine suite |
| Producer-report path | `project-control/reports/M4-T007-producer-report.md` |
| Acceptance evidence | G0/G2/G3/G4/G5; no-float-on-legal-path check; threshold/rounding suites green; existing tests still pass |
| Stop conditions | any need to change rule CONTENT/semantics (G6 territory) or a canonical contract |
| Downstream integration | future M4 rule tasks consume the exact-math foundation once merged |

## Lane 3 — M2-T017 (source_fact + analysis_state_transition contract hardening, DF-4/DF-5)
| Field | Value |
|---|---|
| Task ID / title | **M2-T017** — Canonical source_fact + analysis_state_transition contract hardening |
| Base SHA | frozen first-wave base |
| Dependencies (accepted) | **M2-T003** (accepted; defined these contracts) — no first-wave sibling dependency |
| Complete outputs | closed `packages/contracts/schemas/v1/source_fact.schema.json` + `analysis_state_transition.schema.json`; `packages/contracts/generated/property_profile.ts` (regenerated iff changed; **sole owner this wave**); `services/api/app/_contract_schemas/v1/source_fact.schema.json` (byte-identical bundle); negative fixtures under `packages/contracts/fixtures/invalid/{source_fact,analysis_state_transition}/`; `services/api/app/contracts/serializers.py` (NEW; frozen interface, NOT wired); `services/api/tests/contracts/**`; report |
| Allowed paths | the two schemas; `packages/contracts/generated/property_profile.ts`; `packages/contracts/fixtures/{invalid,valid}/{source_fact,analysis_state_transition}/`; `services/api/app/_contract_schemas/v1/source_fact.schema.json`; `services/api/app/contracts/`; `services/api/tests/contracts/`; `project-control/reports/M2-T017-producer-report.md` |
| Forbidden paths | all other canonical schemas + their generated TS; `legal_source_manifest.schema.json` (lane 1); `services/api/app/profile/builder.py` + `.../api/**` (production wiring deferred to a later integration task); `services/api/app/rules/**` (lane 2); `packages/contracts/scripts/**` (shared generators frozen); all shared hotspots |
| Owned interfaces / schema versions | `source_fact.schema.json` (version/$id bumped), `analysis_state_transition.schema.json`; `contracts/serializers.py` (frozen interface) |
| Read-only from main | `packages/contracts/scripts/generate_ts_types.py`, `services/api/scripts/sync_contract_schemas.py` (run, don't edit); `profile/builder.py` (reference only) |
| Generated artifacts + sole owner | `packages/contracts/generated/property_profile.ts` (**M2-T017 is its sole owner this wave**); `services/api/app/_contract_schemas/v1/source_fact.schema.json` |
| DB / migration ownership | none |
| Env-var ownership | none |
| Service / port ownership | none |
| Test / harness | negative typo/undocumented-field/diagnostic-leak fixtures; serializer unit tests; `sync_contract_schemas.py --check` + `generate_ts_types.py --check` byte-identity |
| Producer-report path | `project-control/reports/M2-T017-producer-report.md` |
| Acceptance evidence | G0/G2/G3/G4/G5; closed-contract negative tests; byte-identical bundle/typegen; serializer not wired into the route |
| Stop conditions | if closing a contract would force a change to a shared production entrypoint/builder (submit interface-change request; do NOT wire it) |
| Downstream integration | a LATER controller-contracted integration task wires `serializers.py` into `profile/builder.py` after M2-T017 is accepted |

---

## Semantic collision matrix (D-002 §5) — proven disjoint
| Collision axis | M3-T001 | M4-T007 | M2-T017 | Overlap? |
|---|---|---|---|---|
| Source paths | docs/** + contracts/schemas/v1/legal_source_manifest.* | services/api/app/rules/{operations,evaluator,units}.py + tests/rules/ | contracts/schemas/v1/{source_fact,analysis_state_transition}.* + contracts/generated/property_profile.ts + app/contracts/ + app/_contract_schemas/v1/source_fact.* + tests/contracts/ | **none** (disjoint subtrees) |
| API contract / schema ID | legal_source_manifest (new) | none | source_fact, analysis_state_transition (existing) | **none** |
| DB table / migration | none | none | none | none |
| Config variable | none | none | none | none |
| Generated output | none (not in SCHEMA_FILES/typegen) | none | property_profile.ts + _contract_schemas/v1/source_fact.* (**sole owner**) | **none** (only lane 3 regenerates) |
| Source-of-truth doc | its 5 docs (owns) | none | none | **none** |
| Package / lockfile | none | none (Decimal is stdlib) | none | none |
| Deployment definition | none | none | none | none |
| Production entrypoint | none | rules/ internals only (no route wiring) | none (serializer NOT wired) | **none** |
| Provider/consumer version | — | does not consume source_fact schema at runtime | provider of source_fact vNext; consumed only AFTER merge+rebase | **none within wave** |

**Dependency independence:** M3-T001←M1-T001(accepted); M4-T007←(merged main code); M2-T017←M2-T003(accepted).
None depends on a sibling's unmerged branch. `property_profile.ts` and the runtime source_fact bundle copy
have exactly one wave owner (M2-T017). Different source paths never write the same generated file.

## Reserved shared hotspots (D-002 §6) — controller/integration-only, no first-wave producer may touch
`CLAUDE.md`; `.claude/**`; `.github/**`; directive registry + `tools/**` (control CLI, ledger, gate code,
control tests, `packages/contracts/scripts/**`); root dependency/lock files; `render.yaml` + deployment defs;
`services/api/app/main.py` + `.../api/**` production entrypoints; `services/api/app/profile/builder.py` shared
serializer wiring; shared generated artifacts other than each lane's sole-owned output; any other task's report.
A producer that finds a frozen interface must change **stops and submits an interface-change request** (§6).

## Idle lane 4 (D-002 §7.4) — auth/RLS/tenant-isolation foundation
**Intentionally idle, not prepared.** Its real acceptance path (apply migrations to Supabase + positive/negative
RLS cross-tenant tests on a real tenant-scoped DB) is prevented by **B-001** (Supabase management access token,
open) and forbidden by the thin-client no-local-database policy. Per D-002 §7 ("do not fill an unsafe fourth
slot"), only three genuinely independent lanes are prepared. Auth/RLS (Area I-foundation / DF-1) is contracted
at a fresh ID once B-001 clears.

## Planned downstream integration task (after providers merged)
A later controller-contracted integration task wires M2-T017's `contracts/serializers.py` into
`profile/builder.py` (schema-before-integration order), and consumes M4-T007's exact-math foundation in
subsequent M4 rule work. M3-T002 (needs accepted M3-T001) opens the next M3 wave. No shared-entrypoint wiring
happens inside any first-wave producer.
