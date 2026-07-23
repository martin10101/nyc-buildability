# Whole-System Trust Replan — Control-Only Proposal (2026-07-23)

**Control-only.** Owner directive 2026-07-23 Part 3. No merge, task movement, claim, dispatch, implementation, acceptance, checkpoint, deployment, purchase, dependency install, or PR closure. This is a **proposal**: it maps every discovered gap to an existing task, a proposed packet area, a blocker, or an explicit continuing limitation. **No new task IDs are contracted** (per the directive — IDs are assigned only after the ledger is reconciled and this proposal is approved). This is a **separate lane from PR #93** (the legal-source/document-corpus lane).

`/replan-project` was invoked. Evidence below is grounded in a read-only codebase inventory (three independent sweeps); file:line citations are to the canonical main tree (`origin/main` = `1acb9b5`).

> **Completeness note (owner directive):** this replan is complete only when every discovered gap has an explicit disposition. §3 (inventory) and §4 (defect matrix) each carry a disposition column; nothing is left in narrative.

---

## 1. Reconciliation (independently verified)

| Item | Value |
|---|---|
| `origin/main` | `1acb9b5` (unchanged) |
| PR #93 | OPEN, head `7ff5304` (rev-5 legal-corpus lane; five packets; not merged) |
| PR #91 | OPEN, superseded (not closed) |
| PR #94 | OPEN (Part 1 frontend-security reconciliation) |
| PR #64 (M0-T019) | OPEN, 115 behind / 8 ahead of main (stale; superseded) |
| Ledger | 42 accepted / 8 awaiting_gate / 9 backlog / 2 blocked / 1 claimed |
| M4-T007+ | uncontracted |

---

## 2. End-to-end dataflow trace + immutable-storage hierarchy

**Production surface today = ONE synchronous endpoint.** `GET /api/v1/properties/{bbl}` (`services/api/app/api/v1/properties.py:306`): `normalize_bbl` → injected PLUTO fetcher (resilient) → `build_property_profile(result)` (PLUTO-only) → `validate_profile` → 200. The frontend calls only this (`apps/web/src/lib/api.ts:168`). **No auth, no database, no run orchestrator, no snapshot set, no report/export.**

| # | Boundary | Implementation | Storage / owner | Identity+dates+hash | State model | Retry/timeout/cancel | Invalidation | PRODUCTION-INVOKED |
|---|---|---|---|---|---|---|---|---|
| 1 | address/BBL → identity | `connectors/bbl.py normalize_bbl` (`properties.py:318`) | none (inline) | canonical BBL only | typed 422 on malformed | n/a | n/a | **yes** (BBL only; **no address/geosearch connector wired** despite fixtures) |
| 2 | source connectors | `connectors/pluto_soda.py:600 fetch_by_bbl` → `PlutoFetchResult` | none persisted (result object) | provenance_id, fact_key, value_digest, response_digest, dataset_version, retrieved_at; `effective_date=None` | conflicts, drift_signals, absent_columns | typed errors; drift never retried | digest-based | **PLUTO yes; ZTLDB / MapPLUTO-geometry / zoning-features connectors NO** (built+tested, not wired) |
| 3 | resilience/retrieval (nearest thing to "capture") | `resilience/fetcher.py:146 ResilientPlutoFetcher` | **in-memory `TTLCache` + LKG, process-local, lost on restart** (`resilience/cache.py`, `fetcher.py:105`) | version-segmented cache key; `staleness` stamped | staleness surfaced to profile | bounded retry, breaker, budget; **no cancellation** | TTL/LRU/key-version; LKG superseded on success | **yes** |
| 4 | extraction/normalization | `pluto_soda._normalize_value:525` over 108-col inventory | in result.facts | value_digest/response_digest | drift_signals, absent_columns, notes | inherited | digest | **yes; no AI extraction exists** |
| 5 | canonical profile | `profile/builder.py:557 build_property_profile` → `property_profile@1.4.0` | HTTP body only; `profile_revision` hard-coded `1` | `reproducibility` block (correlation_id, dataset_version, retrieved_at, response_digest, staleness) | 5 independent `status_dimensions`; `rule_coverage="not_computed"` | route 500 guard | none (stateless rebuild) | **yes (PLUTO-only); wave/geometry/spatial keys NO** (route passes none) |
| 6 | source reconciliation | `profile/zoning_crosscheck.py:319 crosscheck_lot_zoning` (PLUTO×ZTLDB×geom) | would flow to profile | canonical facts | typed cross-source conflicts | connector resilience | n/a | **no** (route never passes it; single-source only) |
| 7 | spatial analysis | `spatial/engine.py` (shapely) via `spatial/adapter.py` | result object | policy/geometry-version pins | rich uncertainty taxonomy; PRR | ArcGIS resilience | geometry-version | **no** (rule-eval endpoint hard-defaults spatial substrate to `None`, and is flag-off) |
| 8 | rule applicability & precedence | `rules/integration.py:446 evaluate_property` → `rule_evaluation@1.0.0` | result object | rule_id/version, evaluated_as_of, in_effect | 6 coverage statuses; conflict → FAILSAFE, never auto-picked; caps at `conditional`; `assert_not_verified` | pure | rule lifecycle (no `published`) | **partial — flag-gated OFF** (`config.py INTERNAL_RULE_EVAL_ENABLED`, default 404; no `as_of_date`, no spatial → fail-safe PRR) |
| 9 | deterministic calc (FAR) | `rules/evaluator.py` + `rules/operations.py` + DSL | trace | ZR snapshot pins | fail-closed on unresolved provenance | pure | snapshot-version | **partial — same flag** |
| 10 | scenario generation | `scenario/builder.py:342 build_scenario` → `scenario` schema | result doc | needs_review + not-Verified always | envelope constraints all `missing`; typed `no_scenario` | pure | n/a | **no — no scenario endpoint exists at all** |
| 11 | human review / publication | `rules/lifecycle.py` states; `analysis_state*` schemas | **none — no workflow engine, no persistence, no transition** | — | labels only | — | — | **no** |
| 12 | report / UI / export | `apps/web` profile UI (`lib/contract-matrix.ts`, client re-validate); AbortController+12s timeout | — | — | (status,state) matrix enforced | abort/timeout | — | **profile UI yes; rule-eval surface NO (flag-off); report/export ABSENT** |

**Immutable-storage hierarchy that SHOULD exist (proposed, §5):** raw response bytes (content-addressed, immutable, dedup, replayable) → per-analysis `source_snapshot_set` (compatibility + permitted skew) → canonical entities (versioned) → evidence spans (M3-T003 lane) → rule releases (hashed) → run record (immutable run id, as_of_date, snapshot set, rule release, engine/config hashes) → report (pins the full manifest). **Today none of this is persisted** — "storage" is an in-memory TTL cache (`resilience/cache.py`); `supabase/migrations/` holds only `.gitkeep`.

---

## 3. Inventory of deferred/incomplete work — with dispositions

Every item maps to: an **existing task**, a **proposed packet area** (§5 letter), a **blocker**, or an **explicit continuing non-launch limitation**. Grouped by area. (The ~150 `professional_review_required` rule occurrences are one intentional fail-closed pattern — "no canonical field exposes this modifier" — consolidated under D, not reprinted.)

| # | Item (file:line) | Type | Disposition |
|---|---|---|---|
| A1 | `connectors/mappluto_geometry_arcgis.py:10` deferred geometry connector | deferred task | existing M2 geometry lane (B-001/B-002) |
| A2 | `api/v1/properties.py:141` drift-monitor **STUB** | stub | proposed **B** (orchestrator/source-monitor) |
| A3 | PLUTO/ZTLDB/geometry/zoning-features connectors built but **NOT wired** to production route (§2 rows 2/6/7) | unwired | proposed **A/B** (wire via run orchestrator + snapshot set) |
| A4 | Address/geosearch connector missing (`ConfirmScreen.tsx:209/295`, `PropertyLookup.tsx:302`) | missing connector | proposed **A** + existing M1 (Geoclient B-004) |
| A5 | No immutable capture store; in-memory TTL only (`resilience/cache.py`) | missing infra | proposed **A** (immutable capture) + blocker B-001 (storage) |
| A6 | Connectors on fixtures until keys (`HUMAN_ACTIONS_REQUIRED.md` §4/§7) | fixture-only | blockers B-004 (Geoclient), Socrata token |
| B1 | Rule extraction pending G6 (`rulesets/*.rule.json` limitations) | pending approval | existing M4 + G6 hold |
| C1 | Tax-lot geometry contract deferred; EPSG UNKNOWN (`property_profile.schema.json:61` OPEN-WITH-FLAG) | deferred contract | existing M2 geometry + proposed **C** |
| C2 | zoning-lot ≠ tax-lot documented limitation (`rules/integration.py:297`) | limitation | proposed **C** + M3-T004 closure (PR #93 lane) |
| C3 | geometry not in profile (`ConfirmScreen.tsx:217`) | not wired | proposed **C** |
| D1 | `r5_residential_far.rule.json:89` `special-district-far-modifier (not yet implemented)` | unimplemented modifier | proposed **E** + existing M4 |
| D2 | QRS FAR + per-DU 0.60 equivalent-FAR **not computed** (`r5_residential_far.rule.json:100`) | partial legal-math | proposed **E** + M4 |
| D3 | overlay/special-district/historic/large-site modifiers fail-closed (no canonical field) across `r5*_height`, `r5_setback` | unimplemented modifiers | proposed **C** (fields) + **E** (rules) + M3-T004 closure |
| D4 | R5A pitched-plane setback not reduced to a depth (`r5a_height.rule.json:57`) | uncomputed geometry | proposed **C/E** |
| E1 | scenario foundation only, no endpoint/optimizer (`scenario/__init__.py`) | foundation-only | existing M5-T001 + proposed **H** |
| E2 | only R5 family wired; others → unsupported stub (`scenario/builder.py:774`) | single-family | proposed **E/H** |
| F1 | professional-review workflow UI not available (`ProfessionalReviewPanel.tsx:5`) | deferred UI | proposed **F** |
| F2 | confirmation persistence not wired (`ConfirmScreen.tsx:344/364`) | not wired | proposed **B/F** |
| F3 | financial engine deferred (`property_profile.schema.json:340` Phase C) | deferred engine | proposed **H** (out of near-term launch) |
| G1 | `source_fact.schema.json` **OPEN** (no additionalProperties) — mandatory provenance record accepts extra keys | open contract | proposed **G** (HIGH) |
| G2 | `analysis_state_transition.schema.json` **OPEN** — audit record accepts unknown keys | open contract | proposed **G** |
| G3 | fixture-only schema fields (`scenario.schema.json:105`, `rule_evaluation.schema.json:148`) | fixture-only | keep; proposed **G** negative tests |
| G4 | district-code enums not modeled (`property_profile.schema.json:80` OPEN-WITH-FLAG) | deferred enum | existing M2 zoning-source + proposed **C/G** |
| H1 | internal rule-eval endpoint disabled-by-default (`config.py`, `rule-evaluation.ts:75`) | feature flag | existing M4; flag stays off until §5-E/F land |
| H2 | `supabase/migrations/.gitkeep` only — no RLS/tenancy/storage | missing infra | proposed **I** + blockers B-001/B-002 |
| H3 | D5 production-deploy workflow does not exist (`IMPLEMENTATION_STATUS.md:65`) | unbuilt | proposed **I** + B-012 deploy hold |
| H4 | worker + cron entrypoints REMOVED, "restoration owed" (`render.yaml:137-154`) | removed infra | proposed **B** (restore under real entrypoints) |
| I1 | 3D massing / premium UI / financial / opportunity-search unbuilt (DRAFT-for-review docs) | expansion | expansion hold (owner review) |
| J1 | truncated/bounded reports (`missing-inputs.ts`, `validate-profile.ts:40`) | documented limitation | continuing limitation (disclosed) |

**No item is dropped:** every row has a disposition. Items marked "continuing limitation" or "expansion hold" are explicit non-launch limitations, not silent omissions.

---

## 4. Defect matrix (severity · evidence · consequence · current safeguard · missing control · disposition)

| ID | Sev | Defect + evidence | Mechanical consequence | Current safeguard | Missing control | Proposed disposition |
|---|---|---|---|---|---|---|
| DF-1 | **P0** | **No auth/RLS/tenancy** anywhere; `supabase/migrations/.gitkeep` only; `main.py:6-11` "auth NOT enabled" | any deploy exposes all data cross-tenant | service documented INTERNAL/DEV-only; not deployed | JWT issuer/aud validation, org membership, RLS on every row/object/job/report, positive+negative cross-tenant tests | proposed **I**; blockers B-001/B-002; **B-012 deploy hold** (no public exposure) |
| DF-2 | **P0** | **Legal math on binary float**; `rules/operations.py:41/46/77` (`float(a)`, `round(v,10)`, `a/b`); no `Decimal` in `services/` | FAR/coverage/yard boundary at exact threshold subject to representation error (e.g. exact FAR equality) | 10-dp determinism rounding; fail-closed non-finite guards; geometry floats **isolated** (`evaluator.py:157` reads typed classes only) | Decimal/rational from canonical strings; per-rule rounding mode/scale/order; unit enforcement; adversarial threshold tests | proposed **D**; amend M4 evaluator (blocks M4 publication) |
| DF-3 | **P0** | **No run orchestrator / snapshot set / persistence**; synchronous per-request; `profile_revision` frozen `1` (`builder.py:669`); no DB | a partial multi-source analysis could be presented as complete; no reproducible run; no as_of coherence | single-source PLUTO path only; wave/spatial not wired (can't silently combine) | immutable run id + as_of_date + source_snapshot_set + typed stage states; coherent cache/LKG/breaker across restarts | proposed **A/B**; blocker B-001 (storage) |
| DF-4 | High | **`source_fact` contract OPEN** (`source_fact.schema.json`, no additionalProperties) — mandatory provenance record | undocumented/typo fields silently accepted into provenance | producer uses allowlist dict assembly (`profile/builder.py:297`) | `additionalProperties:false` (or single versioned `extensions`); negative typo/leak tests | proposed **G** |
| DF-5 | High | **`analysis_state_transition` contract OPEN** | audit records accept unknown keys | schema exists but no runtime writes it | close contract; allowlist serializer | proposed **G** (+ **B** when the state machine is built) |
| DF-6 | High | **Optional inputs inside exception predicates fail-OPEN** (`evaluator.py:196` raw two-valued `_eval_predicate`; optional missing only noted `:505-507`) | a missing optional input silently skips an exception that would DOWNGRADE coverage → fail-open miss of an escalation | required + applicability inputs DO use three-valued indeterminate path (`evaluator.py:511-518`) | route optional-input-missing inside an exception to indeterminate/PRR, never false | proposed **E**; amend M4 evaluator |
| DF-7 | High | **No report/export + no report invalidation**; no export module anywhere | changed sources/rules cannot supersede a report; no reproducible artifact | no report exists yet (nothing to mislead) | reports pin the full analysis manifest; supersede/invalidate on upstream change; injection-safe, tenant-scoped signed export | proposed **H** |
| DF-8 | Med | **Connectors not wired to production** (ZTLDB/geometry/zoning-features, crosscheck, spatial — §2 rows 6/7) | citywide analysis runs on PLUTO alone; zoning-lot/spatial facts absent | additive-only builder; route passes none (honest emptiness) | wire via the run orchestrator + snapshot set with reconciliation | proposed **A/B/C** |
| DF-9 | Med | **`semi_corner` risk / lot taxonomy** (directive 3B; `rules/integration.py:297`) | tax-lot area could be mislabeled zoning-lot area | zoning-lot≠tax-lot documented; PLUTO code never sets legal lot type | canonical zoning-lot entity from legal boundary + street lines; corner/interior/through/portions | proposed **C** + M3-T004 closure (PR #93) |
| DF-10 | Med | **`as_of_date` not supplied on any live path** (rule-eval endpoint omits it, `rule_evaluation.py:252`) | no explicit analysis date; law-effective vs vesting vs existing-condition dates not distinguished at runtime | rules engine supports as_of; fail-closed on invalid | thread explicit analysis date + the four date types through the run | proposed **B/E** |
| DF-11 | Low | confidence-as-legal-signal | (none — correctly separated) | `builder.py:283` "NEVER from confidence"; schema warnings | keep separated; add regression that confidence never feeds coverage | proposed **F** (regression only) |

---

## 5. Proposed packet areas (A–J) — ownership, mapping, dependencies

**No new task IDs are contracted here.** Each area maps to existing tasks/milestones where possible; genuinely new responsibilities are named as *proposed packets* for owner approval, then ID-assigned after reconciliation. One owner per source tree/schema/artifact; downstream imports read-only; no overlapping allowed paths; reuse existing resilience/storage/document-security primitives.

| Area | Scope (owner directive) | Maps to / proposed | Key deps |
|---|---|---|---|
| **A** Machine source registry + immutable capture + snapshot sets | machine-readable registry row per `SOURCE_ID`; CI rejects unregistered connector/endpoint; exact raw-byte capture, content-addressed/immutable/dedup/replayable; `source_snapshot_set` per analysis with skew rules; coherent-snapshot pagination | extend M1 registry (accepted) → machine-readable + CI gate (**proposed**); reuse M3-T002 immutable-capture primitives for connector data (**proposed**, cross-lane reuse) | B-001 storage; M1 (accepted) |
| **B** Analysis-run / job orchestrator | immutable run id, tenant, as_of_date, snapshot set, rule release, engine/config hashes; async/persistent/idempotent/resumable/cancellable; per-source budgets + whole-run deadline; typed stage states; partial-never-complete; coherent cache/LKG/breaker across restarts; restore worker + source-monitor entrypoints | **proposed** (new); `analysis_state*` contracts exist; restore `render.yaml:137-154` worker/cron under real entrypoints | A; B-001/B-002; DF-3 |
| **C** Canonical zoning-lot + physical-context model | distinct address/BBL/tax-lot/condo/building/zoning-lot entities; zoning lot may span tax lots (dated evidence); no MapPLUTO-area-as-zoning-area; frontage/lot-lines/street-lines/street-width class/block-face/legal portions; corner/interior/through/irregular/multi-frontage/remaining-portion; **no `semi_corner`** unless enacted source; missing topology blocks dependent rules | extend M2 geometry (M2-T009 accepted; M2-T014/15/16 survey **HELD**); **proposed** canonical zoning-lot entity; ties to M3-T004 closure (PR #93) | M2 geometry; M3-T004; DF-9 |
| **D** Exact legal math + units | Decimal/rational from canonical strings; per-rule rounding mode/scale/order; unit enforcement; canonical decimal serialization + formula/unit traces; geometry-float isolation with explicit conversions; adversarial threshold/rounding tests | **amend M4** `rules/operations.py`+`evaluator.py` (**proposed** rework); blocks M4 publication | M4 engine; DF-2 |
| **E** Rule applicability, precedence, closure, coverage | true/false/unknown predicates; missing/malformed never false/not_applicable; explicit analysis date + 4 date types; authority-tier ≠ precedence; machine-readable jurisdiction/status/effective-window/scope/amendment/supersession/project-instrument; closure over links/unlinked/defs/tables/footnotes/exceptions/modifiers; coverage certificate; no final value from one matched rule | **M4** rules + **M3-T004** closure (PR #93); fix DF-6 optional-in-exception fail-open; **proposed** coverage-certificate | M3-T004; M4; DF-6/DF-10 |
| **F** Provenance, human review, publication | deprecate generic confidence as legal signal (keep separated); track retrieval-fidelity/normalization/authority/freshness/conflict/review/coverage separately; full derivation graph; immutable user decisions; G6 verifies reviewer authorization+eligible evidence+closure+tests+rule-release hash; approved/suspended/superseded/rejected/revoked; upstream change invalidates downstream without deleting history | **proposed** review workflow + publication state machine (`analysis_state*` runtime); G6 (existing hold) | B (runtime); E; DF-11 |
| **G** Strict versioned contracts | close production objects `additionalProperties:false` or single versioned `extensions`; allowlist serializers; negative typo/undocumented-field/diagnostic-leak tests; schema migration + compat rules | **proposed** contract-hardening (close `source_fact`, `analysis_state_transition`; audit all) | DF-4/DF-5 |
| **H** Scenario, optimizer, 3D, reports | hard/soft constraints + objectives; infeasible/timeout/unsupported/approximate/optimal outcomes; pin solver/version/config/seed/discretization/tolerance/gap; no AI numbers into solver; 3D visualization-only; reports pin manifest + draft/partial/review state; supersede/invalidate; injection-safe tenant-scoped signed export | **M5** (foundation exists) → **proposed** optimizer + reports/export; 3D under **expansion hold** | E; **/dependency-security** for any solver; DF-7 |
| **I** Auth, tenancy, storage, ops | JWT iss/aud, org membership, tenant scope on every row/object/job/report; RLS pos+neg tests; backend-only service creds + CSRF policy; rate/quota/upload/decompression budgets; durable queue + DLQ + recovery; readiness≠liveness≠source-health; telemetry/alerting/migration/rollback/backup/PITR/retention/drills; **no public exposure before auth + P0 gates accepted** | **M0-T007/T008** (blocked B-001) + **proposed** RLS/tenancy/ops; **B-012 deploy hold** | B-001/B-002; DF-1 |
| **J** End-to-end expert golden corpus + launch gate | expert-reviewed cases across every borough/lot-type/condo/split-district/overlay/landmark/flood/street-width/vesting/source-mismatch/conflict/outage/stale-cache/restart/schema-drift/pagination/changed-during-read/rounding/unknown-applicability/override/supersession/tenant-isolation; replay/property-based/mutation/metamorphic/differential/failure-injection harnesses; CI deterministic+offline; live smoke separate, never silently updates goldens | **M6** golden-property library → **proposed** expert corpus + launch gate (G7) | all above; §6 |

---

## 6. Harness + expert-golden-corpus matrix

| Harness | Target area | Deterministic/offline? |
|---|---|---|
| Replay (raw-bytes → identical outputs) | A capture, run reproducibility | yes (frozen fixtures) |
| Property-based (invariants over generated inputs) | D math, E predicates | yes |
| Mutation (does the suite catch a seeded fault?) | D/E/G | yes |
| Metamorphic (relational invariants, e.g. scaling lot area scales FAR cap) | D/E/H | yes |
| Differential (native vs independent recompute) | D math, A snapshot skew | yes |
| Failure-injection (outage/stale/restart/drift/pagination/changed-during-read) | A/B resilience | yes (injected), + **separate scheduled live smoke** |
| Expert golden corpus (borough/lot/condo/overlay/… full list) | J launch gate | yes; live smoke separate and **never silently updates goldens** |

**Rule:** ordinary CI is deterministic + offline (frozen official fixtures); scheduled live-source smoke tests are a separate suite and may never silently update golden expectations.

---

## 7. Cross-milestone holds + enforcement proof

| Hold | Enforcement (machine or record) |
|---|---|
| M4-T007+ uncontracted until accepted M3-T004 closure **+** compatible-snapshot / canonical-zoning-lot / exact-legal-math / three-valued applicability+coverage prerequisites | no M4-T007 task file exists; master_plan records the M3-T004 dependency; §5 adds the further prerequisites (A/C/D/E) as gating |
| Existing M4 rules remain draft/awaiting G6 | ledger: M4-T001..T006 all `awaiting_gate`; G6 gate not recorded |
| M5-T001 remains scenario foundation only | ledger: M5-T001 `awaiting_gate`; `scenario/__init__.py` "service-layer only, no endpoint" |
| Construction-Code claims blocked until accepted M3-T005 | PR #93 M3-T005 `backlog` + B-011 (scope) + B-001 (storage) |
| Fixture-only evidence cannot make a production ingestion/document task accepted | S9 regression (control-plane CI) — B-001 blocks acceptance of M3-T002/T003/T005; proposed A/B ingestion tasks inherit the same B-001 gate |
| No "Verified/complete/buildable" unless every required domain evaluated from compatible snapshots under an approved rule release | `assert_not_verified` (`rules/integration.py:38`); coverage caps at `conditional`; profile `rule_coverage="not_computed"`; G6 human gate |
| Public deployment blocked | **B-012** (new, Part 1); `render.yaml` autoDeploy off; DF-1 |

---

## 8. Dependency & ownership rules (applied to all proposed areas)

- Exactly one owner per source tree/schema/artifact; downstream imports upstream artifacts read-only; **no overlapping allowed paths**.
- Reuse existing `app.resilience.*` (transport/cache/breaker/budget), the M3-T002 content-addressed storage interface, and the M3-T003 shared untrusted-document security surface.
- **No AI/RAG framework** for deterministic legal work.
- Any proposed production/cloud **OCR, paid API, solver, queue, or new parsing library** requires **`/dependency-security`** + a **stop-and-report owner decision** before selection or installation.
- Every eventual packet must carry exact outputs, dependencies, blockers, acceptance preconditions, G0–G5 scenarios, harness owner, and producer-report path (assigned at contracting, not here).

---

## 9. Unresolved owner decisions · paid-service questions · continuing limitations

**Owner decisions needed:**
1. Approve this replan's area breakdown (A–J) and the sequence, so IDs can be assigned (nothing contracted yet).
2. **B-013** — AGE-ONLY exception for `next@15.5.21` (Part 1, PR #94).
3. Sequencing: A/B (capture+orchestrator) and I (auth/RLS) are the P0 substrate; confirm they precede wiring the built-but-unwired connectors (DF-8) into production.
4. Whether DF-2 (Decimal legal math) is a blocking prerequisite to M4 rule *publication* (recommended: yes).

**Paid-service / credential questions (stop-and-report, none purchased):**
- B-001 Supabase (storage/RLS), B-002 Render (workers/deploy), B-004 Geoclient (address→BBL). All free-tier/official; no purchase proposed.
- Any future solver/queue/cloud-OCR → `/dependency-security` + owner decision first.

**Continuing (disclosed) non-launch limitations:**
- PLUTO-only production analysis; ZTLDB/geometry/spatial/rules/scenario not production-invoked (§2).
- No persistence, run orchestrator, report/export, or auth today.
- Bounded/truncated diagnostic reports (J1).
- 3D massing / premium UI / financial / opportunity-search under expansion hold.

---

## 10. Confirmation

Nothing was merged, moved, claimed, dispatched, implemented, accepted, deployed, purchased, installed, or closed. Ledger totals unchanged (42 accepted / 8 awaiting_gate / 9 backlog / 2 blocked / 1 claimed). This document is a proposal; contracting happens only after owner approval and ID reconciliation.
